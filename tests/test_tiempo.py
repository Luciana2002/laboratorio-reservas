"""Pruebas del manejo estricto de fechas, intervalos y modelos de reserva."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from reservas.modelos import EstadoReserva, Reserva
from reservas.tiempo import (
    ZONA_ARGENTINA,
    ErrorFormatoTiempo,
    ErrorIntervalo,
    ErrorTiempo,
    ahora_local,
    formatear_fecha_hora,
    parsear_fecha_hora,
    validar_intervalo,
)


class PruebasParseoFechaHora(unittest.TestCase):
    def test_parsea_el_formato_estricto(self) -> None:
        momento = parsear_fecha_hora("2026-10-31 09:05")

        self.assertEqual(momento, datetime(2026, 10, 31, 9, 5))
        self.assertIsNone(momento.tzinfo)

    def test_acepta_medianoche_y_ultimo_minuto_del_dia(self) -> None:
        self.assertEqual(
            parsear_fecha_hora("2026-01-01 00:00"),
            datetime(2026, 1, 1, 0, 0),
        )
        self.assertEqual(
            parsear_fecha_hora("2026-12-31 23:59"),
            datetime(2026, 12, 31, 23, 59),
        )

    def test_acepta_29_de_febrero_en_anio_bisiesto(self) -> None:
        self.assertEqual(
            parsear_fecha_hora("2024-02-29 10:00"),
            datetime(2024, 2, 29, 10, 0),
        )

    def test_formatea_y_vuelve_a_parsear(self) -> None:
        momento = datetime(2026, 10, 31, 9, 5)

        texto = formatear_fecha_hora(momento)

        self.assertEqual(texto, "2026-10-31 09:05")
        self.assertEqual(parsear_fecha_hora(texto), momento)

    def test_rechaza_formatos_no_estrictos(self) -> None:
        invalidos = (
            "2026-1-1 09:05",
            "2026-01-01 9:05",
            "2026/01/01 09:05",
            "2026-01-01T09:05",
            "2026-01-01 09:05:00",
            "2026-01-01",
            "",
            " 2026-01-01 09:05",
            "2026-01-01 09:05 ",
            "2026-01-01  09:05",
            "2026-01-01 09:05\n",
        )

        for texto in invalidos:
            with self.subTest(texto=texto):
                with self.assertRaises(ErrorFormatoTiempo):
                    parsear_fecha_hora(texto)

    def test_rechaza_fechas_u_horas_inexistentes(self) -> None:
        invalidos = (
            "2026-02-30 10:00",
            "2026-02-29 10:00",
            "2025-02-29 10:00",
            "2026-04-31 10:00",
            "2026-13-01 10:00",
            "2026-00-10 10:00",
            "2026-01-00 10:00",
            "2026-01-01 24:00",
            "2026-01-01 10:60",
            "0000-01-01 00:00",
        )

        for texto in invalidos:
            with self.subTest(texto=texto):
                with self.assertRaises(ErrorFormatoTiempo):
                    parsear_fecha_hora(texto)

    def test_rechaza_valores_que_no_son_texto(self) -> None:
        for valor in (None, 123, datetime(2026, 1, 1, 0, 0)):
            with self.subTest(valor=valor):
                with self.assertRaises(ErrorFormatoTiempo):
                    parsear_fecha_hora(valor)  # type: ignore[arg-type]

    def test_formatear_rechaza_tipos_invalidos_y_fechas_con_zona(self) -> None:
        with self.assertRaises(ErrorTiempo):
            formatear_fecha_hora("2026-01-01 10:00")  # type: ignore[arg-type]

        with self.assertRaises(ErrorTiempo):
            formatear_fecha_hora(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))

    def test_ahora_local_devuelve_un_datetime_naive(self) -> None:
        self.assertIsNone(ahora_local().tzinfo)

    def test_la_zona_argentina_tiene_offset_menos_tres(self) -> None:
        self.assertEqual(ZONA_ARGENTINA.utcoffset(None), timedelta(hours=-3))


class PruebasIntervalo(unittest.TestCase):
    def test_acepta_inicio_anterior_al_fin(self) -> None:
        validar_intervalo(
            datetime(2026, 10, 31, 10, 0),
            datetime(2026, 10, 31, 11, 0),
        )

    def test_acepta_intervalos_consecutivos(self) -> None:
        validar_intervalo(
            datetime(2026, 10, 31, 10, 0),
            datetime(2026, 10, 31, 11, 0),
        )
        validar_intervalo(
            datetime(2026, 10, 31, 11, 0),
            datetime(2026, 10, 31, 12, 0),
        )

    def test_rechaza_inicio_igual_al_fin(self) -> None:
        momento = datetime(2026, 10, 31, 10, 0)

        with self.assertRaises(ErrorIntervalo):
            validar_intervalo(momento, momento)

    def test_rechaza_inicio_posterior_al_fin(self) -> None:
        with self.assertRaises(ErrorIntervalo):
            validar_intervalo(
                datetime(2026, 10, 31, 11, 0),
                datetime(2026, 10, 31, 10, 0),
            )

    def test_rechaza_tipos_invalidos(self) -> None:
        with self.assertRaises(ErrorIntervalo):
            validar_intervalo("2026-10-31 10:00", datetime(2026, 10, 31, 11, 0))  # type: ignore[arg-type]

        with self.assertRaises(ErrorIntervalo):
            validar_intervalo(datetime(2026, 10, 31, 10, 0), None)  # type: ignore[arg-type]

    def test_rechaza_fechas_con_zona_horaria(self) -> None:
        with self.assertRaises(ErrorIntervalo):
            validar_intervalo(
                datetime(2026, 10, 31, 10, 0, tzinfo=timezone.utc),
                datetime(2026, 10, 31, 11, 0, tzinfo=timezone.utc),
            )

    def test_el_error_de_intervalo_es_un_value_error(self) -> None:
        self.assertTrue(issubclass(ErrorIntervalo, ErrorTiempo))
        self.assertTrue(issubclass(ErrorIntervalo, ValueError))


class PruebasModelosDeReserva(unittest.TestCase):
    def _crear_reserva(self, **cambios: object) -> Reserva:
        datos: dict[str, object] = {
            "id": "reserva-1",
            "unidad_id": "MIC-01",
            "solicitante": "  Ada Lovelace  ",
            "inicio": datetime(2026, 10, 31, 10, 0),
            "fin": datetime(2026, 10, 31, 11, 0),
            "estado": EstadoReserva.ACTIVA,
            "creada_en": datetime(2026, 10, 31, 9, 0),
        }
        datos.update(cambios)
        return Reserva(**datos)  # type: ignore[arg-type]

    def test_los_estados_tienen_los_valores_esperados(self) -> None:
        self.assertEqual(EstadoReserva.ACTIVA.value, "activa")
        self.assertEqual(EstadoReserva.CANCELADA.value, "cancelada")
        self.assertEqual(EstadoReserva.ACTIVA, "activa")

    def test_reserva_activa_valida_recorta_el_solicitante(self) -> None:
        reserva = self._crear_reserva()

        self.assertEqual(reserva.solicitante, "Ada Lovelace")
        self.assertTrue(reserva.activa)
        self.assertIsNone(reserva.cancelada_en)

    def test_reserva_cancelada_conserva_sus_datos(self) -> None:
        reserva = self._crear_reserva(
            estado=EstadoReserva.CANCELADA,
            cancelada_en=datetime(2026, 10, 31, 9, 30),
        )

        self.assertFalse(reserva.activa)
        self.assertEqual(reserva.id, "reserva-1")
        self.assertEqual(reserva.unidad_id, "MIC-01")
        self.assertEqual(reserva.inicio, datetime(2026, 10, 31, 10, 0))
        self.assertEqual(reserva.fin, datetime(2026, 10, 31, 11, 0))

    def test_rechaza_intervalo_vacio(self) -> None:
        with self.assertRaises(ErrorIntervalo):
            self._crear_reserva(fin=datetime(2026, 10, 31, 10, 0))

    def test_rechaza_inicio_posterior_al_fin(self) -> None:
        with self.assertRaises(ErrorIntervalo):
            self._crear_reserva(fin=datetime(2026, 10, 31, 9, 59))

    def test_rechaza_solicitante_en_blanco(self) -> None:
        with self.assertRaises(ValueError):
            self._crear_reserva(solicitante="   ")

    def test_rechaza_reserva_activa_con_fecha_de_cancelacion(self) -> None:
        with self.assertRaises(ValueError):
            self._crear_reserva(cancelada_en=datetime(2026, 10, 31, 9, 30))

    def test_rechaza_reserva_cancelada_sin_fecha_de_cancelacion(self) -> None:
        with self.assertRaises(ValueError):
            self._crear_reserva(estado=EstadoReserva.CANCELADA)


if __name__ == "__main__":
    unittest.main()
