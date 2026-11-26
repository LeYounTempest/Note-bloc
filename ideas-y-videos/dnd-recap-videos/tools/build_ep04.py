#!/usr/bin/env python3
"""Arma episodes/ep04_el_cuerpo_es_un_arma/episode.json (0 = "Entonces escuchó un susurro").
Chispa muere; Dei usa su cuerpo como arma; explosión; algo se rompe en Mr. Iguana. Uso: python3 tools/build_ep04.py"""
import json, os, re
from pathlib import Path
EP = Path("episodes/ep04_el_cuerpo_es_un_arma"); L = json.load(open(EP / "lyrics.json")); DUR = 54.0
rel = os.path.relpath("assets/rig", EP)
chars = [d.name for d in sorted(Path("assets/rig").iterdir()) if d.is_dir()]
sprites = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in chars for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}
lines = []
for i, l in enumerate(L):
    t0 = l["start"]; t1 = min(l["end"], t0 + 4.5)
    if i + 1 < len(L) and L[i + 1]["start"] - t0 < 4.5: t1 = L[i + 1]["start"] - 0.02
    lines.append({"t0": round(max(0, t0), 2), "t1": round(t1, 2), "text": l["text"], "big": bool(re.fullmatch(r"¡[A-ZÁÉÍÓÚÑ ]+!", l["text"].strip()))})
def K(t, x, y, anim="idle", **kw): return {"t": t, "x": x, "y": y, "anim": anim, **kw}
actors = []
def kob(i, name, keys): actors.append({"id": f"k{i}", "rig": "kobold", "variant": i, "name": name, "seed": i, "keys": keys})
HID = {0: (12, 428), 1: (32, 432), 2: (52, 428)}
kob(0, "Julia",   [K(0, *HID[0], "scared"), K(31.5, *HID[0], "stiff")])
kob(1, "Piedrín", [K(0, *HID[1], "scared"), K(31.5, *HID[1], "stiff")])
kob(2, "Braulio", [K(0, *HID[2], "scared"), K(31.5, *HID[2], "stiff")])
# Chispa: el susurro lo mata; luego su cuerpo es arma
CX, CY = 140, 392
kob(3, "Chispa", [K(0, CX, CY, "idle"), K(6.5, CX, CY, "stiff"), K(14.5, CX, CY, "die"),
                  K(20.0, CX, CY, "die"), K(22.0, 150, 322, "die"), K(26.4, 150, 322, "die"),
                  K(27.1, 156, 314, "die", rot=0), K(28.65, 182, 272, "die", rot=540), K(28.7, 182, 272, "die", vis=False)])
for i, (nm, pos) in zip((4, 5, 6), (("El Zurdito", (196, 414)), ("Pancho", (222, 422)), ("Lola", (176, 424)))):
    kob(i, nm, [K(0, *pos, "die", flip=(i % 2 == 0))])
actors.append({"id": "kenku", "rig": "kenku", "variant": 0, "name": "Kenku", "keys": [K(0, 84, 386, "guard"), K(28.7, 84, 386, "block"), K(30, 84, 386, "idle")]})
actors.append({"id": "dei", "rig": "dei", "name": "Dei", "keys": [
    K(0, 172, 384, "idle"), K(16.4, 172, 384, "idle"), K(17.6, 172, 384, "walk"), K(19.2, 150, 388, "idle"), K(20.0, 150, 388, "hoist"),
    K(26.2, 150, 388, "throw"), K(28.0, 150, 388, "idle"), K(30.0, 150, 388, "stunned")]})
actors.append({"id": "iguana", "rig": "iguana", "name": "Mr. Iguana", "keys": [
    K(0, 50, 316, "cast", float=392, fxcol=[130, 200, 255]), K(28.8, 50, 316, "idle", float=392), K(40.0, 50, 316, "idle", float=392),
    K(43.9, 50, 384, "idle"), K(47.5, 50, 384, "hollow")]})
actors.append({"id": "hans", "rig": "hans", "variant": 0, "name": "Hans", "keys": [
    K(0, 208, 394, "sneak", opts={"alpha": 0.2}), K(1.6, 160, 394, "sneak", opts={"alpha": 0.2}), K(2.0, 160, 394, "idle", alpha=0.28), K(3.3, 160, 394, "idle", alpha=0.0)]})
DX, DY = 215, 322
actors.append({"id": "dragon", "rig": "dragon", "name": "Dragón", "keys": [
    K(0, DX, DY, "idle"), K(10.0, DX, DY, "breathe", opts={"dur": 1.2}, firedx=-0.15, firedy=1.55, firelen=190), K(11.4, DX, DY, "idle"),
    K(28.7, DX, DY, "hurt"), K(29.6, DX, DY, "idle"), K(40.0, DX, DY, "idle")]})
ice = {"actor": "iguana", "anchor": "crystal"}
def beam(t, dur=1.0, id=1): return {"type": "beam", "t": t, "dur": dur, "from": ice, "to": {"actor": "dragon", "anchor": "eye"}, "id": id}
events = [
  {"type": "fade", "t": 0, "dur": 0.5, "from": "black"},
  {"type": "dim", "t": 0, "dur": 54, "a": 0.2, "fi": 0.1, "fo": 0.1},
  {"type": "label", "t": 1.4, "dur": 2.4, "actor": "hans", "dy": 52, "text": "psst…"},
  beam(2.0, 0.9, 1), beam(7.0, 0.9, 2), beam(11.5, 0.9, 3), beam(16.0, 0.9, 4), beam(23.0, 0.9, 5),
  {"type": "dim", "t": 9.1, "dur": 3.4, "a": 0.55, "fi": 0.12, "fo": 1.6},
  {"type": "flash", "t": 14.5, "dur": 0.2, "a": 0.25},
  {"type": "dome", "t": 10.0, "dur": 2.4, "x": 128, "y": 412, "r": 86},
  {"type": "shake", "t": 10.3, "dur": 0.4, "amp": 2},
  {"type": "explosion", "t": 28.7, "dur": 2.0, "x": 182, "y": 272, "r": 48},
  {"type": "flash", "t": 28.7, "dur": 0.35, "a": 1.0}, {"type": "shake", "t": 28.7, "dur": 1.2, "amp": 5},
  {"type": "dim", "t": 29.8, "dur": 24.2, "a": 0.32, "fi": 1.5, "fo": 0.5},
  {"type": "fade", "t": 51.8, "dur": 2.2, "to": "black"},
]
scene = {"type": "stage", "template": "stage.html", "duration": DUR, "sprites": sprites, "metaFile": f"{rel}/rig.json",
         "chip": {"text": "SESIÓN 1 · EP. 4", "t": 0.2, "dur": 2.6}, "title": {"text": "El cuerpo es un arma", "t": 0.4, "dur": 2.8},
         "bg": [{"t": 0, "mode": "dusk"}], "lines": lines, "actors": actors, "events": events,
         "props": [{"type": "rocks", "x": 28, "y": 448, "w": 74, "h": 42, "seed": 3}]}
json.dump({"fps": 30, "width": 1080, "height": 1920, "audio": "audio.m4a", "scenes": [scene]}, open(EP / "episode.json", "w"), ensure_ascii=False, indent=1)
print("ok", EP / "episode.json")
