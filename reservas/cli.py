"""Interfaz de consola interactiva del sistema de reservas.

La aplicación usa ``ServicioReservas`` para toda la lógica de negocio y
``cargar_inventario`` para mostrar las unidades. La base SQLite se abre con
``reservas.db.conectar`` y, por defecto, se guarda en ``data/reservas.db``.

Para pruebas o usos alternativos se puede indicar otra base con ``--db``.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from .db import RUTA_BD_POR_DEFECTO, conectar
from .inventario import ErrorInventario, Inventario, cargar_inventario
from .modelos import EstadoReserva, Reserva
from .servicio import ServicioReservas
from .tiempo import formatear_fecha_hora


_MENU = (
    "1. Ver inventario.",
    "2. Consultar disponibilidad.",
    "3. Crear una reserva.",
    "4. Cancelar una reserva.",
    "5. Ver reservas activas.",
    "6. Ver historial completo.",
    "7. Reiniciar datos.",
    "0. Salir.",
)


class AplicacionConsola:
    """Menú interactivo sobre una instancia de ``ServicioReservas``."""

    def __init__(
        self,
        servicio: ServicioReservas,
        inventario: Inventario,
        conexion: sqlite3.Connection,
        entrada: TextIO,
        salida: TextIO,
    ) -> None:
        self._servicio = servicio
        self._inventario = inventario
        self._conexion = conexion
        self._entrada = entrada
        self._salida = salida

    def ejecutar(self) -> None:
        """Ejecuta el menú hasta que el usuario elige salir o termina la entrada."""
        self._imprimir("Sistema de reservas de laboratorio")

        while True:
            self._mostrar_menu()
            opcion = self._leer("Seleccione una opción: ")
            if opcion is None:
                self._imprimir("Entrada finalizada. Saliendo.")
                return

            opcion = opcion.strip()
            if opcion == "0":
                self._imprimir("Hasta luego.")
                return

            acciones = {
                "1": self._ver_inventario,
                "2": self._consultar_disponibilidad,
                "3": self._crear_reserva,
                "4": self._cancelar_reserva,
                "5": self._ver_reservas_activas,
                "6": self._ver_historial_completo,
                "7": self._reiniciar_datos,
            }
            accion = acciones.get(opcion)
            if accion is None:
                self._imprimir("Opción inválida. Ingrese un número del 0 al 7.")
                continue
            accion()

    def _mostrar_menu(self) -> None:
        self._imprimir()
        for linea in _MENU:
            self._imprimir(linea)

    def _imprimir(self, texto: str = "") -> None:
        print(texto, file=self._salida)

    def _leer(self, mensaje: str) -> str | None:
        self._salida.write(mensaje)
        self._salida.flush()
        linea = self._entrada.readline()
        if linea == "":
            return None
        return linea.rstrip("\r\n")

    def _ver_inventario(self) -> None:
        self._imprimir("Inventario:")
        for unidad in self._inventario:
            self._imprimir(f"  {unidad.id}  {unidad.equipo}")

    def _consultar_disponibilidad(self) -> None:
        unidad_id = self._leer("ID de unidad: ")
        if unidad_id is None:
            return
        inicio = self._leer("Inicio (AAAA-MM-DD HH:MM): ")
        if inicio is None:
            return
        fin = self._leer("Fin (AAAA-MM-DD HH:MM): ")
        if fin is None:
            return

        try:
            disponible = self._servicio.consultar_disponibilidad(
                unidad_id,
                inicio,
                fin,
            )
        except (ValueError, sqlite3.Error) as exc:
            self._imprimir(f"Error: {exc}")
            return

        if disponible:
            self._imprimir(
                f"La unidad {unidad_id} está disponible de {inicio} a {fin}."
            )
        else:
            self._imprimir(f"La unidad {unidad_id} está ocupada de {inicio} a {fin}.")

    def _crear_reserva(self) -> None:
        unidad_id = self._leer("ID de unidad: ")
        if unidad_id is None:
            return
        solicitante = self._leer("Nombre ficticio del solicitante: ")
        if solicitante is None:
            return
        inicio = self._leer("Inicio (AAAA-MM-DD HH:MM): ")
        if inicio is None:
            return
        fin = self._leer("Fin (AAAA-MM-DD HH:MM): ")
        if fin is None:
            return

        try:
            reserva = self._servicio.crear_reserva(
                unidad_id,
                solicitante,
                inicio,
                fin,
            )
        except (ValueError, sqlite3.Error) as exc:
            self._imprimir(f"Error: {exc}")
            return

        self._imprimir("Reserva creada correctamente.")
        self._mostrar_reserva(reserva)

    def _cancelar_reserva(self) -> None:
        reserva_id = self._leer("ID de la reserva: ")
        if reserva_id is None:
            return

        try:
            resultado = self._servicio.cancelar_reserva(reserva_id)
        except (ValueError, sqlite3.Error) as exc:
            self._imprimir(f"Error: {exc}")
            return

        if resultado.cancelada_ahora:
            self._imprimir("Reserva cancelada. El horario quedó libre.")
        else:
            self._imprimir(
                "La reserva ya estaba cancelada; no se modificaron los datos."
            )
        self._mostrar_reserva(resultado.reserva)

    def _ver_reservas_activas(self) -> None:
        try:
            reservas = self._servicio.listar_historial(EstadoReserva.ACTIVA)
        except (ValueError, sqlite3.Error) as exc:
            self._imprimir(f"Error: {exc}")
            return
        self._mostrar_reservas(reservas, "No hay reservas activas.")

    def _ver_historial_completo(self) -> None:
        try:
            reservas = self._servicio.listar_historial()
        except (ValueError, sqlite3.Error) as exc:
            self._imprimir(f"Error: {exc}")
            return
        self._mostrar_reservas(reservas, "No hay reservas registradas.")

    def _reiniciar_datos(self) -> None:
        self._imprimir()
        self._imprimir(
            "ADVERTENCIA: se eliminarán TODAS las reservas activas y canceladas, "
            "incluido el historial."
        )
        self._imprimir("El inventario no se modifica.")
        confirmacion = self._leer("Escriba exactamente REINICIAR para confirmar: ")
        if confirmacion is None:
            return
        if confirmacion != "REINICIAR":
            self._imprimir("Reinicio cancelado. No se modificaron los datos.")
            return

        try:
            self._reiniciar_base()
        except (ValueError, sqlite3.Error) as exc:
            self._imprimir(f"Error al reiniciar: {exc}")
            return

        self._imprimir(
            "Datos reiniciados. Se eliminaron todas las reservas; "
            "el inventario se conserva."
        )

    def _reiniciar_base(self) -> None:
        if self._conexion.in_transaction:
            self._conexion.execute("DELETE FROM reservas")
            return

        self._conexion.execute("BEGIN IMMEDIATE")
        try:
            self._conexion.execute("DELETE FROM reservas")
            self._conexion.commit()
        except Exception:
            self._conexion.rollback()
            raise

    def _mostrar_reserva(self, reserva: Reserva) -> None:
        self._imprimir(f"ID: {reserva.id}")
        self._imprimir(f"Unidad: {reserva.unidad_id}")
        self._imprimir(f"Solicitante: {reserva.solicitante}")
        self._imprimir(f"Inicio: {formatear_fecha_hora(reserva.inicio)}")
        self._imprimir(f"Fin: {formatear_fecha_hora(reserva.fin)}")
        self._imprimir(f"Estado: {reserva.estado.value}")
        if reserva.cancelada_en is not None:
            self._imprimir(
                "Cancelada en: "
                + reserva.cancelada_en.strftime("%Y-%m-%d %H:%M:%S")
            )

    def _mostrar_reservas(
        self,
        reservas: list[Reserva],
        mensaje_vacio: str,
    ) -> None:
        if not reservas:
            self._imprimir(mensaje_vacio)
            return
        for indice, reserva in enumerate(reservas, start=1):
            self._imprimir(f"Reserva {indice}:")
            self._mostrar_reserva(reserva)
            if indice != len(reservas):
                self._imprimir()


def main(
    argv: Sequence[str] | None = None,
    *,
    entrada: TextIO | None = None,
    salida: TextIO | None = None,
) -> int:
    """Punto de entrada de la aplicación de consola.

    ``entrada`` y ``salida`` permiten inyectar flujos en las pruebas. El
    parámetro ``--db`` permite usar una base temporal sin tocar la real.
    """
    parser = argparse.ArgumentParser(
        prog="reservas",
        description="Sistema local de reservas de laboratorio.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=RUTA_BD_POR_DEFECTO,
        help="Ruta de la base SQLite (por defecto: data/reservas.db).",
    )
    argumentos = parser.parse_args(argv)

    entrada = entrada if entrada is not None else sys.stdin
    salida = salida if salida is not None else sys.stdout

    try:
        inventario = cargar_inventario()
    except ErrorInventario as exc:
        print(f"No se pudo cargar el inventario: {exc}", file=salida)
        return 1

    try:
        conexion = conectar(argumentos.db)
    except (OSError, sqlite3.Error) as exc:
        print(f"No se pudo abrir la base de datos: {exc}", file=salida)
        return 1

    try:
        servicio = ServicioReservas(conexion, inventario)
        aplicacion = AplicacionConsola(
            servicio,
            inventario,
            conexion,
            entrada,
            salida,
        )
        aplicacion.ejecutar()
    finally:
        conexion.close()

    return 0
