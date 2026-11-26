#!/usr/bin/env python3
"""Arma episodes/ep03_el_susurro/episode.json. Tiempos relativos (0 = "¡Fuego!"). El kenku y Dei hacen de tanques,
Mr. Iguana vuela disparando, los kobolds se esconden tras unas rocas. Uso: python3 tools/build_ep03.py"""
import json, os, re
from pathlib import Path
EP = Path("episodes/ep03_el_susurro"); L = json.load(open(EP / "lyrics.json")); DUR = 43.9
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
# escondidos tras las rocas (se asoman); Chispa sale corriendo a ayudar a Dei
HID = {0: (12, 428), 1: (32, 432), 2: (52, 428), 3: (26, 424)}
kob(0, "Julia",   [K(0, *HID[0], "scared"), K(36.8, *HID[0], "stiff")])
kob(1, "Piedrín", [K(0, *HID[1], "scared")])
kob(2, "Braulio", [K(0, *HID[2], "scared")])
kob(3, "Chispa",  [K(0, *HID[3], "scared"), K(11.4, *HID[3], "run"), K(12.9, 140, 392, "idle"), K(13.1, 140, 392, "lift"), K(15.0, 140, 392, "idle"),
                   K(34.0, 140, 392, "stiff"), K(42.0, 140, 392, "die")])
# los tres caídos en ep01, siguen tendidos
for i, (nm, pos) in zip((4, 5, 6), (("El Zurdito", (196, 414)), ("Pancho", (222, 422)), ("Lola", (176, 424)))):
    kob(i, nm, [K(0, *pos, "die", opts={}, flip=(i % 2 == 0))])
# tanques: kenku y Dei; Iguana vuela; Hans ladrón invisible
actors.append({"id": "kenku", "rig": "kenku", "variant": 0, "name": "Kenku", "keys": [
    K(0, 84, 386, "guard"), K(3.25, 84, 386, "block"), K(4.2, 84, 386, "guard"), K(16.3, 84, 386, "block"), K(17.2, 84, 386, "guard"), K(25.0, 84, 386, "idle")]})
actors.append({"id": "dei", "rig": "dei", "name": "Dei", "keys": [
    K(0, 172, 384, "idle"), K(4.2, 172, 384, "cast"), K(8.2, 172, 384, "idle"), K(9.9, 172, 384, "hurt"), K(10.5, 172, 384, "down"),
    K(13.1, 172, 384, "rise"), K(15.0, 172, 384, "idle")]})
actors.append({"id": "iguana", "rig": "iguana", "name": "Mr. Iguana", "keys": [
    K(0, 50, 316, "cast", float=392, fxcol=[130, 200, 255])]})
actors.append({"id": "hans", "rig": "hans", "variant": 0, "name": "Hans", "keys": [
    K(0, 208, 394, "idle"), K(6.0, 208, 394, "idle"), K(6.8, 208, 394, "vanish"), K(21.0, 208, 394, "sneak", opts={"alpha": 0.2}), K(26.5, 156, 394, "sneak", opts={"alpha": 0.2}),
    K(27.5, 156, 394, "idle", alpha=0.25), K(30.8, 156, 394, "idle", alpha=0.0)]})
DX, DY = 215, 322
actors.append({"id": "dragon", "rig": "dragon", "name": "Dragón", "keys": [
    K(0, DX, DY, "breathe", opts={"dur": 1.5}, firedx=-0.15, firedy=1.55, firelen=190), K(2.2, DX, DY, "hurt"), K(2.9, DX, DY, "bite"), K(4.4, DX, DY, "hurt"), K(5.2, DX, DY, "idle"),
    K(9.0, DX, DY, "bite"), K(10.6, DX, DY, "idle"), K(15.8, DX, DY, "bite"), K(17.4, DX, DY, "hurt"), K(18.2, DX, DY, "idle"), K(23.0, DX, DY, "roar"), K(25.0, DX, DY, "idle"), K(33.0, DX, DY, "idle")]})
ice = {"actor": "iguana", "anchor": "crystal"}
def beam(t, dur=1.0, id=1): return {"type": "beam", "t": t, "dur": dur, "from": ice, "to": {"actor": "dragon", "anchor": "eye"}, "id": id}
events = [
  {"type": "fade", "t": 0, "dur": 0.5, "from": "black"},
  {"type": "dome", "t": 0.7, "dur": 5.2, "x": 128, "y": 412, "r": 86}, {"type": "dome", "t": 15.8, "dur": 3.6, "x": 128, "y": 412, "r": 86},
  beam(1.6, 1.0, 1), beam(4.6, 1.0, 2), beam(7.4, 1.0, 3), beam(11.0, 1.0, 4), beam(16.6, 1.0, 5), beam(19.5, 1.0, 6), beam(22.0, 1.2, 7),
  {"type": "flash", "t": 2.3, "dur": 0.2, "a": 0.4},
  {"type": "flash", "t": 3.25, "dur": 0.3, "a": 0.7}, {"type": "shake", "t": 3.25, "dur": 0.5, "amp": 3},
  {"type": "bolt", "t": 4.6, "dur": 1.0, "from": {"actor": "dei", "anchor": "hand_R"}, "to": {"actor": "dragon", "anchor": "chest"}, "id": 8},
  {"type": "flash", "t": 4.6, "dur": 0.25, "a": 0.7}, {"type": "shake", "t": 4.8, "dur": 0.4, "amp": 2},
  {"type": "flash", "t": 9.35, "dur": 0.25, "a": 0.6}, {"type": "shake", "t": 9.35, "dur": 0.7, "amp": 4},
  {"type": "flash", "t": 16.15, "dur": 0.3, "a": 0.7}, {"type": "shake", "t": 16.15, "dur": 0.5, "amp": 3},
  {"type": "label", "t": 27.8, "dur": 2.6, "actor": "hans", "dy": 52, "text": "psst…"},
  {"type": "dim", "t": 26.5, "dur": 15.5, "a": 0.28, "fi": 2.0, "fo": 1.0},
  {"type": "dim", "t": 36.7, "dur": 2.4, "a": 0.55, "fi": 0.15, "fo": 1.2},
  {"type": "fade", "t": 42.4, "dur": 1.5, "to": "black"},
]
scene = {"type": "stage", "template": "stage.html", "duration": DUR, "sprites": sprites, "metaFile": f"{rel}/rig.json",
         "chip": {"text": "SESIÓN 1 · EP. 3", "t": 0.2, "dur": 2.6}, "title": {"text": "El susurro", "t": 0.4, "dur": 2.6},
         "bg": [{"t": 0, "mode": "dusk"}], "lines": lines, "actors": actors, "events": events,
         "props": [{"type": "rocks", "x": 28, "y": 448, "w": 74, "h": 42, "seed": 3}]}
json.dump({"fps": 30, "width": 1080, "height": 1920, "audio": "audio.m4a", "scenes": [scene]}, open(EP / "episode.json", "w"), ensure_ascii=False, indent=1)
print("ok", EP / "episode.json")
