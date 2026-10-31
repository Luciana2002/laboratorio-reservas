# Registro de decisiones

Este documento conserva las decisiones de diseño y su estado real. Cuando una decisión se implementó, se indica el commit o los archivos que la respaldan; no se marca como implementada una decisión sin evidencia.

## D-001 — Diseño inicial propuesto (antes de implementación)

- **Decisión:** sistema local de consola en Python con SQLite y biblioteca estándar.
- **Motivo:** reproducibilidad, bajo costo y persistencia sin servicios externos.
- **Alternativas:** API local / almacenamiento JSON; se prefiere consola + SQLite por simplicidad y manejo transaccional.
- **Consecuencia:** no habrá interfaz gráfica; será necesario documentar comandos.
- **Estado:** aceptada e implementada en las fases 1 a 4 (commits `39a9dd1`, `4f0883f`, `e30b654` y `2c0869e`).

## D-002 — Intervalos semiabiertos

- **Decisión:** `[inicio, fin)`; los límites consecutivos se permiten.
- **Motivo:** refleja explícitamente la regla de la consigna.
- **Consecuencia:** el conflicto se detecta con comparaciones estrictas.
- **Estado:** aceptada e implementada en la Fase 2 (commit `4f0883f`).
- **Evidencia:** `reservas/tiempo.py`, `reservas/repositorio.py`, `tests/test_conflictos.py`, `tests/test_servicio.py`.

## D-003 — Fechas pasadas y límites

- **Decisión:** permitir fechas pasadas, sin límite adicional de duración o anticipación.
- **Motivo:** la consigna deja la política abierta y así los escenarios de prueba son reproducibles.
- **Consecuencia:** uso educativo, no una política de reservas reales de un laboratorio.
- **Estado:** aceptada; comportamiento vigente. El código no rechaza fechas pasadas.

## D-004 a D-012 — Decisiones técnicas aceptadas para la implementación (2026-10-31)

| ID | Decisión | Motivo | Consecuencia | Estado actual |
|---|---|---|---|---|
| D-004 | Usar una base SQLite local en `data/reservas.db`. | Persistencia transaccional sin servicios externos y con un archivo ignorado por Git. | La base no se versiona; las pruebas usan bases temporales. | Implementada en la Fase 2 (`4f0883f`); ruta por defecto en `reservas/db.py`. |
| D-005 | Exigir el formato estricto `AAAA-MM-DD HH:MM` (24 horas). | Evitar ambigüedades y validar fechas reales. | Se combinan regex estricta y `datetime.strptime`; se rechazan variantes sin ceros. | Implementada en la Fase 1 (`39a9dd1`). |
| D-006 | Interpretar las fechas como hora local de `America/Argentina/Buenos_Aires`, usando `datetime` naive. | Evitar depender de `tzdata`, que no forma parte de la biblioteca estándar en Windows. | No se aceptan zonas por reserva; no se reproducen cambios históricos de horario de verano. | Implementada y documentada en `reservas/tiempo.py` desde la Fase 1 (`39a9dd1`). |
| D-007 | Comparar los identificadores de unidad de forma exacta y sensible a mayúsculas. | Los IDs del inventario son códigos fijos y distintos entre sí. | `mic-01` no se considera una unidad conocida. | Implementada en la Fase 1 (`39a9dd1`). |
| D-008 | Usar un menú interactivo de consola. | Coincide con el alcance local y de consola de la especificación. | La interfaz se implementó en la Fase 4; no hay GUI. | Implementada en `reservas/cli.py` (commit `2c0869e`). |
| D-009 | Incluir los campos de auditoría `creada_en` y `cancelada_en`. | Conservar trazabilidad temporal de creación y cancelación. | El modelo y el esquema SQLite los incluyen; `cancelada_en` es nulo mientras la reserva está activa. | Implementada: modelo en Fase 1 (`39a9dd1`), persistencia en Fase 2 (`4f0883f`) y cancelación en Fase 3 (`e30b654`). |
| D-010 | Incluir un mecanismo de reinicio de datos con confirmación explícita y advertencia de eliminación de reservas. | Evitar borrados accidentales del historial. | El mecanismo pide confirmación, advierte que elimina reservas y no toca el inventario. | Implementada en la Fase 4 (`2c0869e`), opción 7 del menú. |
| D-011 | Usar identificadores y nombres de dominio en español. | Mantener coherencia con la especificación y los documentos del proyecto. | Clases, campos y mensajes usan términos como `Reserva`, `unidad_id`, `solicitante`, `inicio`, `fin`. | Aplicada desde la Fase 1 (`39a9dd1`). |
| D-012 | Usar exclusivamente la biblioteca estándar de Python 3.13. | Reproducibilidad sin instalación de paquetes ni acceso a red. | Se usan `unittest`, `sqlite3`, `json`, `datetime`, `re`, `enum`, `dataclasses`, `argparse` y `uuid`; no se instalan dependencias. | Aplicada desde la Fase 1 (`39a9dd1`); verificada en las fases 2 a 4. |

## D-013 — Inserción atómica y regla de conflicto compartida (Fase 2)

- **Decisión:** `hay_conflicto()` consulta `unidad_id = ? AND estado = 'activa' AND inicio < ? AND fin > ?`; `insertar_si_libre()` usa `BEGIN IMMEDIATE` cuando la conexión no tiene una transacción abierta y devuelve `True`/`False`.
- **Motivo:** evitar condiciones de carrera entre la comprobación y la inserción, y no duplicar la regla de superposición.
- **Consecuencia:** disponibilidad y creación comparten la misma función; si el llamador ya abrió una transacción, el commit o rollback queda a su cargo.
- **Evidencia:** `reservas/repositorio.py`, `tests/test_conflictos.py`.
- **Commit:** `4f0883f`.

## D-014 — Cancelación idempotente sin borrado (Fase 3)

- **Decisión:** `marcar_cancelada()` actualiza únicamente `estado` y `cancelada_en` con `WHERE id = ? AND estado = 'activa'`. Un ID inexistente lanza `ReservaNoEncontrada`; una reserva ya cancelada devuelve `ResultadoCancelacion(cancelada_ahora=False)` sin cambios.
- **Motivo:** conservar el historial y evitar dobles cancelaciones con efectos laterales.
- **Consecuencia:** no se borra el registro ni se alteran ID, unidad, solicitante, inicio, fin ni `creada_en`.
- **Evidencia:** `reservas/servicio.py`, `reservas/repositorio.py`, `tests/test_servicio.py`.
- **Commit:** `e30b654`.

## D-015 — Servicio centralizado y UUID (Fase 3)

- **Decisión:** `ServicioReservas` centraliza disponibilidad, creación, cancelación e historial; genera UUID4 y reutiliza inventario, tiempo y repositorio.
- **Motivo:** separar la lógica de negocio de la consola y no duplicar validaciones.
- **Consecuencia:** la CLI es delgada; los errores de negocio son excepciones tipadas (`UnidadInexistente`, `SolicitanteInvalido`, `ConflictoReserva`, `ReservaNoEncontrada`).
- **Evidencia:** `reservas/servicio.py`, `tests/test_servicio.py`.
- **Commit:** `e30b654`.

## D-016 — Consola con entrada/salida inyectables y `--db` opcional (Fase 4)

- **Decisión:** `main(argv, entrada=..., salida=...)` permite probar la consola sin subprocesos; `--db` permite elegir una base distinta de `data/reservas.db`. Los errores de dominio y SQLite se informan y vuelven al menú; el fin de entrada termina con código 0.
- **Motivo:** facilitar pruebas con bases temporales y no tocar la base real.
- **Consecuencia:** las pruebas usan `StringIO` y `TemporaryDirectory`; un test de subproceso verifica `python -m reservas`.
- **Evidencia:** `reservas/cli.py`, `reservas/__main__.py`, `tests/test_cli.py`.
- **Commit:** `2c0869e`.

## D-017 — Reinicio destructivo con confirmación exacta (Fase 4)

- **Decisión:** la opción 7 advierte que se eliminarán todas las reservas activas y canceladas, incluido el historial; exige escribir exactamente `REINICIAR`; ejecuta `DELETE FROM reservas` dentro de una transacción y no modifica el inventario.
- **Motivo:** cumplir el requisito de reinicio sin borrados accidentales.
- **Consecuencia:** el reinicio es irreversible y no crea respaldo automático; la base sigue funcional. Se probó con bases temporales, no manualmente sobre la base real.
- **Evidencia:** `reservas/cli.py`, `tests/test_cli.py`.
- **Commit:** `2c0869e`.

## D-018 — Revisión documental de la Etapa 5 (sin commit)

- **Decisión:** contrastar README y documentos de evidencia con el código y los commits reales; actualizar únicamente `README.md`, `docs/agente.md`, `docs/decisiones.md`, `docs/delegaciones.md` y `docs/verificaciones.md`.
- **Motivo:** preparar la entrega y eliminar afirmaciones desactualizadas sin alterar el comportamiento del sistema.
- **Consecuencia:** no se modifica código, pruebas, `AGENTS.md` ni inventario; no se ejecuta una nueva suite en esta etapa; los cambios quedan pendientes de revisión humana y commit.
- **Estado:** propuesta de cierre; pendiente de aceptación humana.

## Trazabilidad de commits

| Commit | Fecha | Contenido | Episodio / fase |
|---|---|---|---|
| `4ee5936` | 2026-10-31 | Especificación inicial, `AGENTS.md`, inventario y documentos base. | Episodio 1 (análisis) |
| `39a9dd1` | 2026-10-31 | Fase 1: inventario, validaciones, fechas, modelos y 44 pruebas. | Episodio 1 (Fase 1 autorizada) |
| `4f0883f` | 2026-10-31 | Fase 2: SQLite, repositorio, conflictos y 67 pruebas. | Episodio 2 |
| `b4de875` | 2026-10-31 | Documentación de la Fase 2. | Episodio 2 |
| `e30b654` | 2026-10-31 | Fase 3: servicio, cancelación y 84 pruebas. | Episodio 3 |
| `2c0869e` | 2026-10-31 | Fase 4: interfaz de consola y 99 pruebas. | Episodio 4 |

Los cambios de la Etapa 5 no tienen commit todavía. Las decisiones humanas y las acciones del agente se detallan en [`delegaciones.md`](delegaciones.md); los comandos y resultados reales, en [`verificaciones.md`](verificaciones.md).
