#!/usr/bin/env python3
"""Busca y descarga efectos de sonido libres desde la API pública de Openverse (sin clave) y registra la licencia/crédito.
Uso: python3 tools/openverse_sfx.py "thunder" [--license cc0|commercial] [--max-ms 6000] [--min-ms 300] [--n 1] [--out assets/sfx]
Por defecto solo CC0 (no exige atribución). Con --license commercial acepta CC-BY etc.: entonces hay que acreditar (se guarda en credits.json)."""
import argparse, json, os, re, sys, time, urllib.parse, urllib.request
ap = argparse.ArgumentParser()
ap.add_argument("query"); ap.add_argument("--license", default="cc0"); ap.add_argument("--max-ms", type=int, default=6000)
ap.add_argument("--min-ms", type=int, default=300); ap.add_argument("--n", type=int, default=1); ap.add_argument("--out", default="assets/sfx")
a = ap.parse_args()
UA = {"User-Agent": "dnd-recap-sfx/1.0"}
def get(url, retries=3):
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return r.read()
        except Exception as e:
            if i == retries - 1: raise
            time.sleep(1.5 * (i + 1))
qs = {"q": a.query, "page_size": 20}
qs["license" if a.license == "cc0" else "license_type"] = "cc0" if a.license == "cc0" else a.license
data = json.loads(get("https://api.openverse.org/v1/audio/?" + urllib.parse.urlencode(qs)))
cands = [r for r in data.get("results", []) if a.min_ms <= (r.get("duration") or 0) <= a.max_ms]
if not cands: sys.exit(f"sin resultados para '{a.query}' ({data.get('result_count')} totales; prueba --max-ms mayor o --license commercial)")
os.makedirs(a.out, exist_ok=True); credits_path = os.path.join(a.out, "credits.json")
credits = json.load(open(credits_path)) if os.path.exists(credits_path) else {}
slug = re.sub(r"[^a-z0-9]+", "_", a.query.lower()).strip("_")
for i, r in enumerate(cands[:a.n]):
    ext = os.path.splitext(urllib.parse.urlparse(r["url"]).path)[1] or ".mp3"
    fn = f"{slug}{'' if a.n == 1 else '_' + str(i + 1)}{ext}"
    open(os.path.join(a.out, fn), "wb").write(get(r["url"]))
    credits[fn] = {"title": r.get("title"), "creator": r.get("creator"), "license": f"{r.get('license')} {r.get('license_version')}",
                   "license_url": r.get("license_url"), "source": r.get("source"), "page": r.get("foreign_landing_url"), "duration_ms": r.get("duration")}
    print(f"{fn}  {r.get('duration')} ms  {r.get('license')} {r.get('license_version')}  {r.get('source')}  «{(r.get('title') or '')[:40]}»")
json.dump(credits, open(credits_path, "w"), ensure_ascii=False, indent=1)
