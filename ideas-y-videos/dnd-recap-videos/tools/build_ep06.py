#!/usr/bin/env python3
"""ep06 'Siempre seremos ocho' (0 = "Después..."). Uso: python3 tools/build_ep06.py"""
import json, os, re
from pathlib import Path
EP = Path("episodes/ep06_siempre_seremos_ocho"); L = json.load(open(EP / "lyrics.json")); DUR = 53.2
rel = os.path.relpath("assets/rig", EP)
chars = [d.name for d in sorted(Path("assets/rig").iterdir()) if d.is_dir()]
sprites = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in chars for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}
lines = []
for i, l in enumerate(L):
    t0 = l["start"]; t1 = min(l["end"], t0 + 4.5)
    if i + 1 < len(L) and L[i + 1]["start"] - t0 < 4.5: t1 = L[i + 1]["start"] - 0.02
    lines.append({"t0": round(max(0, t0), 2), "t1": round(t1, 2), "text": l["text"], "big": False})
def K(t, x, y, anim="idle", **kw): return {"t": t, "x": x, "y": y, "anim": anim, **kw}
actors = []
P = {"k0": (84, 408), "k1": (104, 420), "k2": (172, 408)}
def kob(i, name, keys, **kw): actors.append({"id": f"k{i}", "rig": "kobold", "variant": i, "name": name, "seed": i, "keys": keys, **kw})
def sing(t0, t1, pos, seed): return [K(t0, *pos, "sing", opts={"seed": seed}), K(t1, *pos, "idle")]
# k0 Julia (Female), k1 Piedrín (Male 2), k2 Braulio (Male 1)
kob(0, "Julia",   [K(0, *P["k0"], "idle")] + sing(7.9, 8.4, P["k0"], 1) + sing(15.6, 22.7, P["k0"], 2) + sing(33.3, 39.2, P["k0"], 3) + sing(39.9, 46.5, P["k0"], 4))
kob(1, "Piedrín", [K(0, *P["k1"], "idle")] + sing(7.2, 7.9, P["k1"], 5) + sing(25.6, 28.0, P["k1"], 6) + sing(30.8, 33.0, P["k1"], 7) + sing(39.9, 46.5, P["k1"], 8))
kob(2, "Braulio", [K(0, *P["k2"], "idle")] + sing(6.4, 7.2, P["k2"], 9) + sing(22.7, 25.4, P["k2"], 10) + sing(28.2, 30.6, P["k2"], 11) + sing(39.9, 46.5, P["k2"], 12))
# 'Y nadie más' (8.4-15.6): los tres cantan
for a in actors[:3]:
    a["keys"] = sorted(a["keys"] + [K(8.4, *a["keys"][0].copy().get("x") and (a["keys"][0]["x"], a["keys"][0]["y"]), "sing", opts={"seed": 20 + a["variant"]}), K(15.4, a["keys"][0]["x"], a["keys"][0]["y"], "idle")], key=lambda k: k["t"])
# fantasmas de los cuatro caídos, sentados en sus lugares
SPOTS = [(80, 378, 4, "El Zurdito", "spyglass"), (115, 378, 5, "Pancho", "hammer"), (150, 378, 6, "Lola", "rope"), (185, 378, 3, "Chispa", "barrel")]
for x, y, v, nm, _ in SPOTS:
    kob(v, nm, [K(0, x, y, "idle", alpha=0.0), K(39.2, x, y, "idle", alpha=0.0), K(42.5, x, y, "idle", alpha=0.5), K(44.9, x, y, "idle", alpha=0.5), K(46.5, x, y, "idle", alpha=0.72)])
actors.append({"id": "iguana", "rig": "iguana", "name": "Mr. Iguana", "keys": [K(0, 138, 440, "idle"), K(47.4, 138, 440, "idle")]})
events = [
  {"type": "fade", "t": 0, "dur": 0.9, "from": "black"},
  {"type": "label", "t": 6.4, "dur": 0.9, "actor": "k2", "text": "1"}, {"type": "label", "t": 7.2, "dur": 0.9, "actor": "k1", "text": "2"}, {"type": "label", "t": 7.9, "dur": 0.9, "actor": "k0", "text": "3"},
  {"type": "label", "t": 23.0, "dur": 7.0, "x": 80, "y": 322, "text": "El Zurdito"}, {"type": "label", "t": 23.0, "dur": 7.0, "x": 115, "y": 306, "text": "Pancho"},
  {"type": "label", "t": 23.0, "dur": 7.0, "x": 150, "y": 322, "text": "Lola"}, {"type": "label", "t": 23.0, "dur": 7.0, "x": 185, "y": 306, "text": "Chispa"},
  {"type": "fade", "t": 50.8, "dur": 2.3, "to": "black"},
]
scene = {"type": "stage", "template": "stage.html", "duration": DUR, "sprites": sprites, "metaFile": f"{rel}/rig.json",
         "chip": {"text": "SESIÓN 1 · EP. 6", "t": 0.3, "dur": 2.6}, "title": {"text": "Siempre seremos ocho", "t": 0.5, "dur": 2.8},
         "bg": [{"t": 0, "mode": "night"}],
         "camp": {"x": 135, "y": 404, "spots": [{"x": x, "y": 372, "item": it, "t": 22.7} for x, _, _, _, it in SPOTS]},
         "lines": lines, "actors": actors, "events": events}
json.dump({"fps": 30, "width": 1080, "height": 1920, "audio": "audio.m4a", "scenes": [scene]}, open(EP / "episode.json", "w"), ensure_ascii=False, indent=1)
print("ok", EP / "episode.json")
