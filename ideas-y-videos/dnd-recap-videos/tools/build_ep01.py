#!/usr/bin/env python3
"""Arma episodes/ep01_dei_el_kenku_y_el_elfo/episode.json (escenario 'stage.html' + audio + subtítulos de la letra).
Tiempos relativos al episodio (0 = "¡Jefe! ¡Hay ladrones...", ver lyrics.json). Uso: python3 tools/build_ep01.py"""
import json, os, re
from pathlib import Path

EP = Path("episodes/ep01_dei_el_kenku_y_el_elfo")
L = json.load(open(EP / "lyrics.json")); DUR = 58.9
rel = os.path.relpath("assets/rig", EP)
chars = [d.name for d in sorted(Path("assets/rig").iterdir()) if d.is_dir()]
sprites = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in chars for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}

# ── subtítulos (de la letra) ──
lines = []
for i, l in enumerate(L):
    t0 = l["start"]; t1 = min(l["end"], t0 + 4.5)
    if i + 1 < len(L): t1 = min(t1, L[i + 1]["start"] - 0.02) if L[i + 1]["start"] - t0 < 4.5 else t1
    lines.append({"t0": round(t0, 2), "t1": round(t1, 2), "text": l["text"].replace("“", "").replace("”", ""), "big": bool(re.fullmatch(r"¡[A-ZÁÉÍÓÚÑ ]+!", l["text"].strip()))})

def K(t, x, y, anim="idle", **kw): return {"t": t, "x": x, "y": y, "anim": anim, **kw}

# posiciones: pies en px de canvas (270x480)
S0 = {0: (24, 392), 1: (46, 404), 2: (68, 394), 3: (90, 406)}               # sobrevivientes + Chispa
actors = []
def kob(i, name, keys): actors.append({"id": f"k{i}", "rig": "kobold", "variant": i, "name": name, "seed": i, "keys": keys})
CAMP = {0: (84, 404), 1: (104, 416), 2: (172, 404), 3: (192, 416)}
kob(0, "Julia", [K(0, *S0[0], "idle"), K(3.3, *S0[0], "sing", opts={"seed": 1}), K(6.3, *S0[0], "idle"), K(9.6, *S0[0], "scared"), K(18.9, *S0[0], "idle"), K(22.5, *S0[0], "scared"), K(31, *S0[0], "idle"), K(36.3, *CAMP[0], "idle", jump=True, flip=False)])
kob(1, "Piedrín", [K(0, *S0[1], "idle"), K(6.3, *S0[1], "sing", opts={"seed": 2}), K(9.6, *S0[1], "scared"), K(18.9, *S0[1], "idle"), K(22.5, *S0[1], "scared"), K(31, *S0[1], "idle"), K(36.3, *CAMP[1], "idle", jump=True, flip=False)])
kob(2, "Braulio", [K(0, *S0[2], "sing", opts={"seed": 3}), K(3.3, *S0[2], "idle"), K(9.6, *S0[2], "scared"), K(18.9, *S0[2], "idle"), K(22.5, *S0[2], "scared"), K(31, *S0[2], "idle"), K(36.3, *CAMP[2], "idle", jump=True, flip=True)])
kob(3, "Chispa", [K(0, *S0[3], "idle"), K(9.6, *S0[3], "scared"), K(18.9, *S0[3], "idle"), K(22.5, *S0[3], "scared"), K(31, *S0[3], "idle"), K(36.3, *CAMP[3], "idle", jump=True, flip=True)])
# los tres hermanos: van hacia el bardo y mueren (¡UNO! 12.9, ¡DOS! 13.7, ¡TRES! 14.4)
kob(4, "El Zurdito", [K(0, 30, 360, "idle"), K(6.3, 30, 360, "walk", opts={"speed": 1.3}), K(9.4, 156, 388, "idle"), K(9.8, 156, 388, "scared"), K(12.9, 156, 388, "die"), K(36.0, 156, 388, "die", vis=False)])
kob(5, "Pancho", [K(0, 54, 366, "idle"), K(6.3, 54, 366, "walk", opts={"speed": 1.3}), K(9.4, 172, 402, "idle"), K(9.8, 172, 402, "scared"), K(13.7, 172, 402, "die"), K(36.0, 172, 402, "die", vis=False)])
kob(6, "Lola", [K(0, 78, 360, "idle"), K(6.3, 78, 360, "walk", opts={"speed": 1.3}), K(9.4, 140, 400, "idle"), K(9.8, 140, 400, "scared"), K(14.4, 140, 400, "die"), K(36.0, 140, 400, "die", vis=False)])
actors.append({"id": "iguana", "rig": "iguana", "name": "Mr. Iguana", "keys": [K(0, 112, 384, "idle"), K(18.9, 112, 384, "cast", fxcol=[240, 90, 210]), K(22.5, 112, 384, "cast", fxcol=[130, 200, 255]), K(31, 112, 384, "idle"), K(36.3, 138, 436, "idle", jump=True)]})
actors.append({"id": "dei", "rig": "dei", "name": "Dei", "keys": [
    K(0, 252, 350, "play"), K(9.6, 252, 350, "cast"), K(15.2, 252, 350, "idle"), K(22.5, 252, 350, "hurt"), K(24.2, 252, 350, "tumble"),
    K(27.0, 252, 350, "tumble", rot=0), K(29.7, 350, 150, "tumble", rot=1000), K(36.0, 350, 150, "tumble", vis=False)]})
actors.append({"id": "kenku", "rig": "kenku", "variant": 0, "name": "Kenku", "keys": [
    K(0, 226, 366, "idle"), K(22.5, 226, 366, "guard"), K(31, 226, 366, "idle"), K(32, 226, 366, "walk"), K(35.2, 330, 366, "walk"), K(36.0, 330, 366, "idle", vis=False)]})
actors.append({"id": "hans", "rig": "hans", "variant": 0, "name": "Hans", "keys": [
    K(3.0, 300, 380, "walk", vis=True), K(5.6, 196, 380, "toast"), K(9.6, 196, 380, "idle"), K(22.5, 196, 380, "scared"), K(31, 196, 380, "idle"), K(32.5, 196, 380, "walk"), K(35.4, 330, 380, "walk"), K(36.0, 330, 380, "idle", vis=False)]})

events = [
  {"type": "fade", "t": 0, "dur": 0.8, "from": "black"},
  {"type": "alert", "t": 0.3, "dur": 2.4, "actor": "k2"},
  {"type": "label", "t": 0.4, "dur": 2.6, "actor": "dei", "text": "Dei"},
  {"type": "label", "t": 0.4, "dur": 2.6, "actor": "kenku", "text": "Kenku"},
  {"type": "label", "t": 3.6, "dur": 2.6, "actor": "hans", "text": "Hans"},
  {"type": "skyflash", "t": 9.6, "dur": 0.3, "a": 0.9}, {"type": "flash", "t": 9.6, "dur": 0.2, "a": 0.5},
  {"type": "bolt", "t": 12.9, "dur": 0.55, "from": {"actor": "dei", "anchor": "hand_R"}, "to": {"actor": "k4", "dy": -16}, "id": 1},
  {"type": "bolt", "t": 13.7, "dur": 0.55, "from": {"actor": "dei", "anchor": "hand_L"}, "to": {"actor": "k5", "dy": -16}, "id": 2},
  {"type": "bolt", "t": 14.4, "dur": 0.55, "from": {"actor": "dei", "anchor": "hand_R"}, "to": {"actor": "k6", "dy": -16}, "id": 3},
  {"type": "flash", "t": 12.9, "dur": 0.25, "a": 0.8}, {"type": "flash", "t": 13.7, "dur": 0.25, "a": 0.8}, {"type": "flash", "t": 14.4, "dur": 0.3, "a": 0.9},
  {"type": "shake", "t": 12.9, "dur": 0.4, "amp": 2}, {"type": "shake", "t": 13.7, "dur": 0.4, "amp": 2}, {"type": "shake", "t": 14.4, "dur": 0.6, "amp": 3},
  {"type": "blizzard", "t": 22.0, "t1": 31.0},
  {"type": "shake", "t": 22.5, "dur": 0.5, "amp": 2},
  {"type": "fade", "t": 35.2, "dur": 1.0, "to": "black"}, {"type": "fade", "t": 36.3, "dur": 1.0, "from": "black"},
  {"type": "label", "t": 48.4, "dur": 8.0, "x": 92, "y": 316, "text": "El Zurdito"}, {"type": "label", "t": 48.4, "dur": 8.0, "x": 135, "y": 316, "text": "Pancho"},
  {"type": "label", "t": 48.4, "dur": 8.0, "x": 178, "y": 316, "text": "Lola"},
  {"type": "fade", "t": 56.6, "dur": 2.2, "to": "black"},
]
scene = {"type": "stage", "template": "stage.html", "duration": DUR, "sprites": sprites, "metaFile": f"{rel}/rig.json",
         "title": {"text": "Dei, el kenku y el elfo", "t": 0.6, "dur": 3.4}, "chip": {"text": "SESIÓN 1 · EP. 1", "t": 0.2, "dur": 3.8},
         "bg": [{"t": 0, "mode": "dusk"}, {"t": 36.3, "mode": "night"}],
         "camp": {"x": 135, "y": 400, "spots": [{"x": 92, "y": 372, "item": "spyglass", "t": 47.9}, {"x": 135, "y": 372, "item": "hammer", "t": 47.9}, {"x": 178, "y": 372, "item": "rope", "t": 47.9}]},
         "lines": lines, "actors": actors, "events": events}
ep = {"fps": 30, "width": 1080, "height": 1920, "audio": "audio.m4a", "scenes": [scene]}
json.dump(ep, open(EP / "episode.json", "w"), ensure_ascii=False, indent=1)
print("ok ->", EP / "episode.json", len(lines), "líneas")
