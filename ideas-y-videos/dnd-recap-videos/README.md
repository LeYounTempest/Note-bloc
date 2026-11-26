# dnd-recap-videos

Resúmenes animados de las sesiones de D&D (Forge VTT / Foundry), en formato reel vertical.

## Idea
Convertir cada sesión (3-4 h) en una serie de videos cortos: 1 video principal de 60-90 s + 2-4 clips de 15-30 s con los mejores momentos. Narración con la voz del autor, animación por código, subtítulos palabra por palabra.

## Estilo visual
- Terminal/fondo oscuro con grilla y partículas como referencia (reels tipo "repo + guía").
- Mapa de la escena con travelling, retratos/tokens con parallax.
- d20 rodando, barras de HP, textos de crítico/pifia.
- Plantilla fija (intro, subtítulos, música) para que cada clip nuevo sea solo guion + arte + audio.

## Flujo por sesión
1. Exportar el chat log de Foundry (clic derecho en el chat > Export) + notas/journals.
2. Rankear momentos por drama (nat 20, nat 1, kills, daño masivo) y elegir 3-5 clips.
3. Guion + storyboard (gancho, conflicto, remate / cliffhanger).
4. Grabar la voz (una sola tanda por sesión).
5. Sincronizar audio (tiempos palabra por palabra), animar y renderizar MP4 vertical 1080x1920.
6. Numerar como serie ("Sesión N, clip M").

## Assets a reunir (Forge Assets Library)
- Tokens y retratos de personajes, NPCs y monstruos.
- Mapas de las escenas.
- Chat log exportado, journals y notas.

## Opcional
- Si graban la partida en audio (Discord): transcripción para detectar momentos hablados.

## Pendiente
- [ ] Elegir sesión piloto
- [ ] Reunir assets y chat log
- [ ] Definir paleta y estilo según la ambientación
- [ ] Primer guion + storyboard

## Esqueleto de render (ya funciona)
```
engine/template.html   escenas: title, map, portrait, roll (d20), subtítulos palabra por palabra
engine/render.py       episode.json -> MP4 vertical 1080x1920 @30fps (Playwright + ffmpeg)
episodes/demo/         episodio de ejemplo (19 s)
tools/foundry_export_macro.js   macro para exportar el chat de Foundry/Forge a chatlog.json
tools/rank_moments.py  rankea nat 20, nat 1 y daño alto del chatlog.json
setup.sh               dependencias (Python, ffmpeg, Chrome)
```
Uso: `./setup.sh && python3 engine/render.py episodes/demo/episode.json out/demo.mp4`
- Vista previa rápida de un cuadro por escena: añade `--preview carpeta/`. Renderizar solo una escena: `--only N`.
- Imágenes propias: en `image` de `map` y `portrait` (rutas relativas al episode.json).
- Subtítulos sincronizados a tu voz: `words` por escena (`t`, `d`, `w`, relativos a la escena), p. ej. desde faster-whisper/WhisperX. Sin `words`, usa `narration` repartido de forma uniforme.
- Audio: `"audio": "voz.wav"` en el episode.json.
- Pendiente: alineado automático con Whisper, música de fondo, más tipos de escena (combate, diálogo), exportar clips cortos.


## Estado actual
- Piloto "Mr. Iguana" (intro de la canción, 46 s) en `episodes/iguana_intro/` — render con `python3 engine/render.py episodes/iguana_intro/episode.json out/mr_iguana_intro.mp4`.
- Sprites pixel art generados por código en `tools/` (kobolds con expresiones normal/cantando/asustado, Mr. Iguana).
- **Instrucciones para Claude Code: ver `CLAUDE.md`** (arquitectura, canon de personajes, reglas aprendidas, pendientes).
