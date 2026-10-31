"""Conexión y esquema de la base SQLite local.

La base se guarda por defecto en ``data/reservas.db``. El esquema se crea de
forma idempotente con ``CREATE ... IF NOT EXISTS``: abrir una base existente no
borra ni recrea tablas ni pierde registros.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

RUTA_BD_POR_DEFECTO = Path(__file__).resolve().parents[1] / "data" / "reservas.db"

_SENTENCIAS_ESQUEMA = (
    """
    CREATE TABLE IF NOT EXISTS reservas (
        id TEXT PRIMARY KEY,
        unidad_id TEXT NOT NULL,
        solicitante TEXT NOT NULL CHECK (length(trim(solicitante)) > 0),
        inicio TEXT NOT NULL,
        fin TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (estado IN ('activa', 'cancelada')),
        creada_en TEXT NOT NULL,
        cancelada_en TEXT,
        CHECK (inicio < fin),
        CHECK (
            (estado = 'activa' AND cancelada_en IS NULL)
            OR (estado = 'cancelada' AND cancelada_en IS NOT NULL)
        )
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_reservas_conflicto
        ON reservas (unidad_id, estado, inicio, fin)
    """,
)


def crear_esquema(conexion: sqlite3.Connection) -> None:
    """Crea la tabla y el índice si no existen. No elimina datos."""
    for sentencia in _SENTENCIAS_ESQUEMA:
        conexion.execute(sentencia)


def conectar(ruta: str | Path | None = None) -> sqlite3.Connection:
    """Abre una conexión SQLite configurada y asegura el esquema.

    ``ruta`` puede ser una ruta a archivo o ``":memory:"``. Si se omite, usa
    ``data/reservas.db``.
    """
    if ruta is None:
        destino: str | Path = RUTA_BD_POR_DEFECTO
    elif str(ruta) == ":memory:":
        destino = ":memory:"
    else:
        destino = Path(ruta)

    if isinstance(destino, Path):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino_texto = str(destino)
    else:
        destino_texto = destino

    conexion = sqlite3.connect(destino_texto, isolation_level=None)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.execute("PRAGMA busy_timeout = 5000")
    crear_esquema(conexion)
    return conexion
