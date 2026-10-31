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

## Cambios posteriores

Agregar fecha, decisión, motivo, alternativas, efecto y commit real asociado cuando ocurra.
