"""Modelos de dominio del sistema de reservas.

Los instantes se representan con ``datetime`` naive en hora local de
``America/Argentina/Buenos_Aires``. Véanse las limitaciones documentadas en
``reservas.tiempo``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .tiempo import validar_intervalo


class EstadoReserva(StrEnum):
    """Estados persistidos de una reserva."""

    ACTIVA = "activa"
    CANCELADA = "cancelada"


@dataclass(frozen=True, slots=True)
class Unidad:
    """Una unidad física del inventario fijo."""

    id: str
    equipo: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("El identificador de la unidad no puede estar vacío.")
        if self.id != self.id.strip():
            raise ValueError("El identificador de la unidad no puede tener espacios exteriores.")
        if not isinstance(self.equipo, str) or not self.equipo.strip():
            raise ValueError("El nombre del equipo no puede estar vacío.")
        if self.equipo != self.equipo.strip():
            raise ValueError("El nombre del equipo no puede tener espacios exteriores.")


@dataclass(slots=True)
class Reserva:
    """Reserva de una unidad para el intervalo semiabierto ``[inicio, fin)``."""

    id: str
    unidad_id: str
    solicitante: str
    inicio: datetime
    fin: datetime
    estado: EstadoReserva
    creada_en: datetime
    cancelada_en: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("El identificador de la reserva no puede estar vacío.")
        if not isinstance(self.unidad_id, str) or not self.unidad_id.strip():
            raise ValueError("La unidad de la reserva no puede estar vacía.")
        if not isinstance(self.solicitante, str) or not self.solicitante.strip():
            raise ValueError(
                "El solicitante no puede estar vacío ni compuesto solo por espacios."
            )
        if not isinstance(self.estado, EstadoReserva):
            raise ValueError("El estado de la reserva debe ser 'activa' o 'cancelada'.")
        if not isinstance(self.creada_en, datetime):
            raise ValueError("La fecha de creación debe ser un datetime.")
        if self.cancelada_en is not None and not isinstance(self.cancelada_en, datetime):
            raise ValueError("La fecha de cancelación debe ser un datetime o None.")
        if self.estado is EstadoReserva.ACTIVA and self.cancelada_en is not None:
            raise ValueError("Una reserva activa no puede tener fecha de cancelación.")
        if self.estado is EstadoReserva.CANCELADA and self.cancelada_en is None:
            raise ValueError("Una reserva cancelada debe registrar su fecha de cancelación.")

        validar_intervalo(self.inicio, self.fin)
        self.solicitante = self.solicitante.strip()

    @property
    def activa(self) -> bool:
        """Indica si la reserva sigue bloqueando su intervalo."""
        return self.estado is EstadoReserva.ACTIVA
