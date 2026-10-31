"""Pruebas de la interfaz de consola."""

from __future__ import annotations

import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

from reservas.cli import main
from reservas.db import conectar
from reservas.inventario import cargar_inventario
from reservas.modelos import EstadoReserva, Reserva
from reservas.repositorio import obtener_reserva
from reservas.servicio import ServicioReservas


class PruebasCLI(unittest.TestCase):
    def setUp(self) -> None:
        self._directorio = tempfile.TemporaryDirectory()
        self.addCleanup(self._directorio.cleanup)
        self.ruta_bd = Path(self._directorio.name) / "reservas.db"
        self.raiz = Path(__file__).resolve().parents[1]

    def _ejecutar(self, entrada: str) -> tuple[int, str]:
        salida = io.StringIO()
        codigo = main(
            ["--db", str(self.ruta_bd)],
            entrada=io.StringIO(entrada),
            salida=salida,
        )
        return codigo, salida.getvalue()

    def _con_servicio(self, accion):
        conexion = conectar(self.ruta_bd)
        try:
            servicio = ServicioReservas(conexion, cargar_inventario())
            return accion(servicio)
        finally:
            conexion.close()

    def _crear(
        self,
        *,
        unidad_id: str = "MIC-01",
        solicitante: str = "Ada Lovelace",
        inicio: str = "2026-10-31 10:00",
        fin: str = "2026-10-31 11:00",
    ) -> Reserva:
        return self._con_servicio(
            lambda servicio: servicio.crear_reserva(
                unidad_id,
                solicitante,
                inicio,
                fin,
            )
        )

    def _reservas(self) -> list[Reserva]:
        return self._con_servicio(lambda servicio: servicio.listar_historial())

    def _obtener(self, reserva_id: str) -> Reserva | None:
        conexion = conectar(self.ruta_bd)
        try:
            return obtener_reserva(conexion, reserva_id)
        finally:
            conexion.close()

    def test_muestra_todas_las_opciones_del_menu(self) -> None:
        codigo, salida = self._ejecutar("0\n")

        self.assertEqual(codigo, 0)
        for opcion in (
            "1. Ver inventario.",
            "2. Consultar disponibilidad.",
            "3. Crear una reserva.",
            "4. Cancelar una reserva.",
            "5. Ver reservas activas.",
            "6. Ver historial completo.",
            "7. Reiniciar datos.",
            "0. Salir.",
        ):
            self.assertIn(opcion, salida)

    def test_muestra_inventario(self) -> None:
        codigo, salida = self._ejecutar("1\n0\n")

        self.assertEqual(codigo, 0)
        for unidad in cargar_inventario():
            self.assertIn(unidad.id, salida)
            self.assertIn(unidad.equipo, salida)

    def test_consulta_disponibilidad_libre_y_ocupada(self) -> None:
        self._crear(inicio="2026-10-31 10:00", fin="2026-10-31 11:00")

        codigo, salida = self._ejecutar(
            "2\nMIC-01\n2026-10-31 10:00\n2026-10-31 11:00\n"
            "2\nMIC-02\n2026-10-31 10:00\n2026-10-31 11:00\n"
            "0\n"
        )

        self.assertEqual(codigo, 0)
        self.assertIn("MIC-01 está ocupada", salida)
        self.assertIn("MIC-02 está disponible", salida)

    def test_crea_reserva_valida_y_muestra_uuid(self) -> None:
        codigo, salida = self._ejecutar(
            "3\nMIC-01\nAda Lovelace\n"
            "2026-10-31 10:00\n2026-10-31 11:00\n"
            "0\n"
        )

        self.assertEqual(codigo, 0)
        self.assertIn("Reserva creada correctamente.", salida)
        coincidencia = re.search(r"ID: ([0-9a-fA-F-]{36})", salida)
        self.assertIsNotNone(coincidencia)
        assert coincidencia is not None
        reserva_id = coincidencia.group(1)
        uuid.UUID(reserva_id)

        reserva = self._obtener(reserva_id)
        self.assertIsNotNone(reserva)
        assert reserva is not None
        self.assertEqual(reserva.unidad_id, "MIC-01")
        self.assertEqual(reserva.solicitante, "Ada Lovelace")
        self.assertEqual(reserva.estado, EstadoReserva.ACTIVA)

    def test_rechaza_superposicion(self) -> None:
        self._crear(inicio="2026-10-31 10:00", fin="2026-10-31 11:00")

        codigo, salida = self._ejecutar(
            "3\nMIC-01\nGrace Hopper\n"
            "2026-10-31 10:30\n2026-10-31 11:30\n"
            "0\n"
        )

        self.assertEqual(codigo, 0)
        self.assertIn("Error:", salida)
        self.assertIn("superpone", salida)
        self.assertEqual(len(self._reservas()), 1)

    def test_cancela_reserva_y_libera_horario(self) -> None:
        reserva = self._crear()

        codigo, salida = self._ejecutar(
            f"4\n{reserva.id}\n"
            "2\nMIC-01\n2026-10-31 10:30\n2026-10-31 11:30\n"
            "0\n"
        )

        self.assertEqual(codigo, 0)
        self.assertIn("Reserva cancelada. El horario quedó libre.", salida)
        self.assertIn("MIC-01 está disponible", salida)

        actualizada = self._obtener(reserva.id)
        self.assertIsNotNone(actualizada)
        assert actualizada is not None
        self.assertEqual(actualizada.estado, EstadoReserva.CANCELADA)
        self.assertEqual(actualizada.unidad_id, reserva.unidad_id)
        self.assertEqual(actualizada.solicitante, reserva.solicitante)
        self.assertEqual(actualizada.inicio, reserva.inicio)
        self.assertEqual(actualizada.fin, reserva.fin)

    def test_muestra_reservas_activas(self) -> None:
        activa = self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        cancelada = self._crear(
            inicio="2026-10-31 11:00",
            fin="2026-10-31 12:00",
        )
        self._con_servicio(lambda servicio: servicio.cancelar_reserva(cancelada.id))

        codigo, salida = self._ejecutar("5\n0\n")

        self.assertEqual(codigo, 0)
        self.assertIn(activa.id, salida)
        self.assertNotIn(cancelada.id, salida)

    def test_muestra_historial_completo(self) -> None:
        activa = self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        cancelada = self._crear(
            inicio="2026-10-31 11:00",
            fin="2026-10-31 12:00",
        )
        self._con_servicio(lambda servicio: servicio.cancelar_reserva(cancelada.id))

        codigo, salida = self._ejecutar("6\n0\n")

        self.assertEqual(codigo, 0)
        for reserva in (activa, cancelada):
            self.assertIn(reserva.id, salida)
            self.assertIn(reserva.unidad_id, salida)
            self.assertIn(reserva.solicitante, salida)
        self.assertIn("Estado: activa", salida)
        self.assertIn("Estado: cancelada", salida)

    def test_opciones_invalidas_no_cierran_el_programa(self) -> None:
        codigo, salida = self._ejecutar("99\nabc\n0\n")

        self.assertEqual(codigo, 0)
        self.assertEqual(salida.count("Opción inválida"), 2)
        self.assertIn("Hasta luego.", salida)

    def test_entrada_invalida_no_cierra_el_programa(self) -> None:
        codigo, salida = self._ejecutar(
            "3\nNO-EXISTE\nAda Lovelace\n"
            "2026-10-31 10:00\n2026-10-31 11:00\n"
            "3\nMIC-01\nAda Lovelace\n"
            "2026-1-1 10:00\n2026-10-31 11:00\n"
            "0\n"
        )

        self.assertEqual(codigo, 0)
        self.assertIn("no existe", salida)
        self.assertIn("Formato inválido", salida)
        self.assertEqual(self._reservas(), [])

    def test_reinicio_rechazado_no_modifica_datos(self) -> None:
        self._crear()

        for confirmacion in ("NO", "reiniciar", " REINICIAR "):
            with self.subTest(confirmacion=confirmacion):
                codigo, salida = self._ejecutar(f"7\n{confirmacion}\n0\n")

                self.assertEqual(codigo, 0)
                self.assertIn("Reinicio cancelado", salida)
                self.assertEqual(len(self._reservas()), 1)

    def test_reinicio_confirmado_elimina_reservas_y_conserva_inventario(self) -> None:
        self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        cancelada = self._crear(
            inicio="2026-10-31 11:00",
            fin="2026-10-31 12:00",
        )
        self._con_servicio(lambda servicio: servicio.cancelar_reserva(cancelada.id))

        codigo, salida = self._ejecutar("7\nREINICIAR\n0\n")

        self.assertEqual(codigo, 0)
        self.assertIn("Datos reiniciados", salida)
        self.assertEqual(self._reservas(), [])
        self.assertEqual(len(cargar_inventario()), 5)

        nueva = self._crear(
            inicio="2026-10-31 12:00",
            fin="2026-10-31 13:00",
        )
        self.assertEqual(nueva.estado, EstadoReserva.ACTIVA)

    def test_persistencia_entre_ejecuciones_independientes(self) -> None:
        codigo_creacion, salida_creacion = self._ejecutar(
            "3\nMIC-01\nGrace Hopper\n"
            "2026-10-31 10:00\n2026-10-31 11:00\n"
            "0\n"
        )
        self.assertEqual(codigo_creacion, 0)
        self.assertIn("Reserva creada correctamente.", salida_creacion)

        codigo_historial, salida_historial = self._ejecutar("6\n0\n")

        self.assertEqual(codigo_historial, 0)
        self.assertIn("Grace Hopper", salida_historial)
        self.assertIn("MIC-01", salida_historial)
        self.assertIn("Estado: activa", salida_historial)

    def test_ejecucion_con_python_m_reservas(self) -> None:
        entorno = os.environ.copy()
        entorno["PYTHONIOENCODING"] = "utf-8"
        resultado = subprocess.run(
            [
                sys.executable,
                "-m",
                "reservas",
                "--db",
                str(self.ruta_bd),
            ],
            input="1\n0\n",
            text=True,
            capture_output=True,
            cwd=str(self.raiz),
            env=entorno,
            encoding="utf-8",
            timeout=30,
        )

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("MIC-01", resultado.stdout)
        self.assertIn("Hasta luego.", resultado.stdout)

    def test_entrada_finalizada_no_cierra_inesperadamente(self) -> None:
        codigo, salida = self._ejecutar("")

        self.assertEqual(codigo, 0)
        self.assertIn("Entrada finalizada", salida)


if __name__ == "__main__":
    unittest.main()
