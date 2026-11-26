#!/usr/bin/env python3
"""Arma episodes/ep02_el_dragon_de_cobre/episode.json. Tiempos relativos al episodio (0 = "Entonces el océano rugió").
Uso: python3 tools/build_ep02.py"""
import json, os, re
from pathlib import Path
EP = Path("episodes/ep02_el_dragon_de_cobre"); L = json.load(open(EP / "lyrics.json")); DUR = 15.0
rel = os.path.relpath("assets/rig", EP)
chars = [d.name for d in sorted(Path("assets/rig").iterdir()) if d.is_dir()]
sprites = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in chars for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}
lines = []
for i, l in enumerate(L):
    t0 = l["start"]; t1 = min(l["end"], t0 + 4.5)
    if i + 1 < len(L) and L[i + 1]["start"] - t0 < 4.5: t1 = L[i + 1]["start"] - 0.02
    lines.append({"t0": round(max(0, t0), 2), "t1": round(t1, 2), "text": l["text"], "big": bool(re.fullmatch(r"¡[A-ZÁÉÍÓÚÑ ]+!", l["text"].strip()))})
def K(t, x, y, anim="idle", **kw): return {"t": t, "x": x, "y": y, "anim": anim, **kw}
S0 = {0: (24, 392), 1: (46, 404), 2: (68, 394), 3: (90, 406)}
actors = []
def kob(i, name, keys): actors.append({"id": f"k{i}", "rig": "kobold", "variant": i, "name": name, "seed": i, "keys": keys})
kob(0, "Julia",   [K(0, *S0[0], "sing", opts={"seed": 1}), K(3.4, *S0[0], "scared"), K(9.9, *S0[0], "sing", opts={"seed": 2}), K(14.4, *S0[0], "scared")])
kob(1, "Piedrín", [K(0, *S0[1], "idle"), K(3.5, *S0[1], "scared")])
kob(2, "Braulio", [K(0, *S0[2], "idle"), K(3.5, *S0[2], "scared")])
kob(3, "Chispa",  [K(0, *S0[3], "idle"), K(3.5, *S0[3], "scared")])
actors.append({"id": "iguana", "rig": "iguana", "name": "Mr. Iguana", "keys": [K(0, 112, 384, "idle")]})
actors.append({"id": "kenku", "rig": "kenku", "variant": 0, "name": "Kenku", "keys": [K(0, 226, 366, "idle"), K(6.5, 226, 366, "guard"), K(9.9, 226, 366, "idle")]})
actors.append({"id": "hans", "rig": "hans", "variant": 0, "name": "Hans", "keys": [K(0, 196, 380, "idle"), K(3.5, 196, 380, "scared"), K(9.9, 196, 380, "idle")]})
actors.append({"id": "dei", "rig": "dei", "name": "Dei", "keys": [K(9.6, 330, 350, "walk"), K(11.8, 252, 350, "idle")]})
DX, DY = 135, 322
actors.append({"id": "dragon", "rig": "dragon", "name": "Dragón de cobre", "keys": [
    K(3.5, DX, DY + 140, "emerge", clipY=306), K(6.2, DX, DY, "emerge", clipY=306), K(6.5, DX, DY, "roar"), K(9.9, DX, DY, "idle"), K(12.8, DX, DY, "roar", opts={}) ]})
events = [
  {"type": "fade", "t": 0, "dur": 0.7, "from": "black"},
  {"type": "shake", "t": 0.2, "dur": 3.2, "amp": 1}, {"type": "shake", "t": 3.5, "dur": 1.8, "amp": 3}, {"type": "shake", "t": 6.5, "dur": 0.9, "amp": 2}, {"type": "shake", "t": 12.8, "dur": 0.9, "amp": 2},
  {"type": "splash", "t": 3.5, "dur": 1.8, "x": 135, "y": 308, "spread": 130, "h": 70}, {"type": "splash", "t": 4.6, "dur": 1.6, "x": 90, "y": 308, "spread": 90, "h": 50},
  {"type": "label", "t": 6.8, "dur": 3.2, "x": 52, "y": 168, "text": "Dragón de cobre"},
  {"type": "fade", "t": 13.7, "dur": 1.3, "to": "black"},
]
scene = {"type": "stage", "template": "stage.html", "duration": DUR, "sprites": sprites, "metaFile": f"{rel}/rig.json",
         "chip": {"text": "SESIÓN 1 · EP. 2", "t": 0.2, "dur": 3.0}, "title": {"text": "El dragón de cobre", "t": 0.5, "dur": 3.0},
         "bg": [{"t": 0, "mode": "dusk"}], "lines": lines, "actors": actors, "events": events}
json.dump({"fps": 30, "width": 1080, "height": 1920, "audio": "audio.m4a", "scenes": [scene]}, open(EP / "episode.json", "w"), ensure_ascii=False, indent=1)
print("ok", EP / "episode.json")
