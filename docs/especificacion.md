# Especificación inicial — v0.1

**Origen:** consigna «Desarrollo de un sistema de reservas con agentes», pp. 1–3.  
**Estado:** propuesta inicial para preservar en Git antes de implementar.  
**Objetivo de negocio:** evitar reservas activas superpuestas sobre una misma unidad y liberar horarios cancelados, conservando el historial.

## 1. Inventario fijo

| ID | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

Cada ID representa una unidad física distinta. Solo lectura; no se implementará administración de inventario.

## 2. Requisitos funcionales y criterios de aceptación

| ID | Requisito | Criterio verificable |
|---|---|---|
| RF-01 | Listar inventario | Se muestran exactamente las 5 unidades precargadas. |
| RF-02 | Consultar disponibilidad | Dada unidad e intervalo válidos, se informa libre/ocupado aplicando las reglas de superposición de reservas activas. |
| RF-03 | Crear reserva | Se genera identificador único y se conservan ID de unidad, solicitante ficticio, inicio, fin y estado activo. |
| RF-04 | Evitar conflicto | Con MIC-01 ocupado 10:00–11:00, no se acepta MIC-01 10:30–11:30. |
| RF-05 | Permitir consecutivas | Con MIC-01 ocupado 10:00–11:00, se acepta MIC-01 11:00–12:00. |
| RF-06 | Independencia entre unidades | MIC-02 se puede reservar 10:00–11:00 aun si MIC-01 está reservado simultáneamente. |
| RF-07 | Cancelar sin borrar | La reserva conserva identificador, campos y estado `cancelada`; el intervalo vuelve a estar libre. |
| RF-08 | Persistir | Tras cerrar y abrir el proceso sin borrar base, reaparecen reservas activas y canceladas. |
| RF-09 | Rechazar inválidos | Se rechazan unidad inexistente, solicitante vacío o solo espacios, fecha/hora inválida, e inicio >= fin. |
| RF-10 | Conservar historial | Se pueden consultar reservas activas y canceladas, con datos sin perder. |

## 3. Reglas formales

- Una reserva ocupa el intervalo semiabierto `[inicio, fin)` solo si está activa.
- Para dos intervalos de una **misma** unidad con reservas activas, hay solapamiento si `inicio_nuevo < fin_existente` **y** `fin_nuevo > inicio_existente`.
- Límites iguales son consecutivos, no superpuestos.
- Reservas de unidades diferentes no entran en conflicto.
- La consulta de disponibilidad y la creación deben aplicar la misma validación y criterio de conflicto.
- Cancelar nunca debe eliminar el registro ni cambiar su identificador.

## 4. Decisiones/supuestos de diseño (no impuestos por la consigna)

- Aplicación de consola local, Python 3 y SQLite; sin servicios de nube.
- Fechas ingresadas en hora local `America/Argentina/Buenos_Aires`, formato `AAAA-MM-DD HH:MM` (24 horas). Se rechazarán fechas/hora que no correspondan a un momento calendario válido.
- Fechas pasadas: se admitirán como reservas de ejemplo/históricas para poder reproducir las pruebas, pues la consigna no lo prohíbe. No habrá límite de anticipación ni de duración, salvo `inicio < fin`.
- Solicitante: texto con al menos un carácter no blanco, y se guardará con espacios exteriores recortados.
- Cancelar una reserva ya cancelada: responder sin efecto e informar que ya está cancelada, sin borrar el historial.
- ID de reserva: UUID; estado `activa` o `cancelada`.
- En esta primera versión, los intervalos se interpretan en la zona indicada sin aceptar zonas distintas por reserva.

## 5. Exclusiones

Autenticación, roles reales, pagos, notificaciones, servicios externos, GUI, despliegue, concurrencia distribuida y escalabilidad de producción. No se administrará inventario.

## 6. Verificación exigida

Se implementarán y **ejecutarán** pruebas automatizadas para: creación válida; rechazo de superposición; límites consecutivos; unidades distintas simultáneas; entradas inválidas; cancelación e historial; disponibilidad tras cancelar. También se comprobará persistencia de reservas activas y canceladas tras reiniciar **sin eliminar la base**. Se documentarán comandos, resultados reales y fallos; no se marcará ningún test como aprobado sin ejecutarlo.

## 7. Versionado

Esta versión `v0.1` quedará en el primer commit. Las modificaciones posteriores se documentarán con motivo y referencia a commit en `docs/decisiones.md`.
