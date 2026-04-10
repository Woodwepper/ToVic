# ToVIC

Este proyecto es un juego o simulador de estrategia donde cada guild de Discord representa un mundo independiente. El sistema se compone de una pagina web, un bot de Discord, un motor en Python y una base de datos.
### DOCUMENTACION: https://woodwepper.github.io/tovic-docs/
## Resumen

La idea general es:

- Cada servidor de discord es un mundo diferente
- Un administrador crea y configura el mundo desde una web
- Los jugadores pueden contrar el pais con el bot, y verlo visualmente desde la pagina
- El bot de Discord es la principal forma de jugar en el juego
- El motor central procesa toda la logica
- La web sirve como editor y como visor visual del estado del juego

## Componentes principales

### Web
Se usa para:
- Autenticacion con Discord
- Editor del mundo
- Vista del mapa
- Consulta de informacion del juego

### Bot de Discord
Se usa para:
- Recibir comandos
- Consultar informacion
- Mandar ordenes al motor
- Responder a jugadores y admins

### Motor
Se encarga de:
- Validar reglas
- Procesar ticks
- Resolver economia, construccion, movimiento y combate
- Guardar el estado del juego

### Base de datos
Se usa para:
- Guardar definiciones del mundo
- Guardar el estado actual
- Guardar ordenes y eventos

## Regla principal

Ni la web ni el bot deben modificar directamente el estado del juego.

Solo el motor puede hacerlo.

## Flujo general

1. Un admin crea o configura el mundo desde la web
2. El motor valida y guarda esos cambios
3. El mundo pasa a estar listo
4. Los jugadores usan el bot para jugar
5. El motor procesa ordenes y ticks
6. La web muestra el estado actualizado

## Estado del proyecto

Actualmente el proyecto esta en fase de diseño y documentacion de arquitectura.

## Objetivo inicial

Construir primero un MVP simple con:

- 1 mundo por guild
- paises
- provincias
- recursos basicos
- stock basico
- una fabrica basica
- un ejercito basico
- ordenes simples desde Discord
- pagina visual para consultar el estado

## Estructura esperada

```text
project/
├─ apps/
│  ├─ engine/
│  ├─ api/
│  ├─ bot/
│  └─ web/
├─ docs/
├─ data/
├─ scripts/
└─ tests/
