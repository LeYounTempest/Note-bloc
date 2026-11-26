#!/usr/bin/env python3
"""Genera episodes/<nombre>/episode.json (demo del rig) listando todas las partes PNG de assets/rig.
Uso: python3 tools/rig_episode.py [episodes/rig_demo] [duración]"""
import json, sys, os
from pathlib import Path
out = Path(sys.argv[1] if len(sys.argv) > 1 else "episodes/rig_demo"); dur = float(sys.argv[2]) if len(sys.argv) > 2 else 12
out.mkdir(parents=True, exist_ok=True)
rel = os.path.relpath("assets/rig", out)
spr = {f"{c}.{p.stem}": f"{rel}/{c}/{p.name}" for c in ("kobold", "iguana") for p in sorted(Path(f"assets/rig/{c}").glob("*.png"))}
ep = {"fps": 30, "width": 1080, "height": 1920, "scenes": [{"type": "rig", "template": "rig_demo.html", "duration": dur,
      "sprites": spr, "metaFile": f"{rel}/rig.json"}]}
json.dump(ep, open(out / "episode.json", "w"), indent=1)
print(len(spr), "sprites ->", out / "episode.json")
