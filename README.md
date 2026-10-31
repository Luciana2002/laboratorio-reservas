# Sistema local de reservas de laboratorio

Proyecto individual del Challenge IA. Estado: **Etapa 1 — especificación inicial; implementación pendiente**.

## 1. Especificación breve

Se desarrollará un sistema local para consultar inventario y disponibilidad, crear reservas y cancelar sin eliminar el historial. Ver [especificación inicial](docs/especificacion.md) para reglas, supuestos y criterios de aceptación. La evolución se conserva en el historial de Git.

## 2. Solución

**Diseño previsto (aún no implementado):** Python 3, biblioteca estándar, SQLite y consola. Una unidad física por reserva; inventario fijo en [`data/inventario.json`](data/inventario.json). Zona horaria y formato en la especificación.

**Estructura actual:** `docs/` documenta requisitos y decisiones; `data/` incluye inventario; `AGENTS.md` define instrucciones para OpenCode.

**Instalación, ejecución, pruebas, persistencia y reinicio de datos:** pendientes de implementar y documentar en la Etapa 2/3. No se afirma que el programa funcione todavía. Se prevé almacenar reservas en un archivo SQLite local, ignorado por Git. El procedimiento de reinicio de datos deberá advertir explícitamente que elimina reservas.

## 3. Preparación del agente

Agente elegido: **OpenCode**, desde Visual Studio Code. Las instrucciones previstas y versionadas están en [AGENTS.md](AGENTS.md). **Modelo exacto, versión de OpenCode, permisos efectivamente utilizados y resultados:** pendientes de registrar con observación real, nunca inventarlos. Véase [registro del agente](docs/agente.md).

## 4. Registro de decisiones y delegación

Véanse [decisiones](docs/decisiones.md), [delegaciones](docs/delegaciones.md) y [verificaciones](docs/verificaciones.md). Los tres episodios deben consignar tareas reales realizadas por OpenCode, revisión humana y evidencias (archivos/commits/comandos), cuando ocurran.

## Alcance de la entrega

Este commit inicial conserva la especificación antes de implementar. Faltan código ejecutable, pruebas automáticas y evidencias de ejecución.
