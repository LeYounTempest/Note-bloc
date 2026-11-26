#!/usr/bin/env python3
"""Extrae la letra con tiempos embebida en un .m4a (stream mov_text de Suno) -> lyrics.json.
Uso: python3 tools/lyrics_from_m4a.py audio.m4a lyrics.json
Cada línea: start/end (s), section, singer (de las etiquetas [..] de la letra), text.
Más fiable que Whisper sobre música cantada."""
import re, json, subprocess, sys
srt = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", sys.argv[1], "-map", "0:s:0", "-f", "srt", "-"]).decode()
def ts(x):
    h, m, r = x.split(":"); s, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
SEC = r"(Intro|Chorus|Final Chorus|Outro|Verse|Bridge)"
sec = who = None; out = []
for b in srt.strip().split("\n\n"):
    l = b.split("\n"); a, e = l[1].split(" --> "); txt = " ".join(l[2:]).strip()
    if txt.startswith("["):
        parts = [x.strip() for x in txt.strip("[]").split("–")]  # "Sección – Cantante, estilo"
        if re.match(SEC, parts[0]):
            sec = parts[0]
            if len(parts) > 1: who = parts[1]
        else:
            who = parts[0]
        continue
    out.append({"start": ts(a), "end": ts(e), "section": sec, "singer": who, "text": txt})
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(out), "líneas")
