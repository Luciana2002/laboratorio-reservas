# Registro de verificaciones

Este documento registra las pruebas ejecutadas durante el desarrollo del sistema de reservas, diferenciando los resultados informados por OpenCode de las verificaciones realizadas por el responsable del proyecto.

## 1. Verificación humana — Fase 1 (31/10/2026)

**Entorno utilizado:**
- Sistema operativo: Windows.
- Python: 3.13.7.
- Agente de programación: OpenCode 2.0.10.
- Commit inicial: `4ee5936`.

**Comando ejecutado manualmente:**

`py -3.13 -m unittest discover -s tests -v`

**Resultado observado:**

```text
Ran 44 tests in 0.026s

OK
```

Las 44 pruebas finalizaron correctamente, sin fallos ni errores.

### Tabla de verificaciones

| Fecha | Versión/commit | Comando o procedimiento | Resultado esperado | Resultado observado | Estado |
|---|---|---|---|---|---|
| 31/10/2026 | Posterior a `4ee5936`, sin commit aún | `py -3.13 -m unittest discover -s tests -v` | Aprobar las pruebas de inventario, fechas, intervalos y modelos | 44 pruebas aprobadas, 0 fallos | Aprobado |
| 31/10/2026 | Posterior a `4ee5936`, sin commit aún | `git status` | Identificar los archivos modificados y creados | 2 archivos modificados y 2 carpetas nuevas sin seguimiento | Verificado |
| 31/10/2026 | Posterior a `4ee5936`, sin commit aún | `git diff --stat` | Identificar los cambios en archivos versionados | 2 documentos modificados; los archivos nuevos aún no figuran | Verificado |
| Pendiente | Pendiente | Pruebas de SQLite, disponibilidad y superposición | Cumplimiento de reglas de reservas | No ejecutado | Pendiente |
| Pendiente | Pendiente | Pruebas de cancelación | Conservar historial y liberar horario | No ejecutado | Pendiente |
| Pendiente | Pendiente | Reiniciar la aplicación sin borrar la base de datos | Recuperar reservas activas y canceladas | No ejecutado | Pendiente |

## 2. Diferencia entre agente y verificación humana

**OpenCode informó:**
- Creación de siete archivos correspondientes a la Fase 1.
- Ejecución de 44 pruebas automáticas.
- Resultado satisfactorio sin errores.

**Verificación humana realizada:**
- Ejecución independiente del comando de pruebas desde Visual Studio Code.
- Confirmación de 44 pruebas aprobadas.
- Comprobación del estado del repositorio mediante Git.

No se realizó todavía una revisión completa del código fuente.

## 3. Verificaciones pendientes

En las siguientes fases será necesario comprobar:

- Disponibilidad y superposición de reservas activas.
- Aceptación de horarios consecutivos.
- Reservas simultáneas de equipos diferentes.
- Validación de entradas incorrectas.
- Cancelación sin eliminación de registros.
- Persistencia de reservas activas y canceladas entre reinicios.

Todos los resultados futuros deberán registrarse con el comando ejecutado, resultado esperado, resultado observado y estado real. No se considerarán aprobadas pruebas que todavía no fueron ejecutadas.

## Verificación humana — Fase 2 (31/10/2026)

**Objetivo:** verificar el funcionamiento de SQLite, la persistencia de reservas y la detección de conflictos entre horarios.

**Entorno utilizado:**
- Sistema operativo: Windows.
- Python: 3.13.7.
- Agente: OpenCode 2.0.10.
- Commit de partida: `39a9dd1`.

**Comando ejecutado manualmente:**

`py -3.13 -m unittest discover -s tests -v`

**Resultado observado:**

```text
Ran 67 tests in 0.513s

OK
```

Se ejecutaron correctamente 67 pruebas automáticas, incluyendo las 44 de la Fase 1 y 23 nuevas correspondientes a la Fase 2.

### Funcionalidades verificadas

- Detección de reservas superpuestas.
- Aceptación de horarios consecutivos.
- Reservas simultáneas de unidades diferentes.
- Reservas canceladas que no bloquean horarios.
- Almacenamiento y recuperación de reservas mediante SQLite.
- Conservación de datos al cerrar y reabrir la conexión.
- Rechazo de identificadores duplicados.

### Verificación del repositorio

Se ejecutaron `git status` y `git diff --stat`.

Se identificaron cuatro archivos nuevos:
- `reservas/db.py`
- `reservas/repositorio.py`
- `tests/test_conflictos.py`
- `tests/test_repositorio.py`

**Resultado de la revisión humana:** se aceptan los resultados de las pruebas ejecutadas. Queda pendiente la integración del servicio y una revisión completa del código fuente.

**Estado:** aprobado en las pruebas ejecutadas.

## Verificación humana — Fase 3 (31/10/2026)

**Objetivo:** comprobar las funcionalidades de creación, disponibilidad, cancelación e historial de reservas.

**Entorno utilizado:**
- Sistema operativo: Windows.
- Python: 3.13.7.
- Agente: OpenCode 2.0.10.
- Commit de partida: `b4de875`.

**Comando ejecutado manualmente:**

`py -3.13 -m unittest discover -s tests -v`

**Resultado observado:**

```text
Ran 84 tests in 0.913s

OK
```

Se ejecutaron correctamente 84 pruebas automáticas, incluidas las 67 anteriores y 17 nuevas.

### Funcionalidades comprobadas

- Creación de reservas válidas con UUID.
- Rechazo de unidades inexistentes y solicitantes inválidos.
- Validación de fechas y horarios.
- Rechazo de reservas superpuestas.
- Aceptación de horarios consecutivos y equipos diferentes.
- Consulta de disponibilidad antes y después de reservar.
- Cancelación conservando los datos originales.
- Liberación del horario después de cancelar.
- Historial de reservas activas y canceladas.
- Persistencia al cerrar y reabrir una conexión SQLite.

### Verificación del repositorio

Se ejecutaron `git status` y `git diff --stat`.

Archivos identificados:
- `reservas/servicio.py` (nuevo).
- `tests/test_servicio.py` (nuevo).
- `reservas/repositorio.py` (modificado).

**Decisión humana:** aceptar los resultados de la Fase 3 porque las 84 pruebas ejecutadas finalizaron sin errores.

**Limitaciones:** todavía no se verificó el funcionamiento de la aplicación mediante una interfaz de consola ni su persistencia entre procesos independientes.

**Estado:** aprobado en las pruebas ejecutadas.

## Verificación manual — Cancelación y persistencia (31/10/2026)

**Aplicación:** sistema de reservas de laboratorio.

**Comando:** `py -3.13 -m reservas`

**Procedimiento ejecutado:**

1. Se canceló la reserva `6403fb27-785b-44a0-bff7-c1bd7046eaf7`, correspondiente a `MIC-01`, solicitante ficticio Juan Pérez, intervalo `2026-11-02 10:00` a `11:00`.
2. El sistema confirmó la cancelación.
3. Se consultó la disponibilidad del mismo equipo e intervalo.
4. El sistema informó que el horario estaba disponible.
5. Se consultó el historial y se comprobó que la reserva seguía registrada con estado `cancelada`.
6. Se cerró la aplicación utilizando la opción `0`.
7. Se volvió a ejecutar la aplicación.
8. Se consultó nuevamente el historial y la reserva cancelada continuaba registrada, con el mismo identificador y datos.

**Resultado esperado:** la cancelación libera el horario sin eliminar el registro y el estado persiste después de cerrar y reabrir la aplicación.

**Resultado observado:** comportamiento coincidente con el esperado.

**Estado:** APROBADO.

**Pendiente:** verificar del mismo modo una reserva activa y registrar la ejecución independiente de la suite completa de 99 pruebas.

## Verificación manual — Persistencia de reserva activa (31/10/2026)

**Objetivo:** comprobar que una reserva activa se conserva después de cerrar y volver a ejecutar la aplicación.

**Entorno utilizado:**
- Sistema operativo: Windows.
- Python: 3.13.7.
- Aplicación: sistema de reservas de laboratorio.
- Commit de partida: `e30b654`.

**Comando ejecutado:**

`py -3.13 -m reservas`

### Procedimiento realizado

1. Se inició la aplicación desde la terminal.
2. Se seleccionó la opción `3` (Crear una reserva).
3. Se ingresaron los siguientes datos:
   - Unidad: `OSC-01`.
   - Solicitante ficticio: Lucía Fernández.
   - Inicio: `2026-11-03 14:00`.
   - Fin: `2026-11-03 15:00`.
4. El sistema creó correctamente la reserva con ID `c144c33b-f463-4bb6-9443-86a3c4e6e5ee`.
5. Se cerró la aplicación mediante la opción `0`.
6. Se volvió a ejecutar `py -3.13 -m reservas`.
7. Se seleccionó la opción `5` (Ver reservas activas).
8. Se comprobó que la reserva continuaba registrada con el mismo identificador, unidad, solicitante, horario y estado `activa`.

### Resultado esperado

La reserva debe permanecer almacenada en SQLite después de cerrar y volver a iniciar la aplicación, sin perder ni modificar sus datos.

### Resultado observado

El sistema recuperó correctamente la reserva activa:

```text
ID: c144c33b-f463-4bb6-9443-86a3c4e6e5ee
Unidad: OSC-01
Solicitante: Lucía Fernández
Inicio: 2026-11-03 14:00
Fin: 2026-11-03 15:00
Estado: activa
```

**Estado: APROBADO.**

La prueba confirma la persistencia de una reserva activa entre dos ejecuciones independientes de la aplicación.

## Verificación humana — Suite completa de la Fase 4 (31/10/2026)

**Objetivo:** comprobar que la interfaz de consola funciona sin afectar las funcionalidades implementadas en las fases anteriores.

**Entorno utilizado:**
- Sistema operativo: Windows.
- Python: 3.13.7.
- OpenCode: 2.0.10.
- Commit de partida: `e30b654`.

**Comando ejecutado manualmente:**

`py -3.13 -m unittest discover -s tests -v`

**Resultado observado:**

```text
Ran 99 tests in 1.322s

OK
```

**Pruebas verificadas:**
- 15 pruebas automáticas de la interfaz de consola.
- 84 pruebas de las fases anteriores.
- Creación y cancelación de reservas.
- Rechazo de superposiciones.
- Consulta de disponibilidad.
- Historial de reservas.
- Reinicio de datos con confirmación, mediante pruebas automatizadas con bases temporales.
- Persistencia entre ejecuciones independientes.

**Verificación de Git:**

Se ejecutaron `git status` y `git diff --stat`.

Se observaron los siguientes cambios:
- `reservas/cli.py` (nuevo).
- `reservas/__main__.py` (nuevo).
- `tests/test_cli.py` (nuevo).
- `docs/verificaciones.md` (modificado).

**Decisión humana:** aceptar los resultados de la Fase 4, porque las 99 pruebas finalizaron correctamente. Se realizaron además verificaciones manuales de creación, superposición, cancelación y persistencia de reservas activas y canceladas, documentadas anteriormente.

**Limitaciones:** no se realizó una inspección completa del código fuente; el reinicio destructivo no se probó manualmente sobre la base real.

**Estado:** APROBADO.