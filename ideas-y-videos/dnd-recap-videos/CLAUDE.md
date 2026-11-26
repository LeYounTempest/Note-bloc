# CLAUDE.md — instrucciones para Claude Code

Proyecto: videos animados en **pixel art 8-bit (vertical 1080x1920, 30 fps)** que resumen la campaña de D&D (Forge/Foundry) de Walter ("LeYounTempest"). Él pone la voz; tú armas animación, subtítulos y render. Responde en español, técnico y directo (es dev senior).

## Cómo correr
```
./setup.sh        # python3, playwright, ffmpeg, Chrome
python3 engine/render.py episodes/iguana_intro/episode.json out/test.mp4
# vista previa rápida (JPEG por tiempo, sin render completo):
python3 engine/render.py episodes/iguana_intro/episode.json /tmp/x --preview /tmp/prev --at 10,23,35,44
# una sola escena: --only N
```
Si Chrome no está en /usr/bin/google-chrome: `CHROME=/ruta/chrome python3 engine/render.py ...`

## Arquitectura
- `engine/render.py`: episode.json → MP4. Por escena: abre HTML con Playwright, llama `window.setScene(sc)` y luego `window.seek(t)` por frame, screenshot JPEG q92 → ffmpeg (libx264 crf18 veryfast). Un mp4 por escena, concat con `-c copy`, audio con `-c:v copy`. Hacer **un render completo por iteración**; antes mira frames con `--preview`.
- `engine/pixel_intro.html`: escena pixel (canvas 270x480 escalado x4, `image-rendering: pixelated`). Fondo en espacio 135x240 (`setTransform(2,…)`), sprites al doble de resolución. Todo es función pura de `t` (`draw(t)`): sin estado entre frames.
- `engine/template.html`: escenas genéricas (title/map/portrait/roll d20) + subtítulos palabra por palabra.
- `episodes/<nombre>/episode.json`: escenas, `times` (override de `T` en el HTML), `lines` (subtítulos con inicio/fin), `sprites`, `audio`.
- `tools/make_kobold_v2.py` / `make_iguana_v4.py`: generan los sprites por código (PNG en `assets/sprites/native`, copiar a `episodes/*/sprites`). Kobolds con variantes `normal | _sing | _scared`.
- `tools/foundry_export_macro.js` + `tools/rank_moments.py`: exportar el chat de Foundry y rankear momentos (nat 20, nat 1, daño alto).

## Personajes (canon que dio Walter)
- **Kobolds** (rojos, cuernos, daga, todos idénticos salvo props): Julia (libro de cuentas + cucharón), Piedrín (barril, robusto), Braulio (mandolina), Chispa (antorcha + barril de pólvora), El Zurdito (catalejo), Pancho (martillo + tabla), Lola (soga). **Sobreviven solo Julia, Piedrín, Braulio**; Chispa, Zurdito, Pancho y Lola mueren.
- **Mr. Iguana**: humanoide ~90 cm (más pequeño que los kobolds), cuerpo rojo tipo dragón barbudo, **sombrero y capa AZULES**, libro de hechizos, bastón druida con cristal magenta. **Sin alas** en sprite. Referencia: lagarto mago rojo.
- **Dei**: draconido eléctrico, negro, 2 m, bardo; mata de un relámpago a Zurdito, Pancho y Lola. Chispa se sacrifica con explosivo. (Faltan detalles visuales: pedirlos.)

## Reglas aprendidas (no repetir errores)
- Los tiempos de la canción **los da Walter** (segundos exactos). No estimar a ojo: "Una mano levantó" ≈ 33 s; "barcos olvidados" termina ≈ 8 s; "recorríamos el mar" ≈ 14–15 s; "íbamos a acabar" ≈ 29 s; "Entonces él llegó" ≈ 30 s. El coro (~38.5 s) sigue estimado: confirmar.
- Quién canta debe verse claro (panel con nombre + boca animada), y los demás kobolds muestran miedo (sprite `_scared`) durante la caída del casco.
- Los nombres de los 7 se ven hasta que se agrupan (`T.kob`).
- Pixel art, no low-poly.
- Sin red a HuggingFace en algunos entornos: no depender de Whisper vía HF en la nube; el alineado automático queda pendiente.
- Audio de ejemplo `episodes/iguana_intro/audio.m4a` es una canción hecha con Suno (plan gratuito, uso no comercial). Walter quiere luego una canción original sin copyright (idea: chiptune generado por código + su voz).
- Antes de publicar, confirmar permiso/crédito del arte de referencia.

## Tareas pendientes (por prioridad)
1. Confirmar con Walter: segundo exacto del coro, origen del susurro (¿elfo invisible?).
2. Clip: Dei mata con relámpago a Zurdito/Pancho/Lola.
3. Clip: Chispa salva a Dei, susurro, el bardo lanza el cuerpo, explosión.
4. Clip: pelea con el dragón de cobre; Rayo de Escarcha / Ventisca.
5. Cierre "cuatro lugares vacíos" (ya existe en la escena final).
6. Alineado automático de subtítulos (faster-whisper local) y música de fondo.
7. Pipeline de sesión: chat de Foundry → ranking → guion → episode.json.
8. Canción original chiptune.

## Aurelia (proyecto aparte)
Ver `AURELIA_PLAN.md`. No mezclar con este repo en el código; es otra línea de trabajo.
