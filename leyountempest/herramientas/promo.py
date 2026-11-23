#!/usr/bin/env python3
"""Prepara las imágenes de Monster Siege (carpeta promo/ con modelos/ y juego/).

Uso (desde leyountempest/):  python3 herramientas/promo.py RUTA/A/promo
 * modelos/*.jpg: renders de personajes pequeños sobre cielo. Se recortan alrededor del personaje
   (recorte cuadrado a tamaño nativo, sin ampliar) y se guardan en assets/juego/.
 * juego/*.jpg: capturas del juego; se recomprimen sin cambiar de tamaño.
Salida: WebP (calidad 82) y JPG de respaldo.
"""
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from escalar import ampliar  # Real-ESRGAN x4 (si no está instalado, no cambia nada)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "assets", "juego")
os.makedirs(SALIDA, exist_ok=True)
origen = sys.argv[1]
informe = []


def guardar(im, nombre, ampliar_ia=False):
    if ampliar_ia:
        im = ampliar(im)[0]
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    for ext, kw in (("webp", dict(quality=82, method=6)), ("jpg", dict(quality=82, optimize=True, progressive=True))):
        ruta = os.path.join(SALIDA, f"{nombre}.{ext}")
        im.save(ruta, "WEBP" if ext == "webp" else "JPEG", **kw)
        informe.append((f"{nombre}.{ext}", im.width, im.height, os.path.getsize(ruta)))


# personajes: (archivo, nombre de salida)
personajes = {
    "general_aveline": "general-aveline", "general_seris": "general-seris",
    "general_kaede": "general-kaede", "general_mirella": "general-mirella",
    "jefe_faraon_de_ambar": "jefe-faraon-de-ambar", "jefe_reina_tempestad": "jefe-reina-tempestad",
    "jefe_gigante_de_escarcha": "jefe-gigante-de-escarcha", "jefe_senor_de_la_ceniza": "jefe-senor-de-la-ceniza",
    "jefe_troll_del_bosque": "jefe-troll-del-bosque",
}
# Todos los renders tienen al personaje centrado en el mismo punto (x≈406, y≈268 de 812×533).
LADO, CX, CY = 340, 406, 268
for src, dst in personajes.items():
    im = Image.open(os.path.join(origen, "modelos", src + ".jpg")).convert("RGB")
    l, t = CX - LADO // 2, CY - LADO // 2
    guardar(im.crop((l, t, l + LADO, t + LADO)), dst, ampliar_ia=True)

# enemigos en grupo: franja horizontal con toda la fila de monstruos
im = Image.open(os.path.join(origen, "modelos", "enemigos_en_grupo.jpg")).convert("RGB")
guardar(im.crop((40, 170, 790, 400)), "enemigos-en-grupo", ampliar_ia=True)

# capturas del juego
for src, dst in {"pueblo_fortin": "pueblo-fortin", "batalla_combo_x53": "batalla-combo",
                 "jefe_gigante_en_el_camino": "jefe-gigante-camino", "jefe_gigante_cerca": "jefe-gigante-cerca"}.items():
    guardar(Image.open(os.path.join(origen, "juego", src + ".jpg")).convert("RGB"), dst)

for n, w, h, b in sorted(informe):
    print(f"{n:38s}{w:>5d}x{h:<5d}{b/1024:>7.1f} KB")
