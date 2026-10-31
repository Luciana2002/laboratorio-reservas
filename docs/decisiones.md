# Registro de decisiones

## D-001 — Diseño inicial propuesto (antes de implementación)

- **Decisión:** sistema local de consola en Python con SQLite y biblioteca estándar.
- **Motivo:** reproducibilidad, bajo costo y persistencia sin servicios externos.
- **Alternativas:** API local / almacenamiento JSON; se prefiere consola + SQLite por simplicidad y manejo transaccional.
- **Consecuencia:** no habrá interfaz gráfica; será necesario documentar comandos.
- **Estado:** propuesta de especificación; pendiente de verificar durante implementación.

## D-002 — Intervalos semiabiertos

- **Decisión:** `[inicio, fin)`; los límites consecutivos se permiten.
- **Motivo:** refleja explícitamente la regla de la consigna.
- **Consecuencia:** el conflicto se detecta con comparaciones estrictas.

## D-003 — Fechas pasadas y límites

- **Decisión:** permitir fechas pasadas, sin límite adicional de duración o anticipación.
- **Motivo:** la consigna deja la política abierta y así los escenarios de prueba son reproducibles.
- **Consecuencia:** uso educativo, no una política de reservas reales de un laboratorio.

## D-004 a D-012 — Decisiones técnicas aceptadas para la implementación (2026-10-31)

| ID | Decisión | Motivo | Consecuencia | Estado |
|---|---|---|---|---|
| D-004 | Usar una base SQLite local en `data/reservas.db`. | Persistencia transaccional sin servicios externos y con un archivo ignorado por Git. | La base no se versiona; las pruebas usan bases temporales. | Aceptada; implementación pendiente (Fase 2). |
| D-005 | Exigir el formato estricto `AAAA-MM-DD HH:MM` (24 horas). | Evitar ambigüedades y validar fechas reales. | Se combinan regex estricta y `datetime.strptime`; se rechazan variantes sin ceros. | Aceptada; implementada en Fase 1. |
| D-006 | Interpretar las fechas como hora local de `America/Argentina/Buenos_Aires`, usando `datetime` naive. | Evitar depender de `tzdata`, que no forma parte de la biblioteca estándar en Windows. | No se aceptan zonas por reserva; no se reproducen cambios históricos de horario de verano. | Aceptada; documentada en `reservas/tiempo.py`. |
| D-007 | Comparar los identificadores de unidad de forma exacta y sensible a mayúsculas. | Los IDs del inventario son códigos fijos y distintos entre sí. | `mic-01` no se considera una unidad conocida. | Aceptada; implementada en Fase 1. |
| D-008 | Usar un menú interactivo de consola. | Coincide con el alcance local y de consola de la especificación. | La interfaz se implementa en una fase posterior; no habrá GUI. | Aceptada; implementación pendiente (Fase 5). |
| D-009 | Incluir los campos de auditoría `creada_en` y `cancelada_en`. | Conservar trazabilidad temporal de creación y cancelación. | El modelo y el esquema SQLite los incluirán; `cancelada_en` es nulo mientras la reserva está activa. | Aceptada; modelo definido en Fase 1, persistencia pendiente. |
| D-010 | Incluir posteriormente un mecanismo de reinicio de datos con confirmación explícita y advertencia de eliminación de reservas. | Evitar borrados accidentales del historial. | El mecanismo no forma parte de la Fase 1; deberá pedir confirmación y advertir que elimina reservas. | Aceptada; implementación pendiente. |
| D-011 | Usar identificadores y nombres de dominio en español. | Mantener coherencia con la especificación y los documentos del proyecto. | Clases, campos y mensajes usan términos como `Reserva`, `unidad_id`, `solicitante`, `inicio`, `fin`. | Aceptada; aplicada desde Fase 1. |
| D-012 | Usar exclusivamente la biblioteca estándar de Python 3.13. | Reproducibilidad sin instalación de paquetes ni acceso a red. | Se usan `unittest`, `sqlite3`, `json`, `datetime`, `re`, `enum` y `dataclasses`; no se instalan dependencias. | Aceptada; aplicada desde Fase 1. |

## Cambios posteriores

Agregar fecha, decisión, motivo, alternativas, efecto y commit real asociado cuando ocurra.
