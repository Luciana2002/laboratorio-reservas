# Preparación y uso real de OpenCode

Este documento registra el entorno, las instrucciones, las herramientas y las aprobaciones humanas del proyecto. Distingue lo observado de lo que sigue pendiente de confirmación; no completa datos por inferencia.

## 1. Identificación del entorno

- **Fecha de ejecución registrada:** 2026-10-31 (fecha del entorno de la sesión y de los commits).
- **Sistema operativo:** Windows (Microsoft Windows NT 10.0.26200.0).
- **Editor:** Visual Studio Code, según el entorno declarado por el responsable y las verificaciones humanas registradas.
- **Terminal:** PowerShell 5.1.26100.9711.
- **Python:** 3.13.7, comprobado con `py -3.13 --version` y `python --version`.
- **Agente:** OpenCode 2.0.10, comprobado con `cmd /c "opencode --version"` → `opencode v2.0.10`.
- **Repositorio:** `https://github.com/Luciana2002/laboratorio-reservas.git`.

## 2. Modelo y proveedor

### 2.1 Sesión actual (revisión documental)

| Campo | Valor | Evidencia |
|---|---|---|
| Proveedor | `opencode` | Metadatos de la sesión actual |
| Modelo | `big-pickle` (nombre visible «Big Pickle») | Metadatos de la sesión actual |
| Alcance de la afirmación | Solo la sesión actual | No hay log versionado por fase |

Esta identificación proviene de los metadatos de la sesión actual, no de un archivo de configuración versionado. Por eso la afirmación **no se extiende** a las sesiones anteriores.

### 2.2 Episodios 1 a 4 (sesiones anteriores)

| Sesión | Modelo/proveedor | Evidencia | Estado |
|---|---|---|---|
| Episodio 1 (análisis y Fase 1) | No registrado | Sin log versionado | No verificable |
| Episodio 2 (Fase 2) | No registrado | Sin log versionado | No verificable |
| Episodio 3 (Fase 3) | No registrado | Sin log versionado | No verificable |
| Episodio 4 (Fase 4) | No registrado | Sin log versionado | No verificable |

**No debe interpretarse** que `big-pickle` fue el modelo de los episodios 1 a 4. La documentación solo puede afirmar el modelo y el proveedor de la sesión actual. Tampoco se conserva la versión de OpenCode usada en cada una de esas sesiones; la versión 2.0.10 se comprobó en la sesión de la Etapa 5.

### 2.3 Cómo comprobarlo

1. En la interfaz de OpenCode, abrir el selector de modelo o la información de la sesión y contrastar el proveedor y el identificador mostrados.
2. Ejecutar `opencode models` para listar los identificadores de modelo disponibles y compararlos con el que muestra la sesión.
3. Revisar los registros de la sesión o la configuración local de OpenCode, sin transcribir credenciales ni claves.

No se identificó una configuración externa de permisos versionada en el repositorio. No se transcribe ninguna configuración de ese tipo porque no hay evidencia de ella.

## 3. Función del agente y motivo de elección

OpenCode se usó como **agente de implementación asistida, revisión y ejecución de pruebas** sobre un repositorio real. La elección se justifica porque permite:

- Leer y modificar archivos del proyecto con control humano.
- Ejecutar comandos de verificación y pruebas de la biblioteca estándar.
- Mantener el progreso en Git y en documentos versionados.
- Trabajar por fases, con revisión y aceptación humanas entre una fase y la siguiente.

El agente no reemplazó las decisiones de producto ni las aprobaciones: cada fase fue autorizada, revisada y aceptada por el responsable.

## 4. Instrucciones de `AGENTS.md` y cómo se aplicaron

| Instrucción | Aplicación comprobable |
|---|---|
| Consultar `docs/especificacion.md` y `data/inventario.json` antes de editar código. | Se leyeron antes de cada fase; el inventario se usa como fuente única de unidades y tiene pruebas propias. |
| Intervalos `[inicio, fin)`; solapamiento solo si `nuevo_inicio < existente_fin and nuevo_fin > existente_inicio`. | Implementado en `reservas/tiempo.py` y en la consulta de `reservas/repositorio.py`; cubierto por `tests/test_conflictos.py` y `tests/test_servicio.py`. |
| Solo reservas activas bloquean; al cancelar conservar ID, solicitante, unidad, inicio y fin. | La consulta filtra `estado = 'activa'`; la cancelación actualiza solo estado y `cancelada_en`; cubierto por pruebas de servicio y consola. |
| Disponibilidad y creación deben usar la misma regla de conflicto. | `ServicioReservas.consultar_disponibilidad()` y `crear_reserva()` delegan en `hay_conflicto()` / `insertar_si_libre()`. |
| Persistir registros y estados en SQLite; deben sobrevivir al reinicio. | `reservas/db.py` y `reservas/repositorio.py`; pruebas de cierre/reapertura y verificación manual de reservas activas y canceladas. |
| Validar unidad conocida, solicitante no blanco, fecha/hora válida e inicio estrictamente anterior al fin. | Validaciones en inventario, tiempo, modelo y servicio; cubiertas por las suites de las fases 1 a 4. |
| No usar información real de estudiantes, claves, tokens ni credenciales. | Todas las pruebas y ejemplos usan nombres ficticios y bases temporales; no se incorporaron secretos. |
| Explicar el plan y los archivos antes de programar; una tarea delegada a la vez. | Cada fase se autorizó por separado y se registró en `docs/delegaciones.md`. |
| No ejecutar comandos destructivos, borrar datos, publicar, instalar paquetes, hacer commits ni acceder a servicios externos sin aprobación. | El agente no instaló dependencias, no borró datos reales, no publicó, no hizo commits ni push. Los commits los realizó el responsable. |
| Proponer y ejecutar pruebas cuando esté permitido; informar comando, salida y fallos sin afirmar ejecuciones inexistentes. | Los comandos y resultados reales se registran en `docs/verificaciones.md`; los resultados no ejecutados se marcan como pendientes. |
| Actualizar `docs/decisiones.md` y `docs/delegaciones.md` con información comprobable; el humano acepta su contenido. | Ambos documentos se actualizaron por fase y se ampliaron en la Etapa 5; la aceptación final queda a cargo del responsable. |

## 5. Herramientas y permisos utilizados

**Herramientas utilizadas:**

- Lectura de archivos del repositorio (`README.md`, `AGENTS.md`, `docs/`, `reservas/`, `tests/`).
- Edición y escritura de archivos de código, pruebas y documentación.
- Comandos de shell en PowerShell para:
  - Git de solo lectura: `git log`, `git status`, `git show --stat`.
  - Ejecución de pruebas: `py -3.13 -m unittest discover -s tests -v`.
  - Verificación de versiones: `py -3.13 --version`, `python --version`, `opencode --version`.
- Ejecución manual de la aplicación con bases temporales durante la Fase 4.

**Permisos y controles:**

- No se identificó una configuración de permisos personalizada versionada; el control efectivo fue la autorización humana explícita en cada fase y las restricciones de `AGENTS.md`.
- No se usaron servicios externos, navegador, instalación de paquetes ni acceso a credenciales.
- Las pruebas y ejemplos usan bases SQLite temporales; la base real `data/reservas.db` fue utilizada por el responsable en las verificaciones manuales.
- El agente no realizó commits ni push. Los commits `39a9dd1`, `4f0883f`, `b4de875`, `e30b654` y `2c0869e` fueron creados por el responsable después de revisar y aceptar cada fase.

## 6. Acciones delegadas y aprobaciones humanas

### Episodio 1 — Análisis y Fase 1

- **Acción del agente:** analizó el repositorio y la especificación, propuso un plan incremental y, tras la autorización, implementó el dominio: `reservas/__init__.py`, `inventario.py`, `tiempo.py`, `modelos.py`, `tests/__init__.py`, `test_inventario.py` y `test_tiempo.py`.
- **Resultado:** 44 pruebas aprobadas.
- **Decisión humana:** aceptó el análisis, fijó las decisiones D-004 a D-012, autorizó la Fase 1 y verificó las 44 pruebas.
- **Commit:** `39a9dd1`.

### Episodio 2 — Persistencia y conflictos

- **Acción del agente:** creó `reservas/db.py`, `reservas/repositorio.py`, `tests/test_conflictos.py` y `tests/test_repositorio.py`; implementó la consulta de conflicto y la inserción atómica.
- **Resultado:** 67 pruebas aprobadas.
- **Decisión humana:** ejecutó y aprobó las 67 pruebas; autorizó registrar la fase.
- **Commits:** `4f0883f` (implementación) y `b4de875` (documentación).

### Episodio 3 — Servicio de reservas

- **Acción del agente:** creó `reservas/servicio.py` y `tests/test_servicio.py`; agregó `marcar_cancelada()` en `reservas/repositorio.py`.
- **Resultado:** 84 pruebas aprobadas, 17 nuevas.
- **Decisión humana:** ejecutó y aprobó las 84 pruebas.
- **Commit:** `e30b654`.

### Episodio 4 — Interfaz de consola

- **Acción del agente:** creó `reservas/cli.py`, `reservas/__main__.py` y `tests/test_cli.py`.
- **Resultado:** 99 pruebas aprobadas, 15 nuevas.
- **Decisión humana:** ejecutó y aprobó las 99 pruebas; verificó manualmente creación, conflicto, cancelación y persistencia de reservas activas y canceladas.
- **Commit:** `2c0869e`.

### Etapa 5 — Revisión documental

- **Acción del agente:** releyó toda la documentación, los módulos y las pruebas; contrastó el contenido con el código y los commits; actualizó únicamente `README.md`, `docs/agente.md`, `docs/decisiones.md`, `docs/delegaciones.md` y `docs/verificaciones.md`.
- **Decisión humana:** autorizó exclusivamente esos cinco documentos y pidió no modificar código, pruebas, `AGENTS.md` ni inventario.
- **Estado:** cambios pendientes de revisión humana; no se realizó commit en esta etapa.

### Ajuste documental final — Matriz de trazabilidad y evidencias

- **Acción del agente:** incorporó la matriz RF-01 a RF-10 en el `README.md`; revisó los cuatro episodios de `docs/delegaciones.md`; separó el modelo de la sesión actual de las sesiones no verificables; ordenó la separación entre resultados informados por OpenCode y ejecuciones humanas; y creó `docs/evidencias/README.md` como propuesta, sin inventar archivos.
- **Decisión humana:** solicitó la mejora documental y prohibió modificar código, pruebas, inventario y `AGENTS.md`; no autorizó commits ni push.
- **Estado:** cambios pendientes de revisión humana.

## 7. Contexto suministrado y excluido

**Suministrado:**

- Consigna del Challenge IA y especificación del sistema.
- Inventario fijo de cinco unidades.
- Código y pruebas de las fases anteriores.
- Documentos de decisiones, delegaciones y verificaciones.
- Restricciones explícitas de cada fase (no instalar dependencias, no borrar datos, no hacer commits, usar bases temporales).

**Excluido:**

- Claves, tokens, credenciales y variables de entorno sensibles.
- Datos reales de estudiantes o de terceros.
- Chats privados y contenido ajeno al proyecto.
- Servicios externos y publicaciones en red.

## 8. Adaptaciones específicas del proyecto

### Turnos consecutivos

Se adoptó el intervalo semiabierto `[inicio, fin)`. La consulta de conflicto usa comparaciones estrictas:

```sql
inicio < :fin_nuevo AND fin > :inicio_nuevo
```

Por eso `10:00–11:00` y `11:00–12:00` no conflictúan. La regla se comparte entre disponibilidad y creación, y se prueba en `tests/test_conflictos.py` y `tests/test_servicio.py`.

### Persistencia

- Base SQLite local en `data/reservas.db`, con esquema idempotente (`CREATE TABLE IF NOT EXISTS`).
- Inserción y cancelación dentro de transacciones; `insertar_si_libre()` usa `BEGIN IMMEDIATE` cuando no hay una transacción abierta.
- Pruebas de cierre y reapertura de conexión, y de ejecuciones independientes de la consola.
- Verificación manual de una reserva cancelada y de una reserva activa después de cerrar y volver a abrir la aplicación, registrada en `docs/verificaciones.md`.

### Validaciones

- Unidad existente en el inventario, con IDs exactos y sensibles a mayúsculas.
- Solicitante no vacío ni compuesto solo por espacios; se recortan los espacios exteriores.
- Fecha/hora estricta `AAAA-MM-DD HH:MM`, validada con regex y `datetime.strptime`.
- `inicio < fin` obligatorio; se rechazan intervalos vacíos o invertidos.
- Las operaciones inválidas no modifican la base.
- La cancelación de un ID inexistente lanza `ReservaNoEncontrada`; una segunda cancelación no cambia los datos y devuelve `cancelada_ahora=False`.

## 9. Archivo utilizado para conservar decisiones y progreso

- [`docs/decisiones.md`](decisiones.md): decisiones D-001 a D-018, con motivo, consecuencias, estado y commits cuando corresponde.
- [`docs/delegaciones.md`](delegaciones.md): los cuatro episodios reales de delegación, con acciones del agente, decisiones humanas y evidencia.
- [`docs/verificaciones.md`](verificaciones.md): comandos, resultados reales, verificaciones manuales y estado de cada fase.
- [`docs/evidencias/README.md`](evidencias/README.md): propuesta de archivos de evidencia real; no contiene capturas, registros ni transcripciones inventadas.
- [`README.md`](../README.md): resumen del sistema, ejecución, pruebas, matriz de trazabilidad y enlaces a la evidencia.

## 10. Comprobaciones y limitaciones

- La versión de OpenCode se comprobó en la sesión de la Etapa 5; no hay un registro por fase que demuestre que fue la misma en los episodios anteriores.
- El modelo y proveedor se identifican solo para la sesión actual; no se conservó un log versionado por fase.
- No se identificó ni transcribió una configuración personalizada de permisos.
- La revisión humana línea por línea del código sigue pendiente; la Etapa 5 releyó el código para contrastar la documentación, sin reemplazar esa revisión.
- El reinicio de datos se probó con bases temporales en la suite, no manualmente sobre la base real.
- El clon limpio se verificó después de la revisión de la Etapa 5: desde una carpeta nueva, `git clone`, 99 pruebas `OK` en `1.426s`, inicio de la aplicación y visualización de los cinco equipos. El procedimiento consta en [`docs/verificaciones.md`](verificaciones.md#verificación-de-reproducibilidad-desde-un-clon-limpio--31102026); el archivo crudo no se conservó (ver [`docs/evidencias/README.md`](evidencias/README.md)).
- No se conservan archivos crudos de las ejecuciones de pruebas ni transcripciones de las sesiones manuales. [`docs/evidencias/README.md`](evidencias/README.md) propone qué archivos reales podrían adjuntarse y distingue lo disponible de lo pendiente.
