"""Persistencia y consultas de reservas en SQLite.

Las fechas de inicio y fin se guardan en el formato estricto
``AAAA-MM-DD HH:MM`` para que la comparación lexicográfica coincida con la
cronológica. Las fechas de auditoría se guardan con precisión de microsegundos.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from .modelos import EstadoReserva, Reserva
from .tiempo import formatear_fecha_hora, parsear_fecha_hora, validar_intervalo


class ErrorRepositorio(ValueError):
    """No se pudo guardar o recuperar una reserva."""


def hay_conflicto(
    conexion: sqlite3.Connection,
    unidad_id: str,
    inicio: datetime,
    fin: datetime,
) -> bool:
    """Indica si existe una reserva activa superpuesta en la misma unidad.

    Usa intervalos semiabiertos ``[inicio, fin)``: los límites iguales no
    conflictúan. Las reservas canceladas se ignoran.
    """
    if not isinstance(unidad_id, str) or not unidad_id.strip():
        raise ValueError("El identificador de la unidad no puede estar vacío.")
    validar_intervalo(inicio, fin)

    fila = conexion.execute(
        """
        SELECT 1
        FROM reservas
        WHERE unidad_id = ?
          AND estado = ?
          AND inicio < ?
          AND fin > ?
        LIMIT 1
        """,
        (
            unidad_id,
            EstadoReserva.ACTIVA.value,
            formatear_fecha_hora(fin),
            formatear_fecha_hora(inicio),
        ),
    ).fetchone()
    return fila is not None


def insertar_reserva(conexion: sqlite3.Connection, reserva: Reserva) -> None:
    """Inserta una reserva sin verificar conflictos.

    La conexión debe haber sido creada con ``reservas.db.conectar``. Si está en
    modo autocommit, la inserción se confirma al ejecutarse; si el llamador
    abrió una transacción, el commit queda a su cargo.
    """
    if not isinstance(reserva, Reserva):
        raise TypeError("Se esperaba una instancia de Reserva.")

    try:
        conexion.execute(
            """
            INSERT INTO reservas (
                id, unidad_id, solicitante, inicio, fin,
                estado, creada_en, cancelada_en
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reserva.id,
                reserva.unidad_id,
                reserva.solicitante,
                formatear_fecha_hora(reserva.inicio),
                formatear_fecha_hora(reserva.fin),
                reserva.estado.value,
                _formatear_auditoria(reserva.creada_en),
                _formatear_auditoria(reserva.cancelada_en)
                if reserva.cancelada_en is not None
                else None,
            ),
        )
    except sqlite3.IntegrityError as exc:
        raise ErrorRepositorio(
            f"No se pudo insertar la reserva {reserva.id!r}: {exc}"
        ) from exc


def marcar_cancelada(
    conexion: sqlite3.Connection,
    reserva_id: str,
    cancelada_en: datetime,
) -> bool:
    """Marca una reserva activa como cancelada sin borrar ni alterar otros campos.

    Devuelve ``True`` si actualizó una fila y ``False`` si no encontró una
    reserva activa con ese ID. No hace commit: el llamador controla la
    transacción.
    """
    if not isinstance(cancelada_en, datetime):
        raise TypeError("La fecha de cancelación debe ser un datetime.")

    cursor = conexion.execute(
        """
        UPDATE reservas
        SET estado = ?, cancelada_en = ?
        WHERE id = ? AND estado = ?
        """,
        (
            EstadoReserva.CANCELADA.value,
            _formatear_auditoria(cancelada_en),
            reserva_id,
            EstadoReserva.ACTIVA.value,
        ),
    )
    return cursor.rowcount == 1


def obtener_reserva(
    conexion: sqlite3.Connection,
    reserva_id: str,
) -> Reserva | None:
    """Recupera una reserva por ID o devuelve ``None`` si no existe."""
    fila = conexion.execute(
        """
        SELECT id, unidad_id, solicitante, inicio, fin,
               estado, creada_en, cancelada_en
        FROM reservas
        WHERE id = ?
        """,
        (reserva_id,),
    ).fetchone()
    return _fila_a_reserva(fila) if fila is not None else None


def listar_reservas(
    conexion: sqlite3.Connection,
    *,
    estado: EstadoReserva | None = None,
    unidad_id: str | None = None,
) -> list[Reserva]:
    """Lista reservas, opcionalmente filtradas por estado y unidad.

    El orden es cronológico por inicio y, ante empate, por ID.
    """
    condiciones: list[str] = []
    parametros: list[object] = []

    if estado is not None:
        if not isinstance(estado, EstadoReserva):
            raise ValueError("El estado debe ser una instancia de EstadoReserva.")
        condiciones.append("estado = ?")
        parametros.append(estado.value)

    if unidad_id is not None:
        condiciones.append("unidad_id = ?")
        parametros.append(unidad_id)

    consulta = (
        "SELECT id, unidad_id, solicitante, inicio, fin, "
        "estado, creada_en, cancelada_en FROM reservas"
    )
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)
    consulta += " ORDER BY inicio, id"

    filas = conexion.execute(consulta, parametros).fetchall()
    return [_fila_a_reserva(fila) for fila in filas]


def insertar_si_libre(
    conexion: sqlite3.Connection,
    reserva: Reserva,
) -> bool:
    """Inserta la reserva solo si no hay conflicto, de forma atómica.

    Si la conexión no tiene una transacción abierta, usa ``BEGIN IMMEDIATE``
    para bloquear escritores, comprobar el conflicto e insertar. Devuelve
    ``True`` si insertó y ``False`` si había conflicto. Si ya hay una
    transacción abierta, participa de ella y deja el commit al llamador.
    """
    if not isinstance(reserva, Reserva):
        raise TypeError("Se esperaba una instancia de Reserva.")

    if conexion.in_transaction:
        return _insertar_si_libre_en_transaccion(conexion, reserva)

    conexion.execute("BEGIN IMMEDIATE")
    try:
        insertado = _insertar_si_libre_en_transaccion(conexion, reserva)
        conexion.commit()
        return insertado
    except Exception:
        conexion.rollback()
        raise


def _insertar_si_libre_en_transaccion(
    conexion: sqlite3.Connection,
    reserva: Reserva,
) -> bool:
    if hay_conflicto(conexion, reserva.unidad_id, reserva.inicio, reserva.fin):
        return False
    insertar_reserva(conexion, reserva)
    return True


def _formatear_auditoria(momento: datetime) -> str:
    if momento.tzinfo is not None:
        raise ErrorRepositorio("Las fechas de auditoría deben ser naive.")
    return momento.isoformat(sep=" ", timespec="microseconds")


def _parsear_auditoria(texto: str) -> datetime:
    try:
        return datetime.fromisoformat(texto)
    except ValueError as exc:
        raise ErrorRepositorio(
            f"Fecha de auditoría inválida en la base: {texto!r}."
        ) from exc


def _fila_a_reserva(fila: sqlite3.Row) -> Reserva:
    cancelada_en = fila["cancelada_en"]
    return Reserva(
        id=fila["id"],
        unidad_id=fila["unidad_id"],
        solicitante=fila["solicitante"],
        inicio=parsear_fecha_hora(fila["inicio"]),
        fin=parsear_fecha_hora(fila["fin"]),
        estado=EstadoReserva(fila["estado"]),
        creada_en=_parsear_auditoria(fila["creada_en"]),
        cancelada_en=(
            _parsear_auditoria(cancelada_en)
            if cancelada_en is not None
            else None
        ),
    )
