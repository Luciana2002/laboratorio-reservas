"""Pruebas de superposición de reservas y de inserción atómica."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from reservas.db import conectar
from reservas.modelos import EstadoReserva, Reserva
from reservas.repositorio import (
    hay_conflicto,
    insertar_reserva,
    insertar_si_libre,
    listar_reservas,
)
from reservas.tiempo import ErrorIntervalo


class PruebasConflictos(unittest.TestCase):
    def setUp(self) -> None:
        self._directorio = tempfile.TemporaryDirectory()
        self.addCleanup(self._directorio.cleanup)
        self.ruta_bd = Path(self._directorio.name) / "reservas.db"
        self.conexion = conectar(self.ruta_bd)
        self.addCleanup(self.conexion.close)

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
        cancelada_en: datetime | None = None,
    ) -> Reserva:
        return Reserva(
            id=identificador,
            unidad_id=unidad_id,
            solicitante="Solicitante ficticio",
            inicio=inicio,
            fin=fin,
            estado=estado,
            creada_en=self._momento(8),
            cancelada_en=cancelada_en,
        )

    def _insertar(
        self,
        identificador: str,
        inicio: datetime,
        fin: datetime,
        **cambios: object,
    ) -> None:
        insertar_reserva(
            self.conexion,
            self._reserva(identificador, inicio, fin, **cambios),  # type: ignore[arg-type]
        )

    def test_superposicion_parcial(self) -> None:
        self._insertar("r1", self._momento(10), self._momento(11))

        self.assertTrue(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(10, 30),
                self._momento(11, 30),
            )
        )

    def test_intervalos_identicos(self) -> None:
        self._insertar("r1", self._momento(10), self._momento(11))

        self.assertTrue(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(10),
                self._momento(11),
            )
        )

    def test_reserva_nueva_contiene_a_la_existente(self) -> None:
        self._insertar("r1", self._momento(10, 30), self._momento(11))

        self.assertTrue(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(10),
                self._momento(12),
            )
        )

    def test_reserva_existente_contiene_a_la_nueva(self) -> None:
        self._insertar("r1", self._momento(10), self._momento(12))

        self.assertTrue(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(10, 30),
                self._momento(11),
            )
        )

    def test_horarios_consecutivos_no_conflictuan(self) -> None:
        self._insertar("r1", self._momento(10), self._momento(11))

        self.assertFalse(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(11),
                self._momento(12),
            )
        )
        self.assertFalse(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(9),
                self._momento(10),
            )
        )

    def test_unidades_distintas_no_conflictuan(self) -> None:
        self._insertar("r1", self._momento(10), self._momento(11), unidad_id="MIC-01")

        self.assertFalse(
            hay_conflicto(
                self.conexion,
                "MIC-02",
                self._momento(10),
                self._momento(11),
            )
        )

    def test_reserva_cancelada_no_bloquea(self) -> None:
        self._insertar(
            "cancelada",
            self._momento(10),
            self._momento(11),
            estado=EstadoReserva.CANCELADA,
            cancelada_en=self._momento(9, 30),
        )

        self.assertFalse(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(10, 30),
                self._momento(11, 30),
            )
        )

    def test_reserva_activa_bloquea_aunque_exista_una_cancelada(self) -> None:
        self._insertar(
            "cancelada",
            self._momento(10),
            self._momento(11),
            estado=EstadoReserva.CANCELADA,
            cancelada_en=self._momento(9, 30),
        )
        self._insertar("activa", self._momento(10), self._momento(11))

        self.assertTrue(
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(10, 30),
                self._momento(11, 30),
            )
        )

    def test_insertar_si_libre_inserta_si_no_hay_conflicto(self) -> None:
        insertado = insertar_si_libre(
            self.conexion,
            self._reserva("r1", self._momento(10), self._momento(11)),
        )

        self.assertTrue(insertado)
        self.assertEqual(
            [reserva.id for reserva in listar_reservas(self.conexion)],
            ["r1"],
        )
        self.assertFalse(self.conexion.in_transaction)

    def test_insertar_si_libre_rechaza_conflicto_sin_insertar(self) -> None:
        self._insertar("r1", self._momento(10), self._momento(11))

        insertado = insertar_si_libre(
            self.conexion,
            self._reserva("r2", self._momento(10, 30), self._momento(11, 30)),
        )

        self.assertFalse(insertado)
        self.assertEqual(
            {reserva.id for reserva in listar_reservas(self.conexion)},
            {"r1"},
        )
        self.assertFalse(self.conexion.in_transaction)

    def test_insertar_si_libre_permite_consecutivos(self) -> None:
        self.assertTrue(
            insertar_si_libre(
                self.conexion,
                self._reserva("r1", self._momento(10), self._momento(11)),
            )
        )
        self.assertTrue(
            insertar_si_libre(
                self.conexion,
                self._reserva("r2", self._momento(11), self._momento(12)),
            )
        )

        self.assertEqual(
            [reserva.id for reserva in listar_reservas(self.conexion)],
            ["r1", "r2"],
        )

    def test_insertar_si_libre_permite_unidades_distintas(self) -> None:
        self.assertTrue(
            insertar_si_libre(
                self.conexion,
                self._reserva(
                    "r1",
                    self._momento(10),
                    self._momento(11),
                    unidad_id="MIC-01",
                ),
            )
        )
        self.assertTrue(
            insertar_si_libre(
                self.conexion,
                self._reserva(
                    "r2",
                    self._momento(10),
                    self._momento(11),
                    unidad_id="MIC-02",
                ),
            )
        )

        self.assertEqual(len(listar_reservas(self.conexion)), 2)

    def test_insertar_si_libre_permite_activa_sobre_intervalo_cancelado(self) -> None:
        self._insertar(
            "cancelada",
            self._momento(10),
            self._momento(11),
            estado=EstadoReserva.CANCELADA,
            cancelada_en=self._momento(9, 30),
        )

        insertado = insertar_si_libre(
            self.conexion,
            self._reserva("activa", self._momento(10), self._momento(11)),
        )

        self.assertTrue(insertado)
        self.assertEqual(len(listar_reservas(self.conexion)), 2)

    def test_hay_conflicto_rechaza_intervalo_invalido(self) -> None:
        with self.assertRaises(ErrorIntervalo):
            hay_conflicto(
                self.conexion,
                "MIC-01",
                self._momento(11),
                self._momento(10),
            )

    def test_consulta_parametrizada_no_interpreta_sql(self) -> None:
        self._insertar("r1", self._momento(10), self._momento(11))

        self.assertFalse(
            hay_conflicto(
                self.conexion,
                "MIC-01' OR '1'='1",
                self._momento(10),
                self._momento(11),
            )
        )


if __name__ == "__main__":
    unittest.main()
