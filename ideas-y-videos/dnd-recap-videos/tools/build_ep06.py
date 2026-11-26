#!/usr/bin/env python3
"""ep06 'Siempre seremos ocho' (0 = "Después..."): cuenta señalada por Iguana, flashback soleado de los siete en la costa
("Antes siete corríamos por la costa"), barco en el horizonte y fantasmas junto al fuego. Uso: python3 tools/build_ep06.py"""
import json, os, re
from pathlib import Path
EP = Path("episodes/ep06_siempre_seremos_ocho"); L = json.load(open(EP / "lyrics.json")); DUR = 76.3
rel = os.path.relpath("assets/rig", EP)
chars = [d.name for d in sorted(Path("assets/rig").iterdir()) if d.is_dir()]
sprites = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in chars for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}
lines = []
for i, l in enumerate(L):
    t0 = l["start"]; t1 = min(l["end"], t0 + 4.5)
    if i + 1 < len(L) and L[i + 1]["start"] - t0 < 4.5: t1 = L[i + 1]["start"] - 0.02
    lines.append({"t0": round(max(0, t0), 2), "t1": round(t1, 2), "text": l["text"], "big": False})
def K(t, x, y, anim="idle", **kw): return {"t": t, "x": x, "y": y, "anim": anim, **kw}
FB0, FB1 = 15.3, 20.4                                   # flashback "Antes siete corríamos por la costa"
actors = []
def add(id_, rig, name, keys, **kw): actors.append({"id": id_, "rig": rig, "name": name, "keys": sorted(keys, key=lambda k: k["t"]), **kw})
def gap(pos, anim_after):                                 # el campamento desaparece durante el flashback
    return [K(FB0, *pos, "idle", vis=False), K(FB1, *pos, anim_after)]
def sing(t0, t1, pos, seed, anim="sing"): return [K(t0, *pos, anim, opts={"seed": seed}), K(t1, *pos, "idle")]
P = {"k0": (84, 408), "k1": (104, 420), "k2": (172, 408), "ig": (138, 440)}
# ── campamento: Julia (Female), Piedrín (Male 2), Braulio (Male 1); cada cuenta del jefe los hace saltar ──
WARM = [255, 205, 120]
# todos cantan juntos el coro (28.2-42.6) y lo celebran con los brazos arriba en "¡nosotros vamos a continuar!" (42.6-51.3)
def chorus(pos, seed): return [K(28.2, *pos, "sing", opts={"seed": seed}), K(42.6, *pos, "cheer"), K(51.2, *pos, "idle")]
add("k0", "kobold", "Julia",   [K(0, *P["k0"], "idle")] + sing(7.9, 8.5, P["k0"], 1, "cheer") + sing(8.5, 15.2, P["k0"], 2) + gap(P["k0"], "sing") + sing(20.4, 22.7, P["k0"], 3) + chorus(P["k0"], 4) + sing(56.4, 62.3, P["k0"], 5) + sing(63.0, 69.6, P["k0"], 6), variant=0, seed=0)
add("k1", "kobold", "Piedrín", [K(0, *P["k1"], "idle")] + sing(7.2, 7.9, P["k1"], 7, "cheer") + sing(8.5, 15.2, P["k1"], 8) + gap(P["k1"], "idle") + sing(25.6, 28.0, P["k1"], 9) + chorus(P["k1"], 10) + sing(53.9, 56.1, P["k1"], 11, "cheer") + sing(63.0, 69.6, P["k1"], 12), variant=1, seed=1)
add("k2", "kobold", "Braulio", [K(0, *P["k2"], "idle")] + sing(6.4, 7.2, P["k2"], 13, "cheer") + sing(8.5, 15.2, P["k2"], 14) + gap(P["k2"], "idle") + sing(22.7, 25.4, P["k2"], 15) + chorus(P["k2"], 16) + sing(51.3, 53.7, P["k2"], 17) + sing(63.0, 69.6, P["k2"], 18), variant=2, seed=2)
# Iguana (el jefe): señala al contar; en el coro se yergue y, en "¡nosotros vamos a continuar!", alza el bastón con un pilar de luz
add("iguana", "iguana", "Mr. Iguana", [K(0, *P["ig"], "idle"), K(6.2, *P["ig"], "point", opts={"sa": 55}), K(7.0, *P["ig"], "point", opts={"sa": -55}), K(7.7, *P["ig"], "point", opts={"sa": -75}),
    K(8.6, *P["ig"], "idle")] + gap(P["ig"], "idle") + [K(38.9, *P["ig"], "point", opts={"sa": 0}, fxcol=WARM), K(42.05, *P["ig"], "cast", fxcol=WARM, aura=0.6), K(46.0, *P["ig"], "cast", fxcol=WARM, aura=1.6), K(51.2, *P["ig"], "cast", fxcol=WARM, aura=0.4), K(52.0, *P["ig"], "idle")])
SPOTS = [(80, 378, 4, "El Zurdito", "spyglass"), (115, 378, 5, "Pancho", "hammer"), (150, 378, 6, "Lola", "rope"), (185, 378, 3, "Chispa", "barrel")]
for x, y, v, nm, _ in SPOTS:
    add(f"g{v}", "kobold", nm, [K(0, x, y, "idle", alpha=0.0), K(30.0, x, y, "idle", alpha=0.0), K(30.8, x, y, "idle", alpha=0.3), K(32.8, x, y, "idle", alpha=0.0), K(42.6, x, y, "idle", alpha=0.0), K(44.5, x, y, "idle", alpha=0.5), K(50.5, x, y, "idle", alpha=0.5), K(53.0, x, y, "idle", alpha=0.0),
                                K(63.0, x, y, "idle", alpha=0.0), K(65.6, x, y, "idle", alpha=0.5), K(68.0, x, y, "idle", alpha=0.5), K(69.6, x, y, "idle", alpha=0.72)], variant=v, seed=v)
# ── flashback: los siete jugando en la costa (día) ──
def fb(id_, v, name, keys): add(id_, "kobold", name, keys, variant=v, seed=v)
def runner(y, off):                                        # ida y vuelta por la orilla
    t = FB0 + off; return [K(t, -14, y, "run"), K(t + 1.7, 290, y, "run"), K(t + 1.8, 290, y + 3, "run", jump=True), K(t + 3.5, -14, y + 3, "run"),
                           K(t + 3.6, -14, y, "run", jump=True), K(FB1, 120, y, "run"), K(FB1 + 0.1, 120, y, "idle", vis=False)]
fb("f0", 0, "Julia", [K(FB0, 24, 376, "walk"), K(FB1, 150, 376, "walk"), K(FB1 + 0.1, 150, 376, "idle", vis=False)])
fb("f1", 1, "Piedrín", [K(FB0, 236, 358, "walk", opts={"speed": .8}), K(FB1, 140, 358, "walk", opts={"speed": .8}), K(FB1 + 0.1, 140, 358, "idle", vis=False)])
fb("f2", 2, "Braulio", [K(FB0, 176, 372, "sing", opts={"seed": 31}), K(FB1, 176, 372, "sing", opts={"seed": 33}), K(FB1 + 0.1, 176, 372, "idle", vis=False)])
fb("f3", 3, "Chispa", runner(342, 0))
fb("f6", 6, "Lola", runner(364, 0.55))
fb("f4", 4, "El Zurdito", [K(FB0, 108, 326, "idle"), K(FB1 + 0.1, 108, 326, "idle", vis=False)])
fb("f5", 5, "Pancho", [K(FB0, 238, 384, "cheer"), K(FB1 + 0.1, 238, 384, "idle", vis=False)])
events = [
  {"type": "fade", "t": 0, "dur": 0.9, "from": "black"},
  {"type": "label", "t": 6.4, "dur": 0.9, "actor": "k2", "text": "1", "big": True}, {"type": "label", "t": 7.2, "dur": 0.9, "actor": "k1", "text": "2", "big": True}, {"type": "label", "t": 7.9, "dur": 0.9, "actor": "k0", "text": "3", "big": True},
  {"type": "flash", "t": 6.4, "dur": 0.2, "a": 0.25}, {"type": "flash", "t": 7.2, "dur": 0.2, "a": 0.25}, {"type": "flash", "t": 7.9, "dur": 0.2, "a": 0.25},
  # flashback: destello, sepia + viñeta + grano, destello de vuelta
  {"type": "flash", "t": FB0 - 0.1, "dur": 0.6, "a": 1.0}, {"type": "tint", "t": FB0, "dur": FB1 - FB0, "a": 0.14, "c": "255,222,160", "vig": True}, {"type": "grain", "t": FB0, "dur": FB1 - FB0},
  {"type": "flash", "t": FB1 - 0.1, "dur": 0.6, "a": 1.0},
  {"type": "label", "t": 23.0, "dur": 7.0, "x": 80, "y": 322, "text": "El Zurdito"}, {"type": "label", "t": 23.0, "dur": 7.0, "x": 115, "y": 306, "text": "Pancho"},
  {"type": "label", "t": 23.0, "dur": 7.0, "x": 150, "y": 322, "text": "Lola"}, {"type": "label", "t": 23.0, "dur": 7.0, "x": 185, "y": 306, "text": "Chispa"},
  # coro final: el fuego crece, luz cálida y, en "¡nosotros vamos a continuar!", un pilar de luz del cristal de Iguana
  {"type": "tint", "t": 36.3, "dur": 15.0, "a": 0.10, "c": "255,190,110"},
  {"type": "flash", "t": 42.6, "dur": 0.5, "a": 0.6}, {"type": "shake", "t": 42.6, "dur": 0.6, "amp": 2},
  {"type": "beam", "t": 42.6, "dur": 8.7, "from": {"actor": "iguana", "anchor": "crystal"}, "to": {"x": 138, "y": -10}, "w": 6, "amp": 2, "id": 1, "cols": ["rgba(255,200,120,.45)", "#ffd890", "#ffffff"]},
  {"type": "fade", "t": 73.9, "dur": 2.4, "to": "black"},
]
scene = {"type": "stage", "template": "stage.html", "duration": DUR, "sprites": sprites, "metaFile": f"{rel}/rig.json",
         "chip": {"text": "SESIÓN 1 · EP. 6", "t": 0.3, "dur": 2.6}, "title": {"text": "Siempre seremos ocho", "t": 0.5, "dur": 2.8},
         "bg": [{"t": 0, "mode": "night"}, {"t": FB0 - 0.05, "mode": "day"}, {"t": FB1 - 0.05, "mode": "night"}],
         "camp": {"x": 135, "y": 404, "flares": [{"t": 36.3, "k": 1.35}, {"t": 42.6, "k": 1.8}, {"t": 51.3, "k": 1.0}], "spots": [{"x": x, "y": 372, "item": it, "t": 22.7} for x, _, _, _, it in SPOTS]},
         "ships": [{"x0": 150, "x1": 62, "t0": 51.5, "t1": 66.5, "y": 94, "s": 1.5}],
         "lines": lines, "actors": actors, "events": events}
json.dump({"fps": 30, "width": 1080, "height": 1920, "audio": "audio.m4a", "scenes": [scene]}, open(EP / "episode.json", "w"), ensure_ascii=False, indent=1)
print("ok", EP / "episode.json")
