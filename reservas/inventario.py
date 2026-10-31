"""Carga y validación del inventario fijo en ``data/inventario.json``.

El inventario es de solo lectura: este módulo nunca escribe ni modifica el
archivo. La lista de unidades es la fuente única para validar que una unidad
reservada existe.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .modelos import Unidad

RUTA_INVENTARIO_POR_DEFECTO = (
    Path(__file__).resolve().parents[1] / "data" / "inventario.json"
)


class ErrorInventario(ValueError):
    """El inventario no existe, no se puede leer o no tiene la estructura esperada."""


@dataclass(frozen=True, slots=True)
class Inventario:
    """Colección ordenada de unidades, sin identificadores duplicados."""

    unidades: tuple[Unidad, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.unidades, tuple):
            object.__setattr__(self, "unidades", tuple(self.unidades))
        if not self.unidades:
            raise ErrorInventario("El inventario no puede estar vacío.")
        for unidad in self.unidades:
            if not isinstance(unidad, Unidad):
                raise ErrorInventario(
                    "El inventario contiene una entrada que no es una unidad válida."
                )
        ids = [unidad.id for unidad in self.unidades]
        if len(ids) != len(set(ids)):
            raise ErrorInventario("El inventario contiene identificadores duplicados.")

    def obtener(self, unidad_id: str) -> Unidad | None:
        """Busca una unidad por ID exacto, sensible a mayúsculas."""
        for unidad in self.unidades:
            if unidad.id == unidad_id:
                return unidad
        return None

    def contiene(self, unidad_id: str) -> bool:
        """Indica si el ID pertenece al inventario."""
        return self.obtener(unidad_id) is not None

    def __iter__(self) -> Iterator[Unidad]:
        return iter(self.unidades)

    def __len__(self) -> int:
        return len(self.unidades)


def cargar_inventario(ruta: str | Path | None = None) -> Inventario:
    """Lee y valida el inventario desde JSON.

    Si no se indica ``ruta``, se usa ``data/inventario.json`` del repositorio.
    """
    ruta_archivo = Path(ruta) if ruta is not None else RUTA_INVENTARIO_POR_DEFECTO

    try:
        texto = ruta_archivo.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ErrorInventario(
            f"No existe el archivo de inventario: {ruta_archivo}."
        ) from exc
    except OSError as exc:
        raise ErrorInventario(
            f"No se pudo leer el archivo de inventario {ruta_archivo}: {exc}."
        ) from exc

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErrorInventario(
            f"El inventario no contiene JSON válido: {exc.msg}."
        ) from exc

    if not isinstance(datos, list):
        raise ErrorInventario("El inventario debe ser una lista de unidades.")

    unidades = tuple(
        _crear_unidad(entrada, indice) for indice, entrada in enumerate(datos)
    )
    return Inventario(unidades)


def _crear_unidad(entrada: Any, indice: int) -> Unidad:
    numero = indice + 1
    if not isinstance(entrada, dict):
        raise ErrorInventario(
            f"La entrada {numero} del inventario debe ser un objeto JSON."
        )
    for campo in ("id", "equipo"):
        if campo not in entrada:
            raise ErrorInventario(
                f"La entrada {numero} del inventario no tiene el campo '{campo}'."
            )

    unidad_id = entrada["id"]
    equipo = entrada["equipo"]

    if not isinstance(unidad_id, str) or not unidad_id.strip():
        raise ErrorInventario(
            f"La entrada {numero} tiene un identificador vacío o inválido."
        )
    if unidad_id != unidad_id.strip():
        raise ErrorInventario(
            f"El identificador de la entrada {numero} no puede tener espacios exteriores."
        )
    if not isinstance(equipo, str) or not equipo.strip():
        raise ErrorInventario(
            f"La entrada {numero} tiene un nombre de equipo vacío o inválido."
        )
    if equipo != equipo.strip():
        raise ErrorInventario(
            f"El nombre del equipo de la entrada {numero} no puede tener espacios exteriores."
        )

    try:
        return Unidad(id=unidad_id, equipo=equipo)
    except ValueError as exc:
        raise ErrorInventario(
            f"La entrada {numero} del inventario es inválida: {exc}"
        ) from exc
