# Registro de verificaciones

Este documento registra las pruebas ejecutadas durante el desarrollo del sistema de reservas, diferenciando los resultados informados por OpenCode de las verificaciones realizadas por el responsable del proyecto.

> **Nota de lectura (Etapa 5):** se conservan las entradas históricas con sus resultados originales. Las filas que figuraban como «Pendiente» al cierre de la Fase 1 se completaron en fases posteriores y aquí se actualizan con referencia a la sección donde está el resultado real. En la Etapa 5 no se ejecutó una nueva suite ni se agregaron resultados de pruebas.

## 0. Resumen de resultados y origen

La siguiente tabla separa el resultado **informado por OpenCode** —según lo registrado en [`docs/delegaciones.md`](delegaciones.md)— de la **ejecución humana independiente**, que es la evidencia principal conservada en este documento.

| Fase | Informado por OpenCode | Verificación humana independiente | Resultado conservado |
|---|---|---|---|
| Fase 1 | 44 pruebas, sin errores | 44 pruebas `OK`, `Ran 44 tests in 0.026s` | 44 |
| Fase 2 | 67 pruebas, sin errores | 67 pruebas `OK`, `Ran 67 tests in 0.513s` | 67 |
| Fase 3 | 84 pruebas, sin errores | 84 pruebas `OK`, `Ran 84 tests in 0.913s` | 84 |
| Fase 4 | 99 pruebas, sin errores | 99 pruebas `OK`, `Ran 99 tests in 1.322s` | 99 |
| Persistencia | No aplica como suite | Verificación manual de una reserva activa y una cancelada | Verificado |

No se conserva un archivo crudo de esas ejecuciones ni una transcripción de las sesiones manuales. La propuesta de archivos que podrían adjuntarse está en [`docs/evidencias/README.md`](evidencias/README.md).

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
| 31/10/2026 | Fase 2 (`4f0883f`) | Pruebas de SQLite, disponibilidad y superposición | Cumplimiento de reglas de reservas | Completado: 67 pruebas aprobadas; ver «Verificación humana — Fase 2» | Cubierto |
| 31/10/2026 | Fase 3 (`e30b654`) | Pruebas de cancelación | Conservar historial y liberar horario | Completado: 84 pruebas aprobadas; ver «Verificación humana — Fase 3» | Cubierto |
| 31/10/2026 | Fase 3 y verificaciones manuales | Reiniciar la aplicación sin borrar la base de datos | Recuperar reservas activas y canceladas | Completado: pruebas de cierre/reapertura y verificaciones manuales de persistencia | Cubierto |

## 2. Separación entre resultados informados por OpenCode y verificación humana

La sección 0 resume las cuatro fases. Esta sección conserva el detalle histórico de la Fase 1 y el criterio general de separación: un resultado informado por el agente no se considera aprobado hasta que el responsable lo ejecuta y lo confirma.

### 2.1 Fase 1 (detalle histórico)

**OpenCode informó:**
- Creación de siete archivos correspondientes a la Fase 1.
- Ejecución de 44 pruebas automáticas.
- Resultado satisfactorio sin errores.

**Verificación humana realizada:**
- Ejecución independiente del comando de pruebas desde Visual Studio Code.
- Confirmación de 44 pruebas aprobadas.
- Comprobación del estado del repositorio mediante Git.

Al 31/10/2026 no se había realizado una revisión humana línea por línea del código fuente. En la Etapa 5 el agente releyó los módulos y las pruebas para contrastar la documentación con el comportamiento real; esa relectura no reemplaza una revisión humana formal.

### 2.2 Fases 2 a 4

- **OpenCode informó:** 67, 84 y 99 pruebas aprobadas, respectivamente, según [`docs/delegaciones.md`](delegaciones.md).
- **Verificación humana:** el responsable ejecutó independientemente cada suite y obtuvo los resultados que se conservan en las secciones «Verificación humana — Fase 2», «Verificación humana — Fase 3» y «Verificación humana — Suite completa de la Fase 4».
- **Verificación manual adicional:** sesiones con `py -3.13 -m reservas` para comprobar la persistencia de una reserva cancelada y de una reserva activa.

La aprobación se basa en la ejecución humana, no en el informe del agente.

## 3. Verificaciones pendientes al cierre de la Fase 1 (histórico)

En las siguientes fases será necesario comprobar:

- Disponibilidad y superposición de reservas activas.
- Aceptación de horarios consecutivos.
- Reservas simultáneas de equipos diferentes.
- Validación de entradas incorrectas.
- Cancelación sin eliminación de registros.
- Persistencia de reservas activas y canceladas entre reinicios.

Todos los resultados futuros deberán registrarse con el comando ejecutado, resultado esperado, resultado observado y estado real. No se considerarán aprobadas pruebas que todavía no fueron ejecutadas.

**Estado al cierre de la Etapa 5:** los puntos anteriores quedaron cubiertos por las fases 2 a 4 y por las verificaciones manuales:

- Disponibilidad, superposición, consecutivos y unidades distintas: «Verificación humana — Fase 2» y «Verificación humana — Fase 3».
- Validación de entradas incorrectas: «Verificación humana — Fase 3» y pruebas de `tests/test_cli.py`.
- Cancelación sin eliminación de registros: «Verificación humana — Fase 3» y «Verificación manual — Cancelación y persistencia».
- Persistencia de reservas activas y canceladas entre reinicios: «Verificación manual — Persistencia de reserva activa» y «Verificación humana — Suite completa de la Fase 4».

La cobertura es automática y manual según se indica; no todos los casos se probaron manualmente sobre la base real.

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

**Pendiente al momento de esa verificación:** verificar del mismo modo una reserva activa y registrar la ejecución independiente de la suite completa de 99 pruebas.

**Actualización (Etapa 5):** ambos puntos quedaron completados. La reserva activa se verificó en «Verificación manual — Persistencia de reserva activa» y la suite de 99 pruebas se registra en «Verificación humana — Suite completa de la Fase 4».

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

## Revisión documental — Etapa 5 (31/10/2026)

**Objetivo:** contrastar el README y los documentos de evidencia con el código, las pruebas y los commits reales, sin modificar el comportamiento del sistema.

**Alcance revisado:**
- `README.md`, `AGENTS.md`, `docs/especificacion.md`, `docs/agente.md`, `docs/decisiones.md`, `docs/delegaciones.md` y `docs/verificaciones.md`.
- Todos los módulos de `reservas/` y todos los archivos de `tests/`.
- Historial de commits con `git log`, `git show --stat` y estado del árbol con `git status --short`.

**Acciones realizadas:**
- Se contrastaron los requisitos RF-01 a RF-10 con la implementación y las pruebas.
- Se corrigieron referencias desactualizadas: la Fase 1 ya no figura como «pendiente» en los puntos que se completaron en las fases 2 a 4.
- Se agregó la trazabilidad de los commits `4ee5936`, `39a9dd1`, `4f0883f`, `b4de875`, `e30b654` y `2c0869e`.
- Se actualizaron `README.md`, `docs/agente.md`, `docs/decisiones.md`, `docs/delegaciones.md` y `docs/verificaciones.md`.

**Resultados conservados:** 44 pruebas en Fase 1, 67 en Fase 2, 84 en Fase 3 y 99 en Fase 4; verificación manual de persistencia de una reserva cancelada y de una reserva activa.

**No realizado en esta etapa:**
- No se ejecutó nuevamente la suite de pruebas; se conservan los resultados reales registrados en las secciones anteriores.
- No se modificó código, pruebas, `AGENTS.md` ni inventario.
- No se realizó commit ni push.
- No se probó manualmente el reinicio destructivo sobre la base real; solo está cubierto por pruebas con bases temporales.
- No se ejecutó un clon limpio desde cero para validar el procedimiento del README.

**Estado:** cambios documentales pendientes de revisión humana.

## Ajuste documental final (31/10/2026)

**Objetivo:** ordenar la evidencia y reforzar la separación entre resultados informados por OpenCode y ejecuciones humanas, sin agregar pruebas ni resultados nuevos.

**Cambios realizados:**
- Se agregó la sección 0 con el resumen de resultados y su origen.
- Se renombró la sección 2 para explicitar la separación entre el informe del agente y la verificación humana.
- Se conservaron los resultados históricos: 44, 67, 84 y 99 pruebas, más las verificaciones manuales de persistencia.
- Se enlazó la propuesta de evidencias crudas en [`docs/evidencias/README.md`](evidencias/README.md).

**No realizado:**
- No se ejecutó una nueva suite de pruebas.
- No se modificó código, pruebas, `AGENTS.md` ni inventario.
- No se realizó commit ni push.

**Estado:** cambios documentales pendientes de revisión humana.

## Verificación final de la suite completa — 31/10/2026

**Objetivo:** comprobar que la aplicación mantiene su funcionamiento después de las revisiones documentales de la Etapa 5.

**Entorno:** Windows, Python 3.13.7.

**Commit de código utilizado:** `2c0869e`, con modificaciones documentales locales todavía no incorporadas a Git.

**Comando ejecutado manualmente:**

`py -3.13 -m unittest discover -s tests -v`

**Resultado observado:**

```text
Ran 99 tests in 1.437s

OK
```

Se aprobaron las 99 pruebas automáticas sin fallos ni errores.

**Conclusión:** la suite completa mantiene un resultado satisfactorio después de las modificaciones documentales.

**Estado: APROBADO.**

## Verificación de reproducibilidad desde un clon limpio — 31/10/2026

**Objetivo:** comprobar que el sistema puede descargarse desde GitHub y ejecutarse sin la cuenta ni las herramientas del agente de IA.

**Entorno:** Windows, Python 3.13.7.

**Repositorio:** https://github.com/Luciana2002/laboratorio-reservas

**Versión probada:** commit `2c0869e` (versión publicada antes del commit final de documentación).

### Procedimiento ejecutado

Se abrió una terminal nueva y se ejecutaron los siguientes comandos:

```cmd
cd /d D:\
git clone https://github.com/Luciana2002/laboratorio-reservas.git laboratorio-reservas-prueba
cd laboratorio-reservas-prueba
py -3.13 -m unittest discover -s tests -v
```

**Resultado observado:**

```text
Ran 99 tests in 1.426s

OK
```

Las 99 pruebas finalizaron correctamente, sin fallos ni errores.

### Ejecución de la aplicación

Se ejecutó:

`py -3.13 -m reservas`

Se seleccionó la opción `1` (Ver inventario).

El sistema mostró correctamente:

```text
MIC-01  Microscopio digital
MIC-02  Microscopio digital
OSC-01  Osciloscopio
MUL-01  Multímetro
FUE-01  Fuente de alimentación
```

Posteriormente se seleccionó `0` y la aplicación finalizó normalmente, mostrando `Hasta luego.`

### Conclusión

El sistema pudo clonarse, ejecutar las 99 pruebas automáticas y abrir la aplicación de consola desde una carpeta independiente, sin utilizar OpenCode ni instalar dependencias externas.

**Estado: APROBADO.**