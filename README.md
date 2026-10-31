# Sistema local de reservas de laboratorio

Proyecto individual del Challenge IA. Estado: **implementado y verificado** en Windows con Python 3.13.7. La última suite registrada tiene **99 pruebas automáticas aprobadas** y se realizaron verificaciones manuales de persistencia de reservas activas y canceladas. Véanse [verificaciones](docs/verificaciones.md) y [delegaciones](docs/delegaciones.md).

## 1. Especificación breve

### Problema

Un laboratorio con cinco unidades físicas necesita registrar reservas sin permitir que dos reservas activas se superpongan sobre la misma unidad. Al cancelar una reserva, el horario debe quedar libre, pero el registro no debe borrarse: debe conservarse el historial con sus datos originales.

### Alcance

- Aplicación **local de consola**, sin servicios de nube ni interfaz gráfica.
- Python 3.13 y **exclusivamente biblioteca estándar**; SQLite para persistencia.
- Inventario fijo de cinco unidades, definido en [`data/inventario.json`](data/inventario.json) y de solo lectura.
- Una unidad física por reserva; el solicitante es un nombre ficticio.
- Sin autenticación, roles reales, pagos, notificaciones, administración de inventario ni concurrencia distribuida.

### Reglas

- Una reserva ocupa el intervalo semiabierto `[inicio, fin)`.
- Solo las reservas **activas** bloquean horarios; las canceladas no.
- Dos reservas activas de la **misma unidad** se superponen si `inicio_nuevo < fin_existente` **y** `fin_nuevo > inicio_existente`.
- Límites iguales son **consecutivos**, no superpuestos: `10:00–11:00` y `11:00–12:00` pueden coexistir.
- Reservas de **unidades distintas** no entran en conflicto, aunque coincidan en horario.
- La consulta de disponibilidad y la creación de reservas usan la **misma regla de conflicto**.
- Cancelar conserva identificador, unidad, solicitante, inicio, fin y fecha de creación; solo cambia el estado y registra la fecha de cancelación.
- Se valida unidad conocida, solicitante no vacío ni compuesto solo por espacios, fecha/hora válida e `inicio < fin`.
- Los registros y estados se guardan en SQLite y sobreviven al cierre y reinicio de la aplicación.

### Criterios de aceptación

| ID | Requisito | Criterio verificable | Evidencia |
|---|---|---|---|
| RF-01 | Listar inventario | Se muestran exactamente las 5 unidades precargadas. | `tests/test_inventario.py`, `tests/test_cli.py` |
| RF-02 | Consultar disponibilidad | Dada unidad e intervalo válidos, se informa libre/ocupado según las reservas activas. | `tests/test_servicio.py`, `tests/test_cli.py` |
| RF-03 | Crear reserva | Se genera un UUID único y se conservan unidad, solicitante, inicio, fin y estado activo. | `tests/test_servicio.py`, `tests/test_cli.py` |
| RF-04 | Evitar conflicto | Con `MIC-01` ocupado `10:00–11:00`, se rechaza `MIC-01 10:30–11:30`. | `tests/test_conflictos.py`, `tests/test_servicio.py` |
| RF-05 | Permitir consecutivas | Con `MIC-01` ocupado `10:00–11:00`, se acepta `MIC-01 11:00–12:00`. | `tests/test_conflictos.py`, `tests/test_servicio.py` |
| RF-06 | Independencia entre unidades | `MIC-02` se puede reservar en el mismo horario que `MIC-01`. | `tests/test_conflictos.py`, `tests/test_servicio.py` |
| RF-07 | Cancelar sin borrar | La reserva conserva sus datos, pasa a `cancelada` y el intervalo queda libre. | `tests/test_servicio.py`, `tests/test_cli.py` |
| RF-08 | Persistir | Tras cerrar y abrir la aplicación, reaparecen reservas activas y canceladas. | `tests/test_repositorio.py`, `tests/test_cli.py`, verificación manual |
| RF-09 | Rechazar inválidos | Se rechazan unidad inexistente, solicitante vacío o solo espacios, fecha/hora inválida e `inicio >= fin`. | `tests/test_inventario.py`, `tests/test_tiempo.py`, `tests/test_servicio.py`, `tests/test_cli.py` |
| RF-10 | Conservar historial | Se pueden consultar reservas activas y canceladas con sus datos. | `tests/test_servicio.py`, `tests/test_cli.py` |

La especificación completa, con supuestos y exclusiones, está en [`docs/especificacion.md`](docs/especificacion.md). La matriz que relaciona cada requisito con su implementación, sus pruebas y el resultado realmente verificado está en la [sección 4](#matriz-de-trazabilidad-rf-01-a-rf-10).

## 2. Solución

### Arquitectura

| Módulo | Responsabilidad |
|---|---|
| `reservas/inventario.py` | Carga y valida el inventario JSON; nunca lo modifica. |
| `reservas/tiempo.py` | Parseo y formato estricto `AAAA-MM-DD HH:MM`, validación `inicio < fin` y hora local de Buenos Aires. |
| `reservas/modelos.py` | Modelos `Unidad`, `EstadoReserva` y `Reserva`, con validaciones de dominio. |
| `reservas/db.py` | Conexión SQLite, esquema idempotente y ruta por defecto. |
| `reservas/repositorio.py` | Consultas SQL parametrizadas, detección de conflictos, inserción atómica, cancelación y listados. |
| `reservas/servicio.py` | Casos de uso: disponibilidad, creación, cancelación e historial. |
| `reservas/cli.py` | Menú interactivo y presentación por consola. |
| `reservas/__main__.py` | Punto de entrada para `python -m reservas`. |
| `tests/` | Pruebas automatizadas con `unittest` y bases SQLite temporales. |

### Estructura real del proyecto

```text
laboratorio-reservas/
├── AGENTS.md
├── README.md
├── data/
│   ├── inventario.json          # inventario fijo, versionado
│   └── reservas.db              # base local, ignorada por Git
├── docs/
│   ├── agente.md
│   ├── decisiones.md
│   ├── delegaciones.md
│   ├── especificacion.md
│   ├── verificaciones.md
│   └── evidencias/
│       └── README.md            # propuesta de evidencias reales
├── reservas/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── db.py
│   ├── inventario.py
│   ├── modelos.py
│   ├── repositorio.py
│   ├── servicio.py
│   └── tiempo.py
└── tests/
    ├── __init__.py
    ├── test_cli.py
    ├── test_conflictos.py
    ├── test_inventario.py
    ├── test_repositorio.py
    ├── test_servicio.py
    └── test_tiempo.py
```

No hay `requirements.txt`, `pyproject.toml` ni dependencias de terceros: el proyecto funciona con la biblioteca estándar.

### Requisitos previos y versiones

- **Python 3.13.x**. La verificación registrada usó **Python 3.13.7**.
- **Git** para clonar el repositorio.
- En Windows, el lanzador `py` permite seleccionar 3.13 con `py -3.13`.
- En Linux/macOS, usar `python3.13` o el comando `python3` que apunte a 3.13.
- **No se instala nada con `pip`**: SQLite y `unittest` forman parte de la biblioteca estándar.
- El desarrollo y las verificaciones registradas se hicieron en **Windows**; el diseño no depende de rutas absolutas ni de características exclusivas de Windows.

### Instalación y ejecución desde un clon nuevo

```bash
git clone https://github.com/Luciana2002/laboratorio-reservas.git
cd laboratorio-reservas
py -3.13 --version
```

No hay paso de instalación de dependencias. Ejecutar desde la raíz del repositorio para que Python encuentre el paquete `reservas`:

```bash
py -3.13 -m reservas
```

Alternativa multiplataforma:

```bash
python3.13 -m reservas
# o, si python3 apunta a 3.13:
python3 -m reservas
```

Para usar otra base SQLite (por ejemplo, una temporal) sin tocar la base normal:

```bash
py -3.13 -m reservas --db C:\ruta\alternativa.db
```

La aplicación resuelve la ruta del inventario y la base por defecto a partir de la ubicación del paquete, no del directorio desde el que se lanza el comando. Aun así, `python -m reservas` requiere ejecutarse desde la raíz del repositorio (o tener el paquete instalado/disponible en `sys.path`).

### Ejemplos de uso

Los identificadores UUID son ejemplos: cada ejecución genera uno nuevo.

```text
$ py -3.13 -m reservas
Sistema de reservas de laboratorio

1. Ver inventario.
2. Consultar disponibilidad.
3. Crear una reserva.
4. Cancelar una reserva.
5. Ver reservas activas.
6. Ver historial completo.
7. Reiniciar datos.
0. Salir.
Seleccione una opción: 1
Inventario:
  MIC-01  Microscopio digital
  MIC-02  Microscopio digital
  OSC-01  Osciloscopio
  MUL-01  Multímetro
  FUE-01  Fuente de alimentación
```

Crear una reserva:

```text
Seleccione una opción: 3
ID de unidad: MIC-01
Nombre ficticio del solicitante: Ada Lovelace
Inicio (AAAA-MM-DD HH:MM): 2026-11-02 09:00
Fin (AAAA-MM-DD HH:MM): 2026-11-02 10:00
Reserva creada correctamente.
ID: 4341f7ad-2dcf-48c6-b90b-83422b46e697
Unidad: MIC-01
Solicitante: Ada Lovelace
Inicio: 2026-11-02 09:00
Fin: 2026-11-02 10:00
Estado: activa
```

Consultar el mismo horario (ocupado) y cancelar:

```text
Seleccione una opción: 2
ID de unidad: MIC-01
Inicio (AAAA-MM-DD HH:MM): 2026-11-02 09:30
Fin (AAAA-MM-DD HH:MM): 2026-11-02 10:30
La unidad MIC-01 está ocupada de 2026-11-02 09:30 a 2026-11-02 10:30.

Seleccione una opción: 4
ID de la reserva: 4341f7ad-2dcf-48c6-b90b-83422b46e697
Reserva cancelada. El horario quedó libre.
ID: 4341f7ad-2dcf-48c6-b90b-83422b46e697
Unidad: MIC-01
Solicitante: Ada Lovelace
Inicio: 2026-11-02 09:00
Fin: 2026-11-02 10:00
Estado: cancelada
Cancelada en: 2026-10-31 19:00:00
```

Después de cancelar, la opción `2` informa que el horario está disponible y la opción `6` sigue mostrando la reserva en el historial con estado `cancelada`.

### Persistencia y ubicación de la base

- La base por defecto es **`data/reservas.db`**, creada automáticamente en la primera ejecución.
- El archivo está ignorado por Git mediante `*.db` en `.gitignore`; no se versiona.
- Al cerrar y volver a abrir la aplicación, se recuperan las reservas activas y canceladas con todos sus campos.
- Las pruebas usan directorios temporales y bases descartables; no tocan la base real.
- La verificación manual de persistencia está registrada en [`docs/verificaciones.md`](docs/verificaciones.md).
- `--db` permite elegir otra ubicación; la aplicación crea el directorio padre si falta.

### Reinicio de datos

La opción **7. Reiniciar datos** elimina **todas las reservas activas y canceladas, incluido el historial**. Antes de hacerlo:

1. Muestra una advertencia explícita.
2. Pide escribir exactamente `REINICIAR`.
3. Cualquier otra entrada (incluidos `NO`, `reiniciar` o ` REINICIAR `) cancela la operación sin modificar la base.
4. Si se confirma, ejecuta `DELETE FROM reservas` dentro de una transacción.
5. **No modifica el inventario**: `data/inventario.json` permanece intacto.
6. La base sigue siendo funcional después del reinicio y se pueden crear reservas nuevas.

**El reinicio es irreversible y no crea un respaldo automático.** La suite automatizada prueba la confirmación y el rechazo con bases temporales; no se ejecutó manualmente sobre la base real durante el desarrollo.

### Pruebas automatizadas

Desde la raíz del repositorio:

```bash
py -3.13 -m unittest discover -s tests -v
```

Alternativa multiplataforma:

```bash
python3.13 -m unittest discover -s tests -v
```

Resultado registrado en la última verificación de la Fase 4:

```text
Ran 99 tests in 1.322s

OK
```

El tiempo puede variar. La distribución es: 19 pruebas de inventario y modelos de unidad, 25 de fechas/intervalos/modelos, 15 de conflictos, 8 de repositorio, 17 de servicio y 15 de consola. La separación entre resultados informados por OpenCode y ejecuciones humanas independientes está en [`docs/verificaciones.md`](docs/verificaciones.md).

### Limitaciones y funcionalidades fuera de alcance

- Aplicación local para un solo usuario; no hay autenticación, roles, permisos por usuario, pagos, notificaciones, GUI ni despliegue.
- No se administra el inventario: es un archivo fijo de solo lectura.
- Las fechas son `datetime` naive en hora local de `America/Argentina/Buenos_Aires` (UTC-3). No se aceptan zonas horarias por reserva ni se reproducen cambios históricos de horario de verano.
- El formato es estricto: `AAAA-MM-DD HH:MM`, con ceros a la izquierda y sin segundos ni sufijos.
- Se permiten fechas pasadas; no hay límite de anticipación ni duración máxima, salvo `inicio < fin`.
- No hay migraciones versionadas del esquema: se usa `CREATE TABLE IF NOT EXISTS`.
- Los listados no tienen paginación ni orden configurable.
- En consolas de Windows con codificación limitada, los acentos pueden mostrarse incorrectamente; las pruebas de subproceso fuerzan `PYTHONIOENCODING=utf-8`.
- La atomicidad se apoya en transacciones SQLite (`BEGIN IMMEDIATE`); no se probó concurrencia entre múltiples procesos.
- El reinicio de datos es destructivo y no tiene respaldo automático.
- La revisión humana línea por línea del código fuente sigue pendiente; la Etapa 5 hizo una relectura para contrastar la documentación.

## 3. Preparación del agente

- **Agente:** **OpenCode 2.0.10**, verificado en la terminal con `opencode --version` → `opencode v2.0.10`.
- **Entorno:** Windows (Microsoft Windows NT 10.0.26200.0), Visual Studio Code y terminal PowerShell; **Python 3.13.7** (`py -3.13 --version`).
- **Modelo y proveedor:** el entorno de ejecución de esta sesión identifica el proveedor `opencode` y el modelo `big-pickle` (nombre visible «Big Pickle»). No hay un registro versionado por fase que permita afirmar que todos los episodios usaron exactamente ese modelo; por eso la afirmación se limita a la sesión actual. Para comprobarlo, usar el selector de modelo de OpenCode o `opencode models` para listar los identificadores disponibles.
- **Función y motivo de elección:** implementación asistida, revisión y ejecución de pruebas sobre un repositorio real, con revisión humana entre fases. Se eligió por su capacidad de operar sobre archivos del proyecto y conservar el historial en Git.
- **Instrucciones aplicadas:** las de [`AGENTS.md`](AGENTS.md), en particular intervalos `[inicio, fin)`, solo reservas activas bloquean, misma regla para disponibilidad y creación, persistencia SQLite, validaciones, ausencia de datos reales y control humano antes de comandos destructivos o commits.
- **Herramientas y permisos utilizados:** lectura, edición y escritura de archivos; comandos de shell para Git de solo lectura y ejecución de pruebas. No se instalaron dependencias, no se accedió a servicios externos, no se borraron datos reales y el agente no realizó commits ni push. No se identificó una configuración de permisos personalizada versionada; el control efectivo fue la autorización humana explícita y las restricciones de `AGENTS.md`.
- **Contexto suministrado:** consigna, especificación, inventario, código, pruebas y documentos del repositorio. **Contexto excluido:** secretos, credenciales, datos reales de estudiantes y chats privados.
- **Registro de decisiones y progreso:** [`docs/decisiones.md`](docs/decisiones.md), [`docs/delegaciones.md`](docs/delegaciones.md) y [`docs/verificaciones.md`](docs/verificaciones.md).

El detalle completo, con la distinción entre acciones del agente y decisiones humanas, está en [`docs/agente.md`](docs/agente.md).

## 4. Registro de decisiones y delegación

### Matriz de trazabilidad RF-01 a RF-10

La columna «Resultado verificado» distingue la suite automatizada de las verificaciones manuales. No implica que cada requisito se haya probado manualmente sobre la base real. Los resultados de la suite son los conservados en [`docs/verificaciones.md`](docs/verificaciones.md): 44 pruebas en Fase 1, 67 en Fase 2, 84 en Fase 3 y 99 en Fase 4.

Los archivos de implementación están en `reservas/` y los de prueba en `tests/`, salvo `data/inventario.json`. Cada fila tiene exactamente cinco columnas.

| RF | Implementación | Pruebas | Resultado verificado | Evidencia |
|---|---|---|---|---|
| RF-01 | `inventario.py`; `cli.py`; `inventario.json` | `test_inventario.py`; `test_cli.py` | Se muestran exactamente las 5 unidades; suite de 99 pruebas OK. | `39a9dd1`, `2c0869e`; [ver](docs/verificaciones.md) |
| RF-02 | `servicio.py`; `repositorio.py`; `cli.py` | `test_servicio.py`; `test_conflictos.py`; `test_cli.py` | Disponibilidad y creación comparten la misma regla; suite de 99 pruebas OK; tras cancelar, el horario se informa disponible. | `e30b654`, `2c0869e`; [ver](docs/verificaciones.md) |
| RF-03 | `servicio.py`; `repositorio.py`; `modelos.py`; `cli.py` | `test_servicio.py`; `test_cli.py` | Se genera UUID y estado `activa`; suite de 99 pruebas OK; la reserva activa `c144c33b-f463-4bb6-9443-86a3c4e6e5ee` persistió tras reiniciar. | `e30b654`, `2c0869e`; [ver](docs/verificaciones.md) |
| RF-04 | `repositorio.py`; `servicio.py` | `test_conflictos.py`; `test_servicio.py` | Se rechaza una reserva activa superpuesta; suite de 99 pruebas OK, con 15 pruebas de conflictos. | `4f0883f`, `e30b654` |
| RF-05 | `repositorio.py`; `servicio.py` | `test_conflictos.py`; `test_servicio.py` | Los límites iguales se aceptan como consecutivos; suite de 99 pruebas OK. | `4f0883f`, `e30b654` |
| RF-06 | `repositorio.py`; `servicio.py` | `test_conflictos.py`; `test_servicio.py` | Reservas de unidades distintas no conflictúan; suite de 99 pruebas OK. | `4f0883f`, `e30b654` |
| RF-07 | `servicio.py`; `repositorio.py`; `cli.py` | `test_servicio.py`; `test_cli.py` | La reserva pasa a `cancelada` sin borrar sus datos; suite de 99 pruebas OK; la reserva `6403fb27-785b-44a0-bff7-c1bd7046eaf7` conservó sus datos. | `e30b654`, `2c0869e`; [ver](docs/verificaciones.md) |
| RF-08 | `db.py`; `repositorio.py`; `cli.py` | `test_repositorio.py`; `test_cli.py` | Activas y canceladas persisten tras cerrar y reabrir; suite de 99 pruebas OK; verificaciones manuales de ambas. | `4f0883f`, `2c0869e`; [ver](docs/verificaciones.md) |
| RF-09 | `inventario.py`; `tiempo.py`; `modelos.py`; `servicio.py`; `cli.py` | `test_inventario.py`; `test_tiempo.py`; `test_servicio.py`; `test_cli.py` | Se rechazan unidad inexistente, solicitante vacío o solo espacios, fecha/hora inválida e `inicio >= fin`; suite de 99 pruebas OK. | `39a9dd1`, `e30b654`, `2c0869e` |
| RF-10 | `servicio.py`; `repositorio.py`; `cli.py` | `test_servicio.py`; `test_cli.py` | Se consultan activas y canceladas con sus datos; suite de 99 pruebas OK; la reserva cancelada siguió en el historial. | `e30b654`, `2c0869e`; [ver](docs/verificaciones.md) |

**Resumen de resultados conservados:**

| Fase | Pruebas | Resultado | Origen |
|---|---|---|---|
| Fase 1 | 44 | `OK` | Ejecución humana independiente |
| Fase 2 | 67 | `OK` | Ejecución humana independiente |
| Fase 3 | 84 | `OK` | Ejecución humana independiente |
| Fase 4 | 99 | `OK` | Ejecución humana independiente |
| Persistencia | Activa y cancelada | Verificado | Sesiones manuales con `py -3.13 -m reservas` |

### Trazabilidad de commits

| Commit | Fecha | Contenido | Episodio |
|---|---|---|---|
| [`4ee5936`](https://github.com/Luciana2002/laboratorio-reservas/commit/4ee5936) | 2026-10-31 | Especificación inicial, `AGENTS.md`, inventario y documentos base. | Episodio 1 (análisis) |
| [`39a9dd1`](https://github.com/Luciana2002/laboratorio-reservas/commit/39a9dd1) | 2026-10-31 | Fase 1: inventario, fechas, modelos y 44 pruebas. | Episodio 1 (Fase 1 autorizada) |
| [`4f0883f`](https://github.com/Luciana2002/laboratorio-reservas/commit/4f0883f) | 2026-10-31 | Fase 2: SQLite, repositorio, conflictos y 67 pruebas. | Episodio 2 |
| [`b4de875`](https://github.com/Luciana2002/laboratorio-reservas/commit/b4de875) | 2026-10-31 | Documentación de la Fase 2. | Episodio 2 |
| [`e30b654`](https://github.com/Luciana2002/laboratorio-reservas/commit/e30b654) | 2026-10-31 | Fase 3: servicio, cancelación y 84 pruebas. | Episodio 3 |
| [`2c0869e`](https://github.com/Luciana2002/laboratorio-reservas/commit/2c0869e) | 2026-10-31 | Fase 4: interfaz de consola y 99 pruebas. | Episodio 4 |
| [`4376425`](https://github.com/Luciana2002/laboratorio-reservas/commit/4376425) | 2026-10-31 | Documentación final, matriz de trazabilidad y propuesta de evidencias. | Revisión documental (sin episodio de implementación) |

### Documentos de evidencia

- [Especificación inicial](docs/especificacion.md)
- [Preparación y uso real del agente](docs/agente.md)
- [Registro de decisiones](docs/decisiones.md)
- [Registro de delegaciones](docs/delegaciones.md)
- [Registro de verificaciones](docs/verificaciones.md)
- [Propuesta de evidencias crudas](docs/evidencias/README.md)
- [Inventario fijo](data/inventario.json)
- [Instrucciones para OpenCode](AGENTS.md)

**Commits directos:** [`4ee5936`](https://github.com/Luciana2002/laboratorio-reservas/commit/4ee5936) · [`39a9dd1`](https://github.com/Luciana2002/laboratorio-reservas/commit/39a9dd1) · [`4f0883f`](https://github.com/Luciana2002/laboratorio-reservas/commit/4f0883f) · [`b4de875`](https://github.com/Luciana2002/laboratorio-reservas/commit/b4de875) · [`e30b654`](https://github.com/Luciana2002/laboratorio-reservas/commit/e30b654) · [`2c0869e`](https://github.com/Luciana2002/laboratorio-reservas/commit/2c0869e) · [`4376425`](https://github.com/Luciana2002/laboratorio-reservas/commit/4376425)

Las decisiones humanas y las acciones del agente se distinguen en [`docs/delegaciones.md`](docs/delegaciones.md). Las revisiones documentales no modifican código, pruebas, `AGENTS.md` ni inventario; esta corrección final queda pendiente de revisión y commit por parte del responsable.
