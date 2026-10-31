# Propuesta de evidencias reales

Esta carpeta está destinada a conservar **evidencia real** del proyecto. No contiene capturas, transcripciones, registros ni resultados inventados. Los archivos de la tabla son una propuesta de lo que podría adjuntarse si el responsable los genera o exporta desde su entorno.

## Archivos propuestos

| Archivo propuesto | Contenido real esperado | Origen o comando | Estado actual |
|---|---|---|---|
| `entorno.txt` | Versiones observadas de OpenCode, Python, Windows y PowerShell. | `cmd /c "opencode --version"`; `py -3.13 --version`; `$PSVersionTable.PSVersion`; `[System.Environment]::OSVersion.VersionString` | Datos disponibles en [`docs/agente.md`](../agente.md); archivo crudo no conservado. |
| `fase-1-unittest.txt` | Salida de la suite de la Fase 1. | `py -3.13 -m unittest discover -s tests -v` | Resultado resumido en [`docs/verificaciones.md`](../verificaciones.md): 44 pruebas, `OK`; archivo crudo no conservado. |
| `fase-2-unittest.txt` | Salida de la suite de la Fase 2. | `py -3.13 -m unittest discover -s tests -v` | Resultado resumido: 67 pruebas, `OK`; archivo crudo no conservado. |
| `fase-3-unittest.txt` | Salida de la suite de la Fase 3. | `py -3.13 -m unittest discover -s tests -v` | Resultado resumido: 84 pruebas, `OK`; archivo crudo no conservado. |
| `fase-4-unittest.txt` | Salida de la suite de la Fase 4. | `py -3.13 -m unittest discover -s tests -v` | Resultado resumido: 99 pruebas, `OK`; archivo crudo no conservado. |
| `persistencia-cancelada.txt` | Transcripción de la sesión manual con la reserva cancelada `6403fb27-785b-44a0-bff7-c1bd7046eaf7`. | `py -3.13 -m reservas` | Procedimiento y resultado en [`docs/verificaciones.md`](../verificaciones.md); transcripción cruda no conservada. |
| `persistencia-activa.txt` | Transcripción de la sesión manual con la reserva activa `c144c33b-f463-4bb6-9443-86a3c4e6e5ee`. | `py -3.13 -m reservas` | Procedimiento y resultado en [`docs/verificaciones.md`](../verificaciones.md); transcripción cruda no conservada. |
| `git-log.txt` | Salida de `git log --oneline --decorate` y de `git show --stat` para los seis commits. | `git log --oneline --decorate`; `git show --stat <commit>` | Reconstruible desde el repositorio; archivo no conservado. |
| `reinicio-datos.txt` | Salida de una prueba de reinicio con base temporal. | `py -3.13 -m unittest discover -s tests -v` | Cubierto por pruebas automatizadas; no se ejecutó manualmente sobre la base real. |
| `clon-limpio.txt` | Salida de clonar, ejecutar y probar desde un directorio nuevo. | `git clone https://github.com/Luciana2002/laboratorio-reservas.git`; `py -3.13 -m unittest discover -s tests -v`; `py -3.13 -m reservas` | **Procedimiento ejecutado y aprobado** sobre el commit `2c0869e`: 99 pruebas `OK` en `1.426s`, inicio de la aplicación y visualización de los cinco equipos (`MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`). El detalle está en [`docs/verificaciones.md`](../verificaciones.md#verificación-de-reproducibilidad-desde-un-clon-limpio--31102026). **El archivo crudo `clon-limpio.txt` todavía no fue adjuntado.** |

## Criterios para incorporar archivos

- Incluir solo salidas reales, sin editar ni completar manualmente.
- Identificar el comando, la fecha y el commit de partida.
- No incluir `data/reservas.db`, credenciales, tokens, variables de entorno ni datos reales de estudiantes.
- Usar únicamente nombres ficticios en las transcripciones, como en las verificaciones ya registradas.
- Si un archivo no existe, dejarlo como pendiente; no crear un reemplazo ficticio.

## Enlaces de referencia

- [README del proyecto](../../README.md)
- [Registro de verificaciones](../verificaciones.md)
- [Registro de delegación](../delegaciones.md)
- [Preparación del agente](../agente.md)
- [Registro de decisiones](../decisiones.md)
- Commits: [`4ee5936`](https://github.com/Luciana2002/laboratorio-reservas/commit/4ee5936), [`39a9dd1`](https://github.com/Luciana2002/laboratorio-reservas/commit/39a9dd1), [`4f0883f`](https://github.com/Luciana2002/laboratorio-reservas/commit/4f0883f), [`b4de875`](https://github.com/Luciana2002/laboratorio-reservas/commit/b4de875), [`e30b654`](https://github.com/Luciana2002/laboratorio-reservas/commit/e30b654), [`2c0869e`](https://github.com/Luciana2002/laboratorio-reservas/commit/2c0869e).
