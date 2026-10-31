"""Pruebas de persistencia y recuperación de reservas en SQLite."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from reservas.db import conectar, crear_esquema
from reservas.modelos import EstadoReserva, Reserva
from reservas.repositorio import (
    ErrorRepositorio,
    insertar_reserva,
    listar_reservas,
    obtener_reserva,
)


class PruebasRepositorio(unittest.TestCase):
    def setUp(self) -> None:
        self._directorio = tempfile.TemporaryDirectory()
        self.addCleanup(self._directorio.cleanup)
        self.ruta_bd = Path(self._directorio.name) / "reservas.db"
        self.conexion = conectar(self.ruta_bd)
        self.addCleanup(self._cerrar_conexion)

    def _cerrar_conexion(self) -> None:
        if self.conexion is not None:
            self.conexion.close()
            self.conexion = None

    def _momento(self, hora: int, minuto: int = 0) -> datetime:
        return datetime(2026, 10, 31, hora, minuto)

    def _reserva(
        self,
        identificador: str,
        inicio: datetime,
        fin: datetime,
        *,
        unidad_id: str = "MIC-01",
        estado: EstadoReserva = EstadoReserva.ACTIVA,
        creada_en: datetime | None = None,
        cancelada_en: datetime | None = None,
    ) -> Reserva:
        return Reserva(
            id=identificador,
            unidad_id=unidad_id,
            solicitante="  Solicitante ficticio  ",
            inicio=inicio,
            fin=fin,
            estado=estado,
            creada_en=creada_en if creada_en is not None else self._momento(8),
            cancelada_en=cancelada_en,
        )

    def test_guarda_y_recupera_todos_los_campos_de_una_reserva_activa(self) -> None:
        reserva = self._reserva(
            "r-activa",
            self._momento(10),
            self._momento(11),
            creada_en=datetime(2026, 10, 31, 8, 0, 0, 123456),
        )

        insertar_reserva(self.conexion, reserva)
        recuperada = obtener_reserva(self.conexion, "r-activa")

        self.assertIsNotNone(recuperada)
        assert recuperada is not None
        self.assertEqual(recuperada, reserva)
        self.assertEqual(recuperada.estado, EstadoReserva.ACTIVA)
        self.assertIsNone(recuperada.cancelada_en)
        self.assertEqual(recuperada.solicitante, "Solicitante ficticio")

    def test_guarda_y_recupera_reserva_cancelada(self) -> None:
        reserva = self._reserva(
            "r-cancelada",
            self._momento(10),
            self._momento(11),
            estado=EstadoReserva.CANCELADA,
            cancelada_en=datetime(2026, 10, 31, 9, 30, 15, 654321),
        )

        insertar_reserva(self.conexion, reserva)
        recuperada = obtener_reserva(self.conexion, "r-cancelada")

        self.assertIsNotNone(recuperada)
        assert recuperada is not None
        self.assertEqual(recuperada, reserva)
        self.assertEqual(recuperada.estado, EstadoReserva.CANCELADA)
        self.assertEqual(
            recuperada.cancelada_en,
            datetime(2026, 10, 31, 9, 30, 15, 654321),
        )

    def test_lista_todas_las_reservas_y_filtra_por_estado(self) -> None:
        insertar_reserva(
            self.conexion,
            self._reserva("r-activa", self._momento(10), self._momento(11)),
        )
        insertar_reserva(
            self.conexion,
            self._reserva(
                "r-cancelada",
                self._momento(11),
                self._momento(12),
                estado=EstadoReserva.CANCELADA,
                cancelada_en=self._momento(9, 30),
            ),
        )

        todas = listar_reservas(self.conexion)
        activas = listar_reservas(self.conexion, estado=EstadoReserva.ACTIVA)
        canceladas = listar_reservas(self.conexion, estado=EstadoReserva.CANCELADA)

        self.assertEqual([reserva.id for reserva in todas], ["r-activa", "r-cancelada"])
        self.assertEqual([reserva.id for reserva in activas], ["r-activa"])
        self.assertEqual([reserva.id for reserva in canceladas], ["r-cancelada"])

    def test_lista_reservas_por_unidad(self) -> None:
        insertar_reserva(
            self.conexion,
            self._reserva(
                "r-mic-01",
                self._momento(10),
                self._momento(11),
                unidad_id="MIC-01",
            ),
        )
        insertar_reserva(
            self.conexion,
            self._reserva(
                "r-mic-02",
                self._momento(10),
                self._momento(11),
                unidad_id="MIC-02",
            ),
        )

        reservas_mic_02 = listar_reservas(self.conexion, unidad_id="MIC-02")

        self.assertEqual([reserva.id for reserva in reservas_mic_02], ["r-mic-02"])

    def test_la_persistencia_sobrevive_al_cierre_y_reapertura(self) -> None:
        insertar_reserva(
            self.conexion,
            self._reserva("r-activa", self._momento(10), self._momento(11)),
        )
        insertar_reserva(
            self.conexion,
            self._reserva(
                "r-cancelada",
                self._momento(11),
                self._momento(12),
                estado=EstadoReserva.CANCELADA,
                cancelada_en=self._momento(9, 30),
            ),
        )

        self._cerrar_conexion()
        self.conexion = conectar(self.ruta_bd)

        activa = obtener_reserva(self.conexion, "r-activa")
        cancelada = obtener_reserva(self.conexion, "r-cancelada")

        self.assertIsNotNone(activa)
        self.assertIsNotNone(cancelada)
        assert activa is not None and cancelada is not None
        self.assertEqual(activa.estado, EstadoReserva.ACTIVA)
        self.assertEqual(cancelada.estado, EstadoReserva.CANCELADA)
        self.assertEqual(
            {reserva.id for reserva in listar_reservas(self.conexion)},
            {"r-activa", "r-cancelada"},
        )

    def test_crear_esquema_es_idempotente_y_conserva_datos(self) -> None:
        insertar_reserva(
            self.conexion,
            self._reserva("r1", self._momento(10), self._momento(11)),
        )

        crear_esquema(self.conexion)
        crear_esquema(self.conexion)

        self.assertEqual(
            [reserva.id for reserva in listar_reservas(self.conexion)],
            ["r1"],
        )

    def test_id_duplicado_no_reemplaza_el_registro_existente(self) -> None:
        original = self._reserva("r1", self._momento(10), self._momento(11))
        insertar_reserva(self.conexion, original)

        with self.assertRaises(ErrorRepositorio):
            insertar_reserva(
                self.conexion,
                self._reserva("r1", self._momento(12), self._momento(13)),
            )

        recuperada = obtener_reserva(self.conexion, "r1")
        self.assertEqual(recuperada, original)
        self.assertEqual(len(listar_reservas(self.conexion)), 1)

    def test_obtener_reserva_inexistente_devuelve_none(self) -> None:
        self.assertIsNone(obtener_reserva(self.conexion, "no-existe"))


if __name__ == "__main__":
    unittest.main()
