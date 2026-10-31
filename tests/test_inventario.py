"""Pruebas del inventario fijo y del modelo de unidad."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from reservas.inventario import (
    RUTA_INVENTARIO_POR_DEFECTO,
    ErrorInventario,
    cargar_inventario,
)
from reservas.modelos import Unidad

UNIDADES_ESPERADAS = (
    ("MIC-01", "Microscopio digital"),
    ("MIC-02", "Microscopio digital"),
    ("OSC-01", "Osciloscopio"),
    ("MUL-01", "Multímetro"),
    ("FUE-01", "Fuente de alimentación"),
)


class PruebasInventarioReal(unittest.TestCase):
    def test_carga_las_cinco_unidades_esperadas(self) -> None:
        inventario = cargar_inventario()

        self.assertEqual(len(inventario), 5)
        self.assertEqual(
            tuple((unidad.id, unidad.equipo) for unidad in inventario),
            UNIDADES_ESPERADAS,
        )

    def test_no_modifica_el_archivo_de_inventario(self) -> None:
        antes = RUTA_INVENTARIO_POR_DEFECTO.read_bytes()

        cargar_inventario()

        despues = RUTA_INVENTARIO_POR_DEFECTO.read_bytes()
        self.assertEqual(antes, despues)

    def test_obtiene_una_unidad_conocida(self) -> None:
        inventario = cargar_inventario()

        unidad = inventario.obtener("OSC-01")

        self.assertIsNotNone(unidad)
        assert unidad is not None
        self.assertEqual(unidad.equipo, "Osciloscopio")
        self.assertTrue(inventario.contiene("MUL-01"))

    def test_los_identificadores_son_exactos_y_sensibles_a_mayusculas(self) -> None:
        inventario = cargar_inventario()

        self.assertIsNone(inventario.obtener("mic-01"))
        self.assertFalse(inventario.contiene("MIC-1"))
        self.assertFalse(inventario.contiene(" MIC-01 "))

    def test_la_ruta_por_defecto_apunta_al_inventario_del_repositorio(self) -> None:
        self.assertTrue(RUTA_INVENTARIO_POR_DEFECTO.is_file())
        self.assertEqual(RUTA_INVENTARIO_POR_DEFECTO.name, "inventario.json")
        self.assertEqual(RUTA_INVENTARIO_POR_DEFECTO.parent.name, "data")


class PruebasValidacionInventario(unittest.TestCase):
    def setUp(self) -> None:
        self._directorio = tempfile.TemporaryDirectory()
        self.addCleanup(self._directorio.cleanup)
        self.ruta = Path(self._directorio.name) / "inventario.json"

    def _escribir(self, datos: object) -> None:
        self.ruta.write_text(
            json.dumps(datos, ensure_ascii=False),
            encoding="utf-8",
        )

    def test_rechaza_archivo_inexistente(self) -> None:
        ruta_inexistente = Path(self._directorio.name) / "no-existe.json"

        with self.assertRaises(ErrorInventario):
            cargar_inventario(ruta_inexistente)

    def test_rechaza_json_invalido(self) -> None:
        self.ruta.write_text("{esto no es json", encoding="utf-8")

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_raiz_que_no_es_lista(self) -> None:
        self._escribir({"id": "MIC-01", "equipo": "Microscopio digital"})

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_lista_vacia(self) -> None:
        self._escribir([])

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_entrada_que_no_es_objeto(self) -> None:
        self._escribir(["MIC-01"])

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_campos_faltantes(self) -> None:
        self._escribir([{"id": "MIC-01"}])

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_identificador_vacio(self) -> None:
        self._escribir([{"id": "   ", "equipo": "Microscopio digital"}])

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_identificador_con_espacios_exteriores(self) -> None:
        self._escribir([{"id": " MIC-01", "equipo": "Microscopio digital"}])

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_equipo_vacio(self) -> None:
        self._escribir([{"id": "MIC-01", "equipo": ""}])

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_equipo_con_espacios_exteriores(self) -> None:
        self._escribir([{"id": "MIC-01", "equipo": " Microscopio digital "}])

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)

    def test_rechaza_identificadores_duplicados(self) -> None:
        self._escribir(
            [
                {"id": "MIC-01", "equipo": "Microscopio digital"},
                {"id": "MIC-01", "equipo": "Otro microscopio"},
            ]
        )

        with self.assertRaises(ErrorInventario):
            cargar_inventario(self.ruta)


class PruebasModeloUnidad(unittest.TestCase):
    def test_unidad_valida(self) -> None:
        unidad = Unidad(id="MIC-01", equipo="Microscopio digital")

        self.assertEqual(unidad.id, "MIC-01")
        self.assertEqual(unidad.equipo, "Microscopio digital")

    def test_rechaza_identificador_vacio(self) -> None:
        with self.assertRaises(ValueError):
            Unidad(id="", equipo="Microscopio digital")

    def test_rechaza_espacios_exteriores(self) -> None:
        with self.assertRaises(ValueError):
            Unidad(id=" MIC-01", equipo="Microscopio digital")

        with self.assertRaises(ValueError):
            Unidad(id="MIC-01", equipo="Microscopio digital ")


if __name__ == "__main__":
    unittest.main()
