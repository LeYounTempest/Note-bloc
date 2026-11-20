#!/usr/bin/env python3
"""Genera los recortes de Aurelia a partir de las hojas de referencia.

Uso (desde la carpeta leyountempest/):
    python3 herramientas/recortes.py            # escribe en assets/aurelia/
    python3 herramientas/recortes.py --debug    # además deja vistas previas sobre fondo oscuro en /tmp

Reglas:
  * Solo se recorta, se limpia texto/marcos y se funden los bordes. No se redibuja nada.
  * Nunca se escala por encima del tamaño nativo del recorte (no se estira).
  * Los recortes con fondo de papel claro se funden con el fondo oscuro de la página con
    una máscara de degradado (alfa en WebP; el JPG de respaldo va compuesto sobre #0b0610).
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
SALIDA = os.path.join(ASSETS, "aurelia")
FONDO = (11, 6, 16)  # #0b0610
CALIDAD = 82
DEBUG = "--debug" in sys.argv
rng = np.random.default_rng(7)


def abrir(nombre):
    return Image.open(os.path.join(ASSETS, nombre)).convert("RGB")


# --------------------------------------------------------------------------- papel
def lamina_papel(im, bloque=16):
    """Estima el color del papel (baja frecuencia) ignorando tinta y dibujos.
    Devuelve (lamina float32 HxWx3, sigma del grano)."""
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(2)
    sat = a.max(2) - a.min(2)
    papel = (lum > 150) & (lum < 235) & (sat < 45)
    H, W = lum.shape
    bh, bw = H // bloque, W // bloque
    medias = np.full((bh, bw, 3), np.nan, np.float32)
    for by in range(bh):
        for bx in range(bw):
            m = papel[by * bloque:(by + 1) * bloque, bx * bloque:(bx + 1) * bloque]
            if m.mean() > 0.35:
                medias[by, bx] = np.median(a[by * bloque:(by + 1) * bloque, bx * bloque:(bx + 1) * bloque][m], axis=0)
    # rellena bloques vacíos con el promedio de los vecinos, hasta cubrir todo
    for _ in range(80):
        vacio = np.isnan(medias[..., 0])
        if not vacio.any():
            break
        pad = np.pad(medias, ((1, 1), (1, 1), (0, 0)), constant_values=np.nan)
        vec = np.stack([pad[:-2, 1:-1], pad[2:, 1:-1], pad[1:-1, :-2], pad[1:-1, 2:]])
        with np.errstate(all="ignore"):
            prom = np.nanmean(vec, axis=0)
        medias[vacio] = prom[vacio]
    medias = np.nan_to_num(medias, nan=float(a[papel].mean()))
    # suaviza la cuadrícula de bloques con un promedio 3x3 repetido y la escala con interpolación bilineal
    k = np.array([1, 2, 1], np.float32) / 4
    for _ in range(2):
        for ax in (0, 1):
            medias = np.apply_along_axis(lambda v: np.convolve(np.pad(v, 1, mode="edge"), k, "valid"), ax, medias)
    canales = []
    for c in range(3):
        ch = Image.fromarray(medias[..., c], mode="F").resize((W, H), Image.BILINEAR)
        canales.append(np.asarray(ch))
    lamina = np.stack(canales, axis=2)
    sigma = float((a - lamina)[papel].std())
    return lamina, min(sigma, 9.0)


def grano(forma, sigma):
    """Ruido gaussiano de grano fino (suavizado 3 taps) para imitar el papel de la hoja."""
    r = rng.normal(0, sigma, forma[:2]).astype(np.float32)
    k = np.array([1, 2, 1], np.float32) / 4
    for ax in (0, 1):
        r = np.apply_along_axis(lambda v: np.convolve(np.pad(v, 1, mode="edge"), k, "valid"), ax, r)
    return np.repeat((r * 1.6)[..., None], 3, axis=2)


def limpiar(im, lamina, sigma, zonas, difuminado=2.5, anillo=14):
    """Sustituye cada zona (rect o polígono, en coords de la hoja) por papel liso con grano.
    El tono se corrige con el papel real que rodea la zona para que no se note la costura."""
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(2)
    sat = a.max(2) - a.min(2)
    es_papel = (lum > 120) & (lum < 235) & (sat < 45)
    mascaras = []
    for z in zonas:
        mz = Image.new("L", im.size, 0)
        d = ImageDraw.Draw(mz)
        if len(z) == 4 and not isinstance(z[0], (tuple, list)):
            d.rectangle(z, fill=255)
        else:
            d.polygon(z, fill=255)
        mascaras.append(mz)
    todas = np.zeros(lum.shape, bool)
    for mz in mascaras:
        todas |= np.asarray(mz) > 0
    out = a.copy()
    for mz in mascaras:
        dentro = np.asarray(mz) > 0
        borde = np.asarray(mz.filter(ImageFilter.MaxFilter(2 * anillo + 1))) > 0
        ring = borde & ~dentro & ~todas & es_papel
        if ring.sum() < 30:
            ring = borde & ~dentro & es_papel
        corr = np.median(a[ring], axis=0) - np.median(lamina[ring], axis=0) if ring.sum() else 0
        m = np.asarray(mz.filter(ImageFilter.GaussianBlur(difuminado))).astype(np.float32) / 255.0
        relleno = lamina + corr + grano(a.shape, sigma)
        out = out * (1 - m[..., None]) + relleno * m[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# --------------------------------------------------------------------------- lienzo
def lienzo(im, caja, lamina, sigma, aspecto=None, margen=0):
    """Recorta `caja` (puede salirse de la hoja) y la centra en un lienzo de papel.
    `aspecto` = ancho/alto objetivo (se rellena con papel, sin estirar). `margen` = papel extra por lado."""
    x0, y0, x1, y1 = caja
    w, h = x1 - x0, y1 - y0
    W = w + 2 * margen
    H = h + 2 * margen
    if aspecto:
        if W / H < aspecto:
            W = int(round(H * aspecto))
        else:
            H = int(round(W / aspecto))
    papel = np.asarray(lamina).mean((0, 1))  # color medio del papel de la hoja
    base = np.tile(papel, (H, W, 1)).astype(np.float32)
    base = base + grano((H, W, 3), sigma)
    lienzo_im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    sub = im.crop((max(x0, 0), max(y0, 0), min(x1, im.width), min(y1, im.height)))
    ox = (W - w) // 2 + max(0, -x0)
    oy = (H - h) // 2 + max(0, -y0)
    lienzo_im.paste(sub, (ox, oy))
    return lienzo_im


def rampa(n, fade):
    i = np.arange(n, dtype=np.float32)
    t = np.clip(np.minimum(i, n - 1 - i) / max(fade, 1), 0, 1)
    return t * t * (3 - 2 * t)


def fundir(im, fade, halo=None, umbral=46):
    """Devuelve RGBA con el borde desvanecido.
    halo=(dilatar, difuminar): el alfa sigue la silueta del dibujo (papel alrededor de la figura que se
    desvanece en un aura) en vez de un rectángulo. Siempre se aplica además una rampa corta en el borde."""
    w, h = im.size
    alfa = np.outer(rampa(h, fade), rampa(w, fade))
    if halo:
        dil, dif = halo
        a = np.asarray(im).astype(np.float32)
        papel = np.median(a.reshape(-1, 3), axis=0)
        tinta = (np.abs(a - papel).max(2) > umbral).astype(np.uint8) * 255
        m = Image.fromarray(tinta).filter(ImageFilter.MaxFilter(2 * dil + 1)).filter(ImageFilter.GaussianBlur(dif))
        m = np.clip(np.asarray(m).astype(np.float32) / 255.0 * 2.0, 0, 1)
        m = m * m * (3 - 2 * m)
        alfa = alfa * m
    rgba = im.convert("RGBA")
    rgba.putalpha(Image.fromarray((alfa * 255).astype(np.uint8)))
    return rgba


def sobre_fondo(rgba):
    fondo = Image.new("RGB", rgba.size, FONDO)
    fondo.paste(rgba, mask=rgba.split()[3])
    return fondo


# --------------------------------------------------------------------------- exportar
resultados = []


def exportar(nombre, im, anchos=(800, 1600)):
    """Escribe nombre.webp/.jpg (tamaño mayor sin pasar de 1600 ni del nativo) y
    nombre-800.webp/.jpg si el nativo supera 800 px. Nunca amplía."""
    os.makedirs(SALIDA, exist_ok=True)
    nativo = im.width
    mayor = min(nativo, anchos[1])
    variantes = [(nombre, mayor)]
    if nativo > anchos[0]:
        variantes.append((f"{nombre}-{anchos[0]}", anchos[0]))
    for base, ancho in variantes:
        alto = round(im.height * ancho / im.width)
        r = im if ancho == im.width else im.resize((ancho, alto), Image.LANCZOS)
        rgb = sobre_fondo(r) if r.mode == "RGBA" else r
        for ext, kw in (("webp", dict(quality=CALIDAD, method=6, alpha_quality=75)),
                        ("jpg", dict(quality=CALIDAD, optimize=True, progressive=True))):
            ruta = os.path.join(SALIDA, f"{base}.{ext}")
            if ext == "webp":
                r.save(ruta, "WEBP", **kw)
            else:
                rgb.save(ruta, "JPEG", **kw)
            resultados.append((f"{base}.{ext}", r.width, r.height, os.path.getsize(ruta), nativo))
    if DEBUG:
        prev = sobre_fondo(im) if im.mode == "RGBA" else im
        prev.save(f"/tmp/prev_{nombre}.png")


# =========================================================================== RECORTES
concepto = abrir("aurelia-concepto.jpg")
ficha2 = abrir("aurelia-ficha-2.jpg")
cafe = abrir("aurelia-cafe.jpg")
retrato = abrir("aurelia-retrato.jpg")
lam_c, sig_c = lamina_papel(concepto)

# ---- cuerpo completo (hoja de concepto; la hoja tiene el mayor tamaño nativo del cuerpo)
zonas_cuerpo = [
    (0, 5, 237, 12),           # filete superior de la hoja (salvo la punta del cuerno)
    (244, 5, 552, 12),
    (0, 0, 12, 1112),          # filete izquierdo de la hoja
    (6, 10, 182, 92),          # título AURELIA / LA DRAGONA
    (6, 92, 182, 274),         # viñetas de personalidad
    (20, 308, 96, 344),        # cota "2.00 m"
    (50, 340, 76, 640),        # línea vertical de la cota
    (386, 84, 480, 192),       # "Cuernos negros..."
    (422, 224, 480, 302),      # "Cabello corto..."
    (476, 0, 552, 868),        # boceto de cabeza, bocetos y notas a la derecha del cuerpo
    (466, 336, 552, 425),      # resto del boceto del ojo
    (468, 650, 552, 868),
    [(552, 1018), (500, 1034), (470, 1050), (440, 1062), (415, 1085), (400, 1112), (552, 1112)],  # ala del dragón
]
c = limpiar(concepto, lam_c, sig_c, zonas_cuerpo)
# margen de papel extra: la cola llega al borde izquierdo de la hoja
cuerpo = lienzo(c, (-44, -36, 546, 1112), lam_c, sig_c)
exportar("aurelia-cuerpo", fundir(cuerpo, 14, halo=(22, 18)))

# ---- detalle del vestido y la joya del cuello (torso de la hoja de concepto)
zonas_vestido = [
    (96, 146, 174, 284),       # viñetas de texto a la izquierda
    (152, 180, 172, 314),      # línea vertical de la cota
    (404, 146, 480, 190),      # "extienden hacia atrás."
    (424, 226, 480, 302),      # "Cabello corto..."
]
c = limpiar(concepto, lam_c, sig_c, zonas_vestido)
vestido = lienzo(c, (100, 190, 468, 548), lam_c, sig_c, aspecto=1.0, margen=14)
exportar("aurelia-vestido", fundir(vestido, 30, halo=(18, 16)))

# ---- cola de escamas arcoíris (boceto de detalle)
zonas_cola = [
    (536, 696, 604, 722),      # rótulo COLA y subrayado
    (546, 722, 600, 784),      # flecha
    (500, 742, 568, 808),      # "Escamas arcoíris que reflejan la luz."
    [(530, 850), (566, 850), (566, 1010), (530, 1010)],  # borde del vestido de la figura
    (776, 690, 800, 1010),     # separador vertical
]
c = limpiar(concepto, lam_c, sig_c, zonas_cola)
cola = lienzo(c, (548, 700, 778, 972), lam_c, sig_c, aspecto=1.0, margen=10)
exportar("aurelia-cola", fundir(cola, 12, halo=(14, 14)))

# ---- garras (boceto de detalle de la mano)
zonas_garras = [
    (800, 696, 876, 722),      # rótulo GARRAS
    (872, 714, 893, 736),      # flecha
    (934, 906, 1012, 928),     # "Sus uñas"
    (914, 930, 1012, 952),     # "siguen siendo"
    (900, 950, 1012, 975),     # "garras de dragón." 
    (776, 690, 790, 1010),     # separador vertical
]
c = limpiar(concepto, lam_c, sig_c, zonas_garras)
garras = lienzo(c, (788, 700, 975, 972), lam_c, sig_c, aspecto=1.0, margen=10)
exportar("aurelia-garras", fundir(garras, 12, halo=(14, 14)))

# ---- forma verdadera: dragón de cuatro alas
zonas_dragon = [
    # todo lo que queda por encima del borde superior del ala (borde del vestido, zapato, boceto de arriba)
    [(150, 940), (800, 940), (790, 992), (762, 990), (700, 992), (650, 999), (597, 1011), (554, 1022),
     (512, 1034), (497, 1034), (486, 1043), (468, 1050), (436, 1056), (420, 1080), (400, 1104), (150, 1104)],
    (150, 1296, 220, 1378),    # ala del boceto "comparación de tamaño"
    (150, 1380, 190, 1460),    # cola del mismo boceto
    (150, 1090, 215, 1128),    # resto de filete bajo el vestido
    (150, 1138, 178, 1158),    # final del subrayado de FORMA VERDADERA
    (548, 1440, 642, 1458),    # "DATOS EXTRAS"
    (545, 1452, 750, 1459),    # borde superior del cuadro
    (533, 1459, 750, 1540),    # texto del cuadro
    (734, 1425, 750, 1540),    # borde derecho del cuadro
    (496, 1478, 505, 1540),    # borde izquierdo (debajo de la cola)
    (496, 1456, 505, 1465),    # borde izquierdo (encima de la cola)
    (745, 1380, 790, 1510),    # separador y rombos de paleta
    (526, 1468, 534, 1540),    # resto del borde izquierdo del cuadro
    (726, 1262, 790, 1380),    # esquina del boceto "vista lateral"
    (748, 1016, 790, 1380),    # bocetos "vista trasera" y "vista lateral"
]
c = limpiar(concepto, lam_c, sig_c, zonas_dragon)
dragon = lienzo(c, (162, 958, 775, 1500), lam_c, sig_c, margen=26)
exportar("aurelia-dragon", fundir(dragon, 14, halo=(22, 18)))

# ---- rostro y cuernos: del retrato de alta resolución (la hoja da solo ~260×390 px)
# El anillo dorado y la estrella inferior quedan fuera del círculo inscrito; en la página se muestra con border-radius:50%.
cx, cy, r = 627, 560, 540
rostro = retrato.crop((cx - r, cy - r, cx + r, cy + r))
exportar("aurelia-rostro", rostro)

# ---- expresiones (ficha 2: caras de ~120 px, más grandes que las de la ficha 1)
# (x0, y0, x1, y1) dentro del marco de cada casilla, sin la barra con la etiqueta
caras = {
    "expr-1": (989, 39, 1110, 158),   # Neutral
    "expr-2": (1122, 39, 1241, 158),  # Amable
    "expr-3": (989, 189, 1110, 308),  # Sorpresa
    "expr-4": (1122, 189, 1241, 308), # Molesta
    "expr-5": (1253, 189, 1373, 308), # Sonrisa leve
    "expr-6": (1386, 189, 1508, 308), # Risa
}
for nombre, caja in caras.items():
    x0, y0, x1, y1 = caja
    lado = min(x1 - x0, y1 - y0)
    cara = ficha2.crop((x0, y0, x0 + lado, y0 + lado))
    exportar(f"aurelia-{nombre}", cara)

# ---- portada: dos recortes de dirección de arte de aurelia-cafe.jpg (1536×1024)
# Escritorio: panorámico 16:9, sin el bajo de pasteles; conserva cuernos, rostro, torso y cola.
portada_esc = cafe.crop((0, 0, 1536, 864))
exportar("aurelia-portada-escritorio", portada_esc)
# Móvil: cuadrado 1:1 que mantiene ambos cuernos (x 555–1070), el rostro (x 700–900) y la cola.
portada_mov = cafe.crop((90, 0, 1114, 1024))
exportar("aurelia-portada-movil", portada_mov)

# =========================================================================== informe
print(f"{'archivo':44s}{'px':>12s}{'KB':>8s}  nativo")
for nombre, w, h, b, nat in sorted(resultados):
    print(f"{nombre:44s}{w:>6d}x{h:<5d}{b/1024:>8.1f}  {nat}")
print("TOTAL KB:", round(sum(r[3] for r in resultados) / 1024, 1))
