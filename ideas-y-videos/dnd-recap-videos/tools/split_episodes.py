#!/usr/bin/env python3
"""Arma los episodios (uno o más tramos de la canción) -> episodes/<id>/{audio.m4a,lyrics.json} + episodes/episodes.json.
Uso: python3 tools/split_episodes.py [episodes/me_iguana_full]
Cada tramo (inicio, fin) se corta con fades y se concatena; la letra se reescribe con tiempos relativos al episodio."""
import json, subprocess, sys, tempfile
from pathlib import Path
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "episodes/me_iguana_full")
L = json.load(open(SRC / "lyrics.json"))
EPISODES = [
 ("ep01_dei_el_kenku_y_el_elfo", "Dei, el kenku y el elfo",
  "Llegan Dei, el kenku y el elfo con vino; Dei mata con relámpagos; Mr. Iguana responde con Ventisca; duelo por los caídos",
  [(95.6, 154.5)]),
 ("ep02_el_dragon_de_cobre", "El dragón de cobre",
  "El océano ruge y el dragón adulto emerge y abre las alas; todos deben dejar de pelear entre ellos",
  [(154.5, 169.5)]),
 ("ep03_el_susurro", "El susurro",
  "Todos pelean junto al dragón: fuego, escudos, hielo; el elfo se hace invisible; el dragón derriba a Dei; Chispa va a ayudarlo y el elfo invisible susurra: muere al instante",
  [(169.5, 213.4)]),
 ("ep04_el_cuerpo_es_un_arma", "El cuerpo es un arma",
  "Dei usa el cuerpo de Chispa como arma contra el dragón; explosión; algo se rompe dentro de Mr. Iguana",
  [(213.4, 251.0)]),
 ("ep05_siempre_seremos_ocho", "Siempre seremos ocho",
  "Mr. Iguana mata al dragón de cobre (Rayo de Hielo); cuenta a su familia; cierre 'siempre seremos ocho'",
  [(251.0, 317.3), (332.1, 360.3), (383.4, 408.4)]),
]
FI, FO = 0.15, 0.6
meta = []; tmp = Path(tempfile.mkdtemp())
for eid, title, event, segs in EPISODES:
    d = Path("episodes") / eid; d.mkdir(parents=True, exist_ok=True)
    parts, lines, off = [], [], 0.0
    for k, (a, b) in enumerate(segs):
        dur = b - a; p = tmp / f"{eid}_{k}.wav"
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(SRC / "audio.m4a"), "-map", "0:a",
                               "-af", f"afade=t=in:d={FI},afade=t=out:st={dur-FO:.2f}:d={FO}", "-ar", "48000", "-ac", "2", str(p)])
        parts.append(p)
        for l in L:
            if a - 0.1 <= l["start"] < b - 0.1:  # tolerancia: los límites coinciden con inicios de línea
                lines.append({**l, "start": round(l["start"] - a + off, 2), "end": round(min(l["end"], l["start"] + 4.5, b) - a + off, 2), "seg": k})
        off += dur
    lst = tmp / f"{eid}.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "aac", "-b:a", "192k", str(d / "audio.m4a")])
    json.dump(lines, open(d / "lyrics.json", "w"), ensure_ascii=False, indent=1)
    meta.append({"id": eid, "title": title, "event": event, "duration": round(off, 1), "segments": segs,
                 "singers": sorted({l["singer"] for l in lines}), "lines": len(lines)})
json.dump(meta, open("episodes/episodes.json", "w"), ensure_ascii=False, indent=1)
for m in meta: print(f"{m['id']:32s} {m['duration']:6.1f}s  {m['segments']}")
