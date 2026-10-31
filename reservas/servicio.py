"""Capa de servicio con las operaciones de negocio de reservas.

Las fechas de entrada se reciben como texto estricto ``AAAA-MM-DD HH:MM`` y
se validan con ``reservas.tiempo``. La existencia de la unidad se valida con
el inventario precargado y los conflictos se delegan en
``reservas.repositorio.hay_conflicto`` para no duplicar la regla.

Comportamiento de cancelación
-----------------------------
- ID inexistente: se lanza ``ReservaNoEncontrada`` y no se modifica la base.
- Reserva ya cancelada: se devuelve ``ResultadoCancelacion`` con
  ``cancelada_ahora=False`` y la reserva sin cambios.
- Reserva activa: se actualizan únicamente ``estado`` y ``cancelada_en``;
  se conservan ID, unidad, solicitante, inicio y fin.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass

from .inventario import Inventario, cargar_inventario
from .modelos import EstadoReserva, Reserva
from .repositorio import (
    hay_conflicto,
    insertar_si_libre,
    listar_reservas,
    marcar_cancelada,
    obtener_reserva,
)
from .tiempo import ahora_local, parsear_fecha_hora


class ErrorServicio(ValueError):
    """Error de negocio del servicio de reservas."""


class UnidadInexistente(ErrorServicio):
    """La unidad no pertenece al inventario precargado."""


class SolicitanteInvalido(ErrorServicio):
    """El solicitante está vacío o compuesto únicamente por espacios."""


class ConflictoReserva(ErrorServicio):
    """Ya existe una reserva activa superpuesta para la misma unidad."""


class ReservaNoEncontrada(ErrorServicio):
    """No existe una reserva con el identificador indicado."""


@dataclass(frozen=True, slots=True)
class ResultadoCancelacion:
    """Resultado de cancelar una reserva.

    ``cancelada_ahora`` es ``False`` cuando la reserva ya estaba cancelada;
    en ese caso no se modifica ningún dato.
    """

    reserva: Reserva
    cancelada_ahora: bool


class ServicioReservas:
    """Operaciones de negocio sobre reservas, inventario y persistencia."""

    def __init__(
        self,
        conexion: sqlite3.Connection,
        inventario: Inventario | None = None,
    ) -> None:
        self._conexion = conexion
        self._inventario = inventario if inventario is not None else cargar_inventario()

    def consultar_disponibilidad(
        self,
        unidad_id: str,
        inicio: str,
        fin: str,
    ) -> bool:
        """Devuelve ``True`` si la unidad está libre en ``[inicio, fin)``.

        Lanza ``UnidadInexistente`` si la unidad no existe, y los errores de
        ``reservas.tiempo`` si el formato o el intervalo son inválidos.
        """
        self._validar_unidad(unidad_id)
        inicio_dt = parsear_fecha_hora(inicio)
        fin_dt = parsear_fecha_hora(fin)
        return not hay_conflicto(self._conexion, unidad_id, inicio_dt, fin_dt)

    def crear_reserva(
        self,
        unidad_id: str,
        solicitante: str,
        inicio: str,
        fin: str,
    ) -> Reserva:
        """Crea una reserva activa si la unidad está libre.

        Lanza ``UnidadInexistente``, ``SolicitanteInvalido``,
        ``ErrorFormatoTiempo``, ``ErrorIntervalo`` o ``ConflictoReserva``.
        Ninguna validación fallida modifica la base de datos.
        """
        self._validar_unidad(unidad_id)
        self._validar_solicitante(solicitante)
        inicio_dt = parsear_fecha_hora(inicio)
        fin_dt = parsear_fecha_hora(fin)

        reserva = Reserva(
            id=str(uuid.uuid4()),
            unidad_id=unidad_id,
            solicitante=solicitante,
            inicio=inicio_dt,
            fin=fin_dt,
            estado=EstadoReserva.ACTIVA,
            creada_en=ahora_local(),
            cancelada_en=None,
        )
        if not insertar_si_libre(self._conexion, reserva):
            raise ConflictoReserva(
                f"La unidad {unidad_id!r} ya tiene una reserva activa "
                f"que se superpone con {inicio!r}–{fin!r}."
            )
        return reserva

    def cancelar_reserva(self, reserva_id: str) -> ResultadoCancelacion:
        """Cancela una reserva activa sin borrar ni alterar sus demás campos.

        Si el ID no existe lanza ``ReservaNoEncontrada``. Si la reserva ya
        estaba cancelada devuelve ``cancelada_ahora=False`` sin cambios.
        Si la conexión ya tiene una transacción abierta, participa de ella y
        deja el commit o rollback al llamador.
        """
        if self._conexion.in_transaction:
            return self._cancelar_en_transaccion(reserva_id)

        self._conexion.execute("BEGIN IMMEDIATE")
        try:
            resultado = self._cancelar_en_transaccion(reserva_id)
            self._conexion.commit()
            return resultado
        except Exception:
            self._conexion.rollback()
            raise

    def listar_historial(
        self,
        estado: EstadoReserva | None = None,
    ) -> list[Reserva]:
        """Lista reservas activas y canceladas, opcionalmente por estado."""
        return listar_reservas(self._conexion, estado=estado)

    def _validar_unidad(self, unidad_id: str) -> None:
        if not self._inventario.contiene(unidad_id):
            raise UnidadInexistente(
                f"La unidad {unidad_id!r} no existe en el inventario."
            )

    def _validar_solicitante(self, solicitante: str) -> None:
        if not isinstance(solicitante, str) or not solicitante.strip():
            raise SolicitanteInvalido(
                "El solicitante no puede estar vacío ni compuesto solo por espacios."
            )

    def _cancelar_en_transaccion(
        self,
        reserva_id: str,
    ) -> ResultadoCancelacion:
        reserva = obtener_reserva(self._conexion, reserva_id)
        if reserva is None:
            raise ReservaNoEncontrada(
                f"No existe una reserva con ID {reserva_id!r}."
            )
        if not reserva.activa:
            return ResultadoCancelacion(reserva=reserva, cancelada_ahora=False)

        cancelada_en = ahora_local()
        actualizada = marcar_cancelada(self._conexion, reserva.id, cancelada_en)
        if not actualizada:
            actual = obtener_reserva(self._conexion, reserva.id)
            if actual is None:
                raise ReservaNoEncontrada(
                    f"No existe una reserva con ID {reserva.id!r}."
                )
            if actual.activa:
                raise ErrorServicio("No se pudo cancelar la reserva.")
            return ResultadoCancelacion(reserva=actual, cancelada_ahora=False)

        cancelada = obtener_reserva(self._conexion, reserva.id)
        if cancelada is None:
            raise ReservaNoEncontrada(
                f"No existe una reserva con ID {reserva.id!r}."
            )
        return ResultadoCancelacion(reserva=cancelada, cancelada_ahora=True)
