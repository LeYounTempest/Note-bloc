#!/usr/bin/env python3
"""Rankea momentos dramáticos de un chatlog.json exportado con foundry_export_macro.js.

Uso: python3 tools/rank_moments.py chatlog.json [--top 8]
Puntaje: nat 20 / nat 1 en d20 (+ contexto), totales altos (daño), rachas de tiradas en poco tiempo.
Salida: lista ordenada para elegir los clips; el guion lo escribe Claude con tus notas.
"""
import json, sys, argparse
from datetime import datetime

ap = argparse.ArgumentParser(); ap.add_argument("log"); ap.add_argument("--top", type=int, default=8)
a = ap.parse_args()
msgs = json.load(open(a.log))
scored = []
for i, m in enumerate(msgs):
    s, why = 0, []
    for r in m.get("rolls", []):
        for d in r["dice"]:
            if d["faces"] == 20:
                for x in d["results"]:
                    if x == 20: s += 10; why.append("nat 20")
                    elif x == 1: s += 9; why.append("nat 1")
        if r["total"] and r["total"] >= 25 and "d20" not in r["formula"]:
            s += min(8, r["total"] / 6); why.append(f"total alto {r['total']}")
    if s:
        # cercanía de tiradas = escena intensa
        near = sum(1 for k in msgs[max(0, i-6):i+7] if k.get("rolls"))
        s += near * 0.3
        scored.append((s, i, m, why))
scored.sort(reverse=True, key=lambda x: x[0])
for s, i, m, why in scored[:a.top]:
    ts = datetime.fromtimestamp(m["ts"] / 1000).strftime("%H:%M:%S") if m.get("ts") else "?"
    print(f"[{s:5.1f}] #{i} {ts} {m.get('speaker','?')}: {m.get('flavor') or m.get('content','')[:60]}  ({', '.join(why)})")
