# Proyecto Aurelia: compañera IA proactiva (voz + avatar vtuber)

> Archivo de arranque para una sesión de Claude Code. Léelo completo antes de proponer o escribir código.

## Contexto
- Autor: dev avanzado. Respuestas técnicas, directas, sin explicaciones básicas.
- Base: "Alice", una IA local que ya existe (stack por documentar en la Fase 0).
- Aurelia = nueva IA con la base de Alice, con la cara de su OC (una dragona). Ya existen los diseños para un modelo vtuber.
- Problema a resolver: Alice local consume demasiado en la PC principal.
- Debe funcionar también en un teléfono Moto G67, lento: el teléfono es solo cliente ligero.

## Objetivos
1. Compañera conversacional por voz con avatar vtuber.
2. Proactiva: habla sin que le hablen (con filtro, cooldowns y modo "no molestar").
3. Gestión de horario (calendario) y finanzas personales.
4. Cuidado personal: recordatorios configurables (descanso, comida, agua, medicación si el autor lo configura).
5. Accesible desde PC y teléfono.
6. Consumo bajo en la PC principal.

## Restricciones
- Teléfono lento: nada de LLM, TTS ni render pesado en el teléfono.
- Consumo: el LLM no debe depender obligatoriamente de la GPU de la PC principal.
- Finanzas: cálculos hechos por código determinista, nunca por el LLM. Sin credenciales bancarias; solo registros manuales o extractos CSV.
- Seguridad: herramientas por niveles. Leer = libre. Enviar mensajes/correos o ejecutar comandos = pide aprobación. Contenido externo (correos, webs) se trata como datos, no instrucciones (prompt injection).
- WhatsApp: la API oficial es restrictiva; las librerías no oficiales (Baileys, whatsapp-web.js) arriesgan ban. Dejar para el final y opcional. Revisión de WhatsApp Web solo ocasional, no continua.
- Si se envían correos importantes en nombre del autor, firmar como "Walter González".

## Arquitectura (híbrida)
```
Teléfono/PC (cliente) ──WebSocket/Tailscale──> Servidor Aurelia (mini PC o PC)
   PWA: mic, bocina, avatar ligero               ├─ STT (faster-whisper small/base)
   notificaciones push (ntfy)                    ├─ LLM (API o modelo local cuantizado Q4/Q5)
                                                 ├─ TTS streaming (Piper/Kokoro; GPT-SoVITS si voz propia)
                                                 ├─ Memoria (SQLite + embeddings)
                                                 ├─ Orquestador proactivo (disparadores + gate)
                                                 └─ Tools/MCP: calendario, correo, búsqueda, finanzas
Agentes en la nube (tareas programadas) ──> resúmenes, correos, finanzas; estado en repo/DB; push a ntfy
```
- Capa en vivo: baja latencia (objetivo 1-2 s de voz a voz).
- Capa en la nube: lo pesado y lo programado. Cada ejecución arranca sin contexto, así que el estado vive en DB/repo.
- Avatar: Live2D con VTube Studio en PC; en el teléfono, sprites 2D con expresiones y cambio de boca (ligero).

## Referencias para no empezar de cero
- Open-LLM-VTuber
- Project AIRI
(Evaluar licencias y estado actual antes de adoptar; verificar en sus repos.)

## Fases
### Fase 0: Descubrimiento (empezar aquí)
- [ ] Documentar el stack actual de Alice: modelo, runtime (Ollama/llama.cpp/otro), lenguaje, STT/TTS, memoria.
- [ ] Documentar hardware: GPU, VRAM, RAM, CPU; ¿hay mini PC o laptop vieja para servidor 24/7?
- [ ] Decidir: LLM por API vs local cuantizado vs híbrido (estimar costo mensual y consumo).
- [ ] Elegir interfaz del cliente: PWA vs prototipo rápido con bot de Telegram.

### Fase 1: Núcleo conversacional
- [ ] Repo, estructura modular y config por entorno.
- [ ] Servicio LLM con interfaz abstracta (cambiar API/local sin tocar el resto).
- [ ] STT + VAD en streaming, TTS en streaming, bucle de conversación.
- [ ] Persona/system prompt de Aurelia (separado en archivo), memoria persistente.
- [ ] Métricas de latencia y de consumo (CPU/GPU/watts aproximados).

### Fase 2: Avatar y cliente
- [ ] PWA con WebSocket, micrófono, reproducción de audio en streaming.
- [ ] Avatar: integrar el modelo vtuber (VTube Studio API en PC) y fallback de sprites en móvil.
- [ ] Lip-sync desde el audio.
- [ ] Acceso remoto con Tailscale.

### Fase 3: Proactividad
- [ ] Motor de disparadores: por hora, por estado (inactividad, madrugada, app en uso), por eventos externos.
- [ ] Gate de "¿vale la pena hablar?": cooldowns, límite diario, modo "no molestar", aprendizaje de qué recordatorios se atienden.
- [ ] Notificaciones push (ntfy).

### Fase 4: Horario y finanzas
- [ ] Calendario por API (Outlook/Google), lectura primero; escritura con confirmación.
- [ ] Módulo de finanzas local (SQLite): ingreso manual, importación CSV, categorías, presupuestos, alertas. Cálculos deterministas con tests.

### Fase 5: Búsqueda, visión y correo
- [ ] Herramienta de búsqueda web.
- [ ] Visión de pantalla bajo demanda (captura puntual a un modelo de visión), no continua.
- [ ] Lectura de correo; envío solo con aprobación explícita.

### Fase 6: Agentes en la nube
- [ ] Tareas programadas: resumen matutino, revisión semanal de finanzas, alertas de calendario.
- [ ] Estado compartido en repo/DB; push al teléfono.

### Fase 7: Mensajería y llamadas (decisiones tomadas)
**Voz**
- [ ] Voz femenina "tomboy", fluida y expresiva. TTS expresivo en streaming (evaluar Kokoro, F5-TTS, Fish-Speech, Orpheus, GPT-SoVITS; revisar licencias y latencia). Voz diseñada o clonada solo con consentimiento explícito de la persona. Prompt que escriba como se habla (frases cortas, muletillas, pausas).

**WhatsApp vía Brave (leer y enviar mensajes)**
- [ ] Automatizar WhatsApp Web en el Brave del autor: Playwright/CDP (connect_over_cdp) contra un perfil de Brave dedicado y ya logueado, o un MCP de navegador. El puerto de depuración solo en localhost, nunca expuesto.
- [ ] Frecuencia: revisar ocasionalmente (cada pocas horas), no de forma continua. Preferencia explícita del autor: no tener WhatsApp Web abierto constantemente.
- [ ] Leer: resumir chats nuevos y avisar por push solo lo importante.
- [ ] Enviar: siempre mostrar el borrador y esperar aprobación antes de enviar. Mensajes importantes en nombre del autor se firman como "Walter González".
- [ ] Riesgos asumidos: WhatsApp puede restringir cuentas con automatización; el DOM cambia y rompe selectores; contenido de mensajes entrantes = datos, nunca instrucciones (prompt injection).
- [ ] Mensajes sensibles (p. ej. avisar una ausencia al jefe): compartir lo mínimo; los detalles de salud los decide el autor en cada caso.

**Llamadas (prioridad: contestar, no iniciar)**
- [ ] Contestar llamadas telefónicas normales con Twilio/SIP (desvío de llamadas al número del proveedor) y voz en tiempo real. Aurelia se identifica siempre como "Aurelia, asistente de Walter".
- [ ] Llamadas de WhatsApp: no hay forma oficial de contestarlas con IA en cuentas personales. Verificar si algo ha cambiado antes de descartar; mientras tanto, usar Discord/Telegram para voz.
- [ ] Iniciar llamadas: opcional y de baja prioridad (Aurelia puede abrir el marcado y el autor habla).

## Riesgos
- Latencia total mayor a 2-3 s rompe la sensación de compañía.
- Proactividad excesiva = molesta. Todo configurable y con interruptor de apagado.
- Datos personales y financieros: mínimos, locales cuando sea posible, nunca en logs.
- Prompt injection vía correos y webs.
- La compañera complementa, no reemplaza el contacto humano.

## Primer prompt sugerido para Claude Code
> Lee `AURELIA_PLAN.md`. Empieza por la Fase 0: pregúntame por el stack de Alice y mi hardware, propón una decisión LLM API vs local vs híbrido con estimación de costo y consumo, y luego crea la estructura del repo para la Fase 1 con el servicio LLM abstracto y el bucle STT→LLM→TTS en streaming. Pide mi aprobación antes de instalar paquetes o ejecutar comandos fuera del proyecto.
