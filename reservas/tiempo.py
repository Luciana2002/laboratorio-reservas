"""Parseo y validación estricta de fechas y horas.

Zona horaria
------------
Las fechas se interpretan como hora local de ``America/Argentina/Buenos_Aires``.
Se usan objetos ``datetime`` naive (sin ``tzinfo``) para no depender de
``tzdata``, que no forma parte de la biblioteca estándar en Windows.

Buenos Aires usa UTC-03:00 de forma estable desde 2009. Este módulo no
reproduce los cambios históricos de horario de verano anteriores a esa fecha,
no acepta zonas horarias por reserva y no realiza conversiones entre zonas.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M"

# \Z (y no $) para rechazar, por ejemplo, un salto de línea final.
PATRON_FECHA_HORA = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}\Z")

ZONA_ARGENTINA = timezone(timedelta(hours=-3), name="America/Argentina/Buenos_Aires")


class ErrorTiempo(ValueError):
    """Error base de fechas y horas."""


class ErrorFormatoTiempo(ErrorTiempo):
    """El texto no respeta el formato estricto AAAA-MM-DD HH:MM."""


class ErrorIntervalo(ErrorTiempo):
    """El intervalo no cumple la condición inicio < fin."""


def parsear_fecha_hora(texto: str) -> datetime:
    """Convierte un texto estricto ``AAAA-MM-DD HH:MM`` en un datetime naive.

    Se rechazan variantes sin ceros a la izquierda, formatos ISO con ``T``,
    segundos, espacios exteriores y fechas u horas inexistentes.
    """
    if not isinstance(texto, str):
        raise ErrorFormatoTiempo("La fecha y hora deben ingresarse como texto.")
    if not PATRON_FECHA_HORA.fullmatch(texto):
        raise ErrorFormatoTiempo(
            "Formato inválido: se esperaba AAAA-MM-DD HH:MM y se recibió "
            f"{texto!r}."
        )
    try:
        return datetime.strptime(texto, FORMATO_FECHA_HORA)
    except ValueError as exc:
        raise ErrorFormatoTiempo(f"Fecha u hora inexistente: {texto!r}.") from exc


def formatear_fecha_hora(momento: datetime) -> str:
    """Devuelve un datetime naive en el formato estricto del sistema."""
    if not isinstance(momento, datetime):
        raise ErrorTiempo("Se esperaba un objeto datetime.")
    if momento.tzinfo is not None:
        raise ErrorTiempo("Se esperaba un datetime sin zona horaria (naive).")
    return momento.strftime(FORMATO_FECHA_HORA)


def validar_intervalo(inicio: datetime, fin: datetime) -> None:
    """Exige ``inicio < fin`` para un intervalo semiabierto ``[inicio, fin)``."""
    if not isinstance(inicio, datetime) or not isinstance(fin, datetime):
        raise ErrorIntervalo("El inicio y el fin deben ser fechas y horas válidas.")
    if inicio.tzinfo is not None or fin.tzinfo is not None:
        raise ErrorIntervalo("El inicio y el fin deben ser datetimes sin zona horaria (naive).")
    if inicio >= fin:
        raise ErrorIntervalo("El inicio debe ser estrictamente anterior al fin.")


def ahora_local() -> datetime:
    """Devuelve la hora local argentina como datetime naive."""
    return datetime.now(ZONA_ARGENTINA).replace(tzinfo=None)
