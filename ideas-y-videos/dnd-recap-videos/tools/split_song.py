#!/usr/bin/env python3
"""Corta la canción en clips (tabla CLIPS) -> episodes/clips/<id>/{audio.m4a,lyrics.json} + episodes/clips/clips.json.
Uso: python3 tools/split_song.py [episodes/me_iguana_full]
Inicio/fin = inicio de líneas de la letra; el fin se fija a mano para cortar colas instrumentales."""
import json, subprocess, sys, numpy as np
from pathlib import Path
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "episodes/me_iguana_full")
OUT = Path("episodes/clips"); OUT.mkdir(parents=True, exist_ok=True)
L = json.load(open(SRC / "lyrics.json"))
# id, título, inicio, fin(inicio de línea siguiente o None=auto), evento D&D, tono, prioridad(1=imprescindible)
CLIPS = [  # (el fin es explícito; la cola instrumental se corta a mano)
 ("c01_casco_y_la_mano",   "El casco y la mano",            0.0,  45.0, None, "Intro: siete kobolds, cae el casco, aparece Mr. Iguana", "épico/melancólico", 2),
 ("c02_saqueo_y_coro",     "Hijos de la costa",            61.8, 95.6, None, "Saqueo cotidiano y coro del grupo (presentación)", "alegre/épico", 3),
 ("c03_relampago_1_2_3",   "Uno, dos, tres",               95.6, 114.5, None, "Elfo con vino, tres kobolds van por el bardo, relámpago de Dei", "tensión → golpe", 1),
 ("c04_ventisca",          "Ventisca",                    114.5, 132.3, None, "Mr. Iguana lanza Ventisca; el dracónido sale volando", "acción", 2),
 ("c05_tres_lugares",      "Tres lugares junto al fuego",  132.3, 154.5, None, "Duelo por los tres muertos (Zurdito, Pancho, Lola)", "emotivo/oscuro", 2),
 ("c06_dragon_de_cobre",   "El dragón de cobre",          154.5, 180.9, None, "Emerge el dragón adulto; fuego, escudos, hielo; elfo invisible", "acción", 2),
 ("c07_chispa_y_el_susurro","Chispa y el susurro",        180.9, 213.4, None, "Chispa levanta a Dei, susurro invisible, Chispa cae", "dramático", 1),
 ("c08_explosion",         "El cuerpo es un arma",        213.4, 251.0, None, "El bardo arroja a Chispa contra el dragón; explosión; Iguana se quiebra", "clímax emocional", 1),
 ("c09_el_oceano_se_detiene","El océano dejó de avanzar", 251.0, 279.9, None, "Iguana congela costa y mar; el dragón intenta huir", "épico creciente", 2),
 ("c10_rayo_de_hielo",     "Rayo de Hielo",               279.9, 317.3, None, "¡Demasiado tarde! Rayo de Hielo, el dragón se hace pedazos", "clímax", 1),
 ("c11_cuatro_lugares_vacios","Cuatro lugares vacíos",    332.1, 360.3, None, "Tras la batalla: el jefe cuenta 1-2-3, quedan tres", "emotivo", 1),
 ("c12_somos_hijos_de_la_costa","Nosotros vamos a continuar",360.3, 383.4, None, "Coro final de duelo y resistencia", "épico/emotivo", 2),
 ("c13_siempre_seremos_ocho","Siempre seremos ocho",      383.4, 408.4, None, "Outro: mañana otro barco; fuimos siete, con el jefe somos ocho", "cálido/cierre", 1),
]
def rms(a, b):
    y = np.frombuffer(subprocess.check_output(["ffmpeg","-loglevel","error","-ss",str(a),"-t",str(b-a),"-i",str(SRC/"audio.m4a"),"-f","s16le","-ac","1","-ar","16000","-"]),np.int16).astype(np.float32)/32768
    return float(np.sqrt((y**2).mean())), float(np.abs(y).max())
meta = []
for cid, title, a, b, auto_end, event, mood, prio in CLIPS:
    ls = [dict(l) for l in L if l["start"] >= a - 0.01 and l["start"] < b - 0.01]
    for l in ls: l["end"] = min(l["end"], l["start"] + 4.5, b)
    d = Path(OUT / cid); d.mkdir(exist_ok=True)
    for l in ls: l["start"] = round(l["start"] - a, 2); l["end"] = round(l["end"] - a, 2)
    json.dump(ls, open(d / "lyrics.json", "w"), ensure_ascii=False, indent=1)
    dur = b - a
    subprocess.check_call(["ffmpeg","-y","-loglevel","error","-ss",f"{a:.2f}","-t",f"{dur:.2f}","-i",str(SRC/"audio.m4a"),"-map","0:a",
        "-af",f"afade=t=in:d=0.15,afade=t=out:st={dur-0.6:.2f}:d=0.6","-c:a","aac","-b:a","160k",str(d/"audio.m4a")])
    r, pk = rms(a, b)
    meta.append({"id": cid, "title": title, "src_start": round(a,2), "src_end": round(b,2), "duration": round(dur,1), "event": event, "mood": mood,
                 "priority": prio, "singers": sorted({l["singer"] for l in ls}), "energy_rms": round(r,3), "peak": round(pk,2), "lines": len(ls)})
json.dump(meta, open(OUT / "clips.json", "w"), ensure_ascii=False, indent=1)
for m in meta: print(f"{m['id']:30s} {m['src_start']:6.1f}-{m['src_end']:6.1f} {m['duration']:5.1f}s P{m['priority']} rms={m['energy_rms']} {m['title']}")
