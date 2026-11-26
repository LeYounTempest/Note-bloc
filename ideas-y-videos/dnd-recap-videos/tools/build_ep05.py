#!/usr/bin/env python3
"""ep05 'El Rayo de Hielo' (0 = "Mr. Iguana levantó una mano"). Uso: python3 tools/build_ep05.py"""
import json, os, re
from pathlib import Path
EP = Path("episodes/ep05_el_rayo_de_hielo"); L = json.load(open(EP / "lyrics.json")); DUR = 66.3
rel = os.path.relpath("assets/rig", EP)
chars = [d.name for d in sorted(Path("assets/rig").iterdir()) if d.is_dir()]
sprites = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in chars for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}
lines = []
for i, l in enumerate(L):
    t0 = l["start"]; t1 = min(l["end"], t0 + 4.5)
    if i + 1 < len(L) and L[i + 1]["start"] - t0 < 4.5: t1 = L[i + 1]["start"] - 0.02
    lines.append({"t0": round(max(0, t0), 2), "t1": round(t1, 2), "text": l["text"], "big": bool(re.fullmatch(r"¡[A-ZÁÉÍÓÚÑ ]+!", l["text"].strip())) or l["text"].startswith(("QUE ", "SOBRE")) or l["text"].startswith("¡POR")})
def K(t, x, y, anim="idle", **kw): return {"t": t, "x": x, "y": y, "anim": anim, **kw}
actors = []
def kob(i, name, keys): actors.append({"id": f"k{i}", "rig": "kobold", "variant": i, "name": name, "seed": i, "keys": keys})
HID = {0: (12, 428), 1: (32, 432), 2: (52, 428)}
kob(0, "Julia",   [K(0, *HID[0], "scared"), K(30.6, *HID[0], "sing", opts={"seed": 1}), K(37.0, *HID[0], "scared")])
kob(1, "Piedrín", [K(0, *HID[1], "scared"), K(30.6, *HID[1], "sing", opts={"seed": 2}), K(37.0, *HID[1], "scared")])
kob(2, "Braulio", [K(0, *HID[2], "scared"), K(30.6, *HID[2], "sing", opts={"seed": 3}), K(37.0, *HID[2], "scared")])
for i, (nm, pos) in zip((4, 5, 6, 3), (("El Zurdito", (196, 414)), ("Pancho", (222, 422)), ("Lola", (176, 424)), ("Chispa", None))):
    if pos: kob(i, nm, [K(0, *pos, "die", flip=(i % 2 == 0))])
actors.append({"id": "kenku", "rig": "kenku", "variant": 0, "name": "Kenku", "keys": [K(0, 84, 386, "idle")]})
actors.append({"id": "dei", "rig": "dei", "name": "Dei", "keys": [K(0, 150, 388, "stunned"), K(28.9, 150, 388, "idle")]})
ICE = [140, 210, 255]
actors.append({"id": "iguana", "rig": "iguana", "name": "Mr. Iguana", "keys": [
    K(0, 120, 404, "cast", fxcol=ICE), K(5.0, 120, 404, "cast", fxcol=ICE, aura=0.7),
    # desde la escarcha (8.1): carga el Rayo de Hielo, enojado, y vuelve a elevarse poco a poco
    K(8.1, 120, 404, "charge", fxcol=ICE, aura=0.7, charge=0.1), K(14.0, 120, 404, "charge", fxcol=ICE, aura=1.0, charge=0.45, float=410),
    K(20.0, 120, 388, "charge", fxcol=ICE, aura=1.3, charge=0.7, float=410), K(28.9, 120, 366, "charge", fxcol=ICE, aura=1.6, charge=0.9, float=410),
    K(36.45, 120, 352, "cast", fxcol=ICE, aura=2.0, charge=1.0, float=410), K(60.0, 120, 352, "cast", fxcol=ICE, aura=1.2, float=410)]})
DX, DY = 215, 322
actors.append({"id": "dragon", "rig": "dragon", "name": "Dragón", "keys": [
    K(0, DX, DY, "idle"), K(13.6, DX, DY, "breathe", opts={"dur": 0.9}, firedx=-0.15, firedy=1.55, firelen=60), K(15.0, DX, DY, "idle"),
    K(16.0, DX, DY, "idle", tint=0.3, tintc="130,160,200"), K(19.4, DX, DY, "fly", tint=0.3, tintc="130,160,200"), K(28.9, 190, 226, "freezing", opts={"dur": 19}, float=330),
    K(48.1, 190, 226, "frozen", float=330), K(58.6, 190, 226, "frozen", float=330, vis=False)]})
ice = {"actor": "iguana", "anchor": "crystal"}; chest = {"actor": "dragon", "anchor": "chest"}
events = [
  {"type": "fade", "t": 0, "dur": 0.5, "from": "black"},
  {"type": "dim", "t": 0, "dur": 5.0, "a": 0.3, "fi": 0.05, "fo": 3.0},
  {"type": "frost", "kind": "seafreeze", "t": 5.0}, {"type": "frost", "kind": "ice", "t": 8.1, "t1": 40.0},
  {"type": "shake", "t": 5.0, "dur": 0.5, "amp": 1}, {"type": "shake", "t": 8.1, "dur": 0.4, "amp": 1},
  {"type": "beam", "t": 28.9, "dur": 1.3, "from": ice, "to": chest, "w": 4, "id": 1}, {"type": "flash", "t": 28.9, "dur": 0.3, "a": 0.5},
  {"type": "flash", "t": 32.2, "dur": 0.2, "a": 0.3}, {"type": "flash", "t": 35.1, "dur": 0.3, "a": 0.4},
  {"type": "flash", "t": 37.0, "dur": 0.6, "a": 0.9}, {"type": "shake", "t": 37.0, "dur": 0.9, "amp": 4},
  {"type": "beam", "t": 37.0, "dur": 13.8, "from": ice, "to": chest, "w": 8, "amp": 3, "id": 2, "cols": ["rgba(160,220,255,.5)", "#b8e8ff", "#ffffff"]},
  {"type": "crack", "t": 54.2, "ids": [0, 1]}, {"type": "crack", "t": 55.2, "ids": [2, 3]}, {"type": "crack", "t": 56.7, "ids": [4, 5]},
  {"type": "flash", "t": 54.2, "dur": 0.15, "a": 0.3}, {"type": "flash", "t": 55.2, "dur": 0.15, "a": 0.3}, {"type": "flash", "t": 56.7, "dur": 0.2, "a": 0.4},
  {"type": "shake", "t": 54.2, "dur": 0.25, "amp": 1}, {"type": "shake", "t": 55.2, "dur": 0.25, "amp": 1}, {"type": "shake", "t": 56.7, "dur": 0.35, "amp": 2},
  {"type": "shatter", "t": 58.6}, {"type": "flash", "t": 58.6, "dur": 0.7, "a": 1.0}, {"type": "shake", "t": 58.6, "dur": 1.6, "amp": 5},
  {"type": "splash", "t": 59.4, "dur": 1.6, "x": 120, "y": 306, "spread": 150, "h": 30}, {"type": "splash", "t": 60.0, "dur": 1.6, "x": 200, "y": 306, "spread": 130, "h": 30},
  {"type": "fade", "t": 64.2, "dur": 2.1, "to": "black"},
]
scene = {"type": "stage", "template": "stage.html", "duration": DUR, "sprites": sprites, "metaFile": f"{rel}/rig.json",
         "chip": {"text": "SESIÓN 1 · EP. 5", "t": 0.2, "dur": 2.6}, "title": {"text": "El Rayo de Hielo", "t": 0.4, "dur": 2.8},
         "bg": [{"t": 0, "mode": "dusk"}], "lines": lines, "actors": actors, "events": events,
         "props": [{"type": "rocks", "x": 28, "y": 448, "w": 74, "h": 42, "seed": 3}]}
json.dump({"fps": 30, "width": 1080, "height": 1920, "audio": "audio.m4a", "scenes": [scene]}, open(EP / "episode.json", "w"), ensure_ascii=False, indent=1)
print("ok", EP / "episode.json")
