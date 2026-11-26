#!/usr/bin/env python3
"""Genera episodes/<nombre>/episode.json (demo del rig) listando todas las partes PNG de assets/rig.
Uso: python3 tools/rig_episode.py [episodes/rig_demo] [duración]"""
import json, sys, os
from pathlib import Path
out = Path(sys.argv[1] if len(sys.argv) > 1 else "episodes/rig_demo"); dur = float(sys.argv[2]) if len(sys.argv) > 2 else 12
out.mkdir(parents=True, exist_ok=True)
rel = os.path.relpath("assets/rig", out)
chars = [d.name for d in sorted(Path("assets/rig").iterdir()) if d.is_dir()]
spr = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in chars for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}
G2 = dict(cols=2, rows=3, zoom=2, feetX=33, feetY=75)
PRESETS = {"tall": [
 dict(grid=G2, cells=[["kenku","idle",0,{},"kenku"], ["kenku","guard",0,{},"kenku resiste"], ["kenku","smite",0,{"loop":1.8},"kenku lanzada"],
                      ["dei","play",0,{},"Dei toca"], ["dei","cast",0,{"loop":2.4},"Dei relámpago"], ["dei","die",0,{"loop":2.6,"x":64},"Dei muere"]]),
 dict(grid=G2, cells=[["hans","walk",0,{},"Hans camina"], ["hans","toast",0,{},"Hans brinda"], ["hans","sneak",1,{"alpha":.55},"Hans sigilo"],
                      ["hans","stab",1,{"loop":1.6},"Hans puñalada"], ["hans","vanish",0,{"loop":2.6},"Hans invisible"], ["kenku","walk",0,{},"kenku camina"]]),
]}
base = {"type": "rig", "template": "rig_demo.html", "duration": dur, "sprites": spr, "metaFile": f"{rel}/rig.json"}
scenes = [{**base, **o} for o in PRESETS[sys.argv[3]]] if len(sys.argv) > 3 else [base]
ep = {"fps": 30, "width": 1080, "height": 1920, "scenes": scenes}
json.dump(ep, open(out / "episode.json", "w"), indent=1)
print(len(spr), "sprites ->", out / "episode.json")
