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