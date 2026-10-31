"""Pruebas de la capa de servicio de reservas."""

from __future__ import annotations

import tempfile
import unittest
import uuid
from datetime import datetime
from pathlib import Path

from reservas.db import conectar
from reservas.inventario import cargar_inventario
from reservas.modelos import EstadoReserva, Reserva
from reservas.repositorio import obtener_reserva
from reservas.servicio import (
    ConflictoReserva,
    ReservaNoEncontrada,
    ResultadoCancelacion,
    ServicioReservas,
    SolicitanteInvalido,
    UnidadInexistente,
)
from reservas.tiempo import ErrorFormatoTiempo, ErrorIntervalo


class PruebasServicio(unittest.TestCase):
    def setUp(self) -> None:
        self._directorio = tempfile.TemporaryDirectory()
        self.addCleanup(self._directorio.cleanup)
        self.ruta_bd = Path(self._directorio.name) / "reservas.db"
        self.conexion = conectar(self.ruta_bd)
        self.addCleanup(self._cerrar_conexion)
        self.servicio = ServicioReservas(self.conexion, cargar_inventario())

    def _cerrar_conexion(self) -> None:
        if self.conexion is not None:
            self.conexion.close()
            self.conexion = None

    def _crear(
        self,
        *,
        unidad_id: str = "MIC-01",
        solicitante: str = "Ada Lovelace",
        inicio: str = "2026-10-31 10:00",
        fin: str = "2026-10-31 11:00",
    ) -> Reserva:
        return self.servicio.crear_reserva(unidad_id, solicitante, inicio, fin)

    def _historial(self) -> list[Reserva]:
        return self.servicio.listar_historial()

    def test_crea_reserva_valida_con_uuid_y_estado_activo(self) -> None:
        reserva = self._crear(solicitante="  Ada Lovelace  ")

        self.assertIsInstance(reserva, Reserva)
        self.assertEqual(reserva.unidad_id, "MIC-01")
        self.assertEqual(reserva.solicitante, "Ada Lovelace")
        self.assertEqual(reserva.inicio, datetime(2026, 10, 31, 10, 0))
        self.assertEqual(reserva.fin, datetime(2026, 10, 31, 11, 0))
        self.assertEqual(reserva.estado, EstadoReserva.ACTIVA)
        self.assertIsNone(reserva.cancelada_en)
        self.assertIsNotNone(reserva.creada_en)
        uuid.UUID(reserva.id)

        persistida = obtener_reserva(self.conexion, reserva.id)
        self.assertEqual(persistida, reserva)

    def test_genera_identificadores_unicos(self) -> None:
        primera = self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        segunda = self._crear(
            inicio="2026-10-31 11:00",
            fin="2026-10-31 12:00",
        )

        self.assertNotEqual(primera.id, segunda.id)
        self.assertEqual(len({primera.id, segunda.id}), 2)

    def test_rechaza_unidad_inexistente(self) -> None:
        with self.assertRaises(UnidadInexistente):
            self._crear(unidad_id="NO-EXISTE")

        self.assertEqual(self._historial(), [])

    def test_rechaza_solicitante_vacio_o_solo_espacios(self) -> None:
        for solicitante in ("", "   ", "\t\n "):
            with self.subTest(solicitante=solicitante):
                with self.assertRaises(SolicitanteInvalido):
                    self._crear(solicitante=solicitante)

        self.assertEqual(self._historial(), [])

    def test_rechaza_fechas_invalidas(self) -> None:
        casos = (
            ("2026-1-1 10:00", "2026-10-31 11:00"),
            ("2026-10-31 10:00", "2026-02-30 11:00"),
            ("2026-10-31", "2026-10-31 11:00"),
            ("2026-10-31 10:00", "2026-10-31 11:00:00"),
        )

        for inicio, fin in casos:
            with self.subTest(inicio=inicio, fin=fin):
                with self.assertRaises(ErrorFormatoTiempo):
                    self._crear(inicio=inicio, fin=fin)

        self.assertEqual(self._historial(), [])

    def test_rechaza_inicio_igual_o_posterior_al_fin(self) -> None:
        casos = (
            ("2026-10-31 10:00", "2026-10-31 10:00"),
            ("2026-10-31 11:00", "2026-10-31 10:00"),
        )

        for inicio, fin in casos:
            with self.subTest(inicio=inicio, fin=fin):
                with self.assertRaises(ErrorIntervalo):
                    self._crear(inicio=inicio, fin=fin)

        self.assertEqual(self._historial(), [])

    def test_rechaza_superposicion_sin_modificar_la_base(self) -> None:
        self._crear(inicio="2026-10-31 10:00", fin="2026-10-31 11:00")

        with self.assertRaises(ConflictoReserva):
            self._crear(inicio="2026-10-31 10:30", fin="2026-10-31 11:30")

        self.assertEqual(len(self._historial()), 1)

    def test_acepta_horarios_consecutivos(self) -> None:
        primera = self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        segunda = self._crear(
            inicio="2026-10-31 11:00",
            fin="2026-10-31 12:00",
        )

        self.assertEqual(len(self._historial()), 2)
        self.assertNotEqual(primera.id, segunda.id)
        self.assertTrue(
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 12:00",
                "2026-10-31 13:00",
            )
        )

    def test_acepta_unidades_distintas_en_horarios_iguales(self) -> None:
        primera = self._crear(unidad_id="MIC-01")
        segunda = self._crear(unidad_id="MIC-02")

        self.assertEqual(len(self._historial()), 2)
        self.assertNotEqual(primera.id, segunda.id)

    def test_disponibilidad_antes_y_despues_de_reservar(self) -> None:
        self.assertTrue(
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 10:00",
                "2026-10-31 11:00",
            )
        )

        self._crear(inicio="2026-10-31 10:00", fin="2026-10-31 11:00")

        self.assertFalse(
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 10:00",
                "2026-10-31 11:00",
            )
        )
        self.assertTrue(
            self.servicio.consultar_disponibilidad(
                "MIC-02",
                "2026-10-31 10:00",
                "2026-10-31 11:00",
            )
        )

    def test_disponibilidad_rechaza_unidad_inexistente_y_entradas_invalidas(
        self,
    ) -> None:
        with self.assertRaises(UnidadInexistente):
            self.servicio.consultar_disponibilidad(
                "NO-EXISTE",
                "2026-10-31 10:00",
                "2026-10-31 11:00",
            )

        with self.assertRaises(ErrorFormatoTiempo):
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-1-1 10:00",
                "2026-10-31 11:00",
            )

        with self.assertRaises(ErrorIntervalo):
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 11:00",
                "2026-10-31 10:00",
            )

    def test_cancelacion_conserva_datos_y_cambia_solo_estado_y_fecha(self) -> None:
        reserva = self._crear()

        resultado = self.servicio.cancelar_reserva(reserva.id)

        self.assertIsInstance(resultado, ResultadoCancelacion)
        self.assertTrue(resultado.cancelada_ahora)
        cancelada = resultado.reserva
        self.assertEqual(cancelada.id, reserva.id)
        self.assertEqual(cancelada.unidad_id, reserva.unidad_id)
        self.assertEqual(cancelada.solicitante, reserva.solicitante)
        self.assertEqual(cancelada.inicio, reserva.inicio)
        self.assertEqual(cancelada.fin, reserva.fin)
        self.assertEqual(cancelada.creada_en, reserva.creada_en)
        self.assertEqual(cancelada.estado, EstadoReserva.CANCELADA)
        self.assertIsNotNone(cancelada.cancelada_en)

        persistida = obtener_reserva(self.conexion, reserva.id)
        self.assertEqual(persistida, cancelada)
        self.assertEqual(len(self._historial()), 1)

    def test_cancelar_libera_el_horario(self) -> None:
        reserva = self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        self.assertFalse(
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 10:30",
                "2026-10-31 11:30",
            )
        )

        self.servicio.cancelar_reserva(reserva.id)

        self.assertTrue(
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 10:30",
                "2026-10-31 11:30",
            )
        )
        nueva = self._crear(
            inicio="2026-10-31 10:30",
            fin="2026-10-31 11:30",
        )
        self.assertEqual(nueva.estado, EstadoReserva.ACTIVA)

    def test_historial_incluye_activas_y_canceladas(self) -> None:
        activa = self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        cancelada = self._crear(
            inicio="2026-10-31 11:00",
            fin="2026-10-31 12:00",
        )
        self.servicio.cancelar_reserva(cancelada.id)

        todas = self.servicio.listar_historial()
        solo_activas = self.servicio.listar_historial(EstadoReserva.ACTIVA)
        solo_canceladas = self.servicio.listar_historial(EstadoReserva.CANCELADA)

        self.assertEqual(
            [reserva.id for reserva in todas],
            [activa.id, cancelada.id],
        )
        self.assertEqual([reserva.id for reserva in solo_activas], [activa.id])
        self.assertEqual(
            [reserva.id for reserva in solo_canceladas],
            [cancelada.id],
        )

    def test_cancelar_reserva_inexistente_no_modifica_la_base(self) -> None:
        with self.assertRaises(ReservaNoEncontrada):
            self.servicio.cancelar_reserva("no-existe")

        self.assertEqual(self._historial(), [])

    def test_doble_cancelacion_no_modifica_la_reserva(self) -> None:
        reserva = self._crear()

        primera = self.servicio.cancelar_reserva(reserva.id)
        segunda = self.servicio.cancelar_reserva(reserva.id)

        self.assertTrue(primera.cancelada_ahora)
        self.assertFalse(segunda.cancelada_ahora)
        self.assertEqual(segunda.reserva, primera.reserva)
        self.assertEqual(len(self._historial()), 1)

    def test_persistencia_tras_cerrar_y_reabrir_la_conexion(self) -> None:
        activa = self._crear(
            inicio="2026-10-31 10:00",
            fin="2026-10-31 11:00",
        )
        cancelada = self._crear(
            inicio="2026-10-31 11:00",
            fin="2026-10-31 12:00",
        )
        self.servicio.cancelar_reserva(cancelada.id)

        self._cerrar_conexion()
        self.conexion = conectar(self.ruta_bd)
        self.servicio = ServicioReservas(self.conexion, cargar_inventario())

        historial = {
            reserva.id: reserva for reserva in self.servicio.listar_historial()
        }
        self.assertEqual(historial[activa.id].estado, EstadoReserva.ACTIVA)
        self.assertEqual(historial[cancelada.id].estado, EstadoReserva.CANCELADA)
        self.assertIsNotNone(historial[cancelada.id].cancelada_en)
        self.assertFalse(
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 10:00",
                "2026-10-31 11:00",
            )
        )
        self.assertTrue(
            self.servicio.consultar_disponibilidad(
                "MIC-01",
                "2026-10-31 11:00",
                "2026-10-31 12:00",
            )
        )


if __name__ == "__main__":
    unittest.main()
