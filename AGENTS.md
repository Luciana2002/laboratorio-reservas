# Instrucciones del proyecto para OpenCode — borrador v0.1

Estas instrucciones se prepararon antes de la primera sesión de implementación. Su uso real debe registrarse en `docs/agente.md`.

## Objetivo

Implementar la especificación de `docs/especificacion.md` de manera local y reproducible, con Python y SQLite; no agregar funciones fuera de alcance sin aprobación humana.

## Obligaciones técnicas

- Consultar `docs/especificacion.md` y `data/inventario.json` antes de editar código.
- Los horarios consecutivos NO entran en conflicto: usar intervalos `[inicio, fin)`; solapamiento solo si `nuevo_inicio < existente_fin and nuevo_fin > existente_inicio`.
- Solo reservas activas bloquean horarios; al cancelar conservar ID, solicitante, unidad, inicio y fin.
- La disponibilidad y la creación de reservas deben usar la misma regla de conflicto.
- Persistir registros y estados en SQLite: deben sobrevivir al reinicio.
- Validar unidad conocida, solicitante no blanco, fecha/hora válida e inicio estrictamente anterior al fin.
- No utilizar información real de estudiantes, claves, tokens ni credenciales.

## Flujo y controles humanos

- Antes de programar: explicar brevemente plan y archivos que se modificarán.
- Implementar una tarea delegada a la vez y explicar los cambios.
- No ejecutar comandos destructivos, borrar datos, publicar repositorios, instalar paquetes, realizar commits ni acceder a servicios externos sin aprobación humana explícita.
- Proponer pruebas, ejecutarlas cuando esté permitido e informar comando exacto, salida resumida y fallos. Nunca afirmar que se ejecutaron si no ocurrió.
- Actualizar `docs/decisiones.md` y `docs/delegaciones.md` con información comprobable de lo realmente realizado; el humano debe aceptar su contenido.
- Conservar evidencias de archivos modificados, comandos de verificación y decisiones.
