#!/usr/bin/env python3
"""Genera las partes pixel art de los rigs (kobold e iguana) + assets/rig/rig.json.
Cada parte es un PNG del tamaño completo de la celda (36x32 kobold, 28x30 iguana) con solo sus píxeles,
así los pivotes están en coordenadas de la grilla y no hay recortes/offsets que mantener.
Uso: python3 tools/make_rig.py [assets/rig]"""
import sys, os, json
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/rig"

KP = dict(q=(230,100,110),c=(150,210,250),o=(250,140,40),T=(212,172,112),r=(196,62,52),R=(132,38,40),n=(222,120,102),y=(250,222,70),
          K=(18,12,20),k=(44,30,34),w=(244,240,226),W=(150,152,164),Y=(228,190,62),Z=(160,120,36),A=(214,220,232),s=(110,70,44))
IP = dict(g=(226,84,48),G=(160,50,40),e=(246,206,150),E=(222,170,112),u=(150,60,200),i=(255,255,255),K=(18,12,22),
          H=(70,84,168),h=(42,52,116),c=(84,104,178),C=(52,66,128),s=(122,66,52),S=(82,40,40),m=(236,74,208),M=(150,30,140),
          b=(132,72,176),B=(220,208,238),o=(250,150,40),p=(250,190,120))

class Layer:
    def __init__(s, w, h, pal): s.w, s.h, s.pal, s.p = w, h, pal, {}
    def px(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.p[(x, y)] = c
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.px(x, y, c)
    def pts(s, lst, c):
        for x, y in lst: s.px(x, y, c)
    def save(s, path):
        im = Image.new("RGBA", (s.w, s.h), (0, 0, 0, 0))
        for (x, y), c in s.p.items(): im.putpixel((x, y), s.pal[c] + (255,))
        im.save(path)

def save_all(d, layers):
    os.makedirs(d, exist_ok=True)
    for n, l in layers.items(): l.save(f"{d}/{n}.png")

# ───────────────────────── KOBOLD (36x32) ─────────────────────────
def kobold():
    mk = lambda: Layer(36, 32, KP)
    P = {}
    t = mk()
    for i, (x, y) in enumerate([(23,25),(24,26),(25,27),(26,27),(27,26),(28,25),(29,24),(30,23),(30,22)]):
        t.rect(x, y, x+1, y+1, 'r' if i < 7 else 'R')
    P['tail'] = t
    l = mk(); l.rect(12,26,15,29,'r'); l.rect(10,30,16,31,'r'); l.pts([(10,31),(12,31),(14,31)], 'K'); P['leg_L'] = l
    l = mk(); l.rect(20,26,23,29,'r'); l.rect(19,30,25,31,'r'); l.pts([(19,31),(21,31),(23,31)], 'K'); P['leg_R'] = l
    b = mk()
    b.rect(10,12,25,14,'r'); b.rect(12,14,23,21,'r'); b.rect(15,14,20,20,'n')
    b.pts([(13,15),(22,16),(14,18),(21,19),(11,13),(24,13)], 'R')
    for y in range(15, 21, 2): b.rect(16,y,19,y,'R')
    b.rect(12,21,23,21,'Z'); b.rect(13,22,22,27,'Y'); b.rect(15,28,20,28,'Y'); b.rect(17,22,18,27,'Z')
    P['torso'] = b
    a = mk(); a.rect(7,13,10,20,'r'); a.rect(7,16,10,18,'W'); a.rect(6,20,10,22,'r'); a.pts([(6,23),(8,23),(10,23)], 'K'); P['arm_L'] = a
    a = mk(); a.rect(25,13,28,19,'r'); a.rect(25,15,28,17,'W'); a.rect(26,19,29,21,'r'); a.pts([(26,22),(28,22)], 'K'); P['arm_R'] = a
    h = mk()
    h.pts([(12,4),(11,3),(10,2),(10,1),(9,0)], 'k'); h.pts([(13,4),(12,3),(11,2),(11,1),(10,0)], 'k')
    h.pts([(23,4),(24,3),(25,2),(25,1),(26,0)], 'k'); h.pts([(22,4),(23,3),(24,2),(24,1),(25,0)], 'k')
    h.rect(12,5,23,11,'r'); h.rect(11,7,11,10,'r'); h.rect(24,7,24,10,'r'); h.rect(15,9,20,11,'n'); h.pts([(16,10),(19,10)], 'K')
    P['head'] = h

    # caras (se dibujan encima de la cabeza y heredan su transformación)
    def face(fn):
        f = mk(); fn(f); return f
    def brows(f, y=6): f.rect(13,y,15,y,'R'); f.rect(20,y,22,y,'R')
    def eyes_open(f):
        f.rect(13,7,14,8,'y'); f.pts([(14,7),(14,8)], 'K'); f.rect(21,7,22,8,'y'); f.pts([(21,7),(21,8)], 'K')
    def eyes_closed(f): f.rect(13,8,14,8,'K'); f.rect(21,8,22,8,'K')
    def mouth_line(f): f.rect(16,11,19,11,'R'); f.pts([(16,11),(19,11)], 'w')
    def n(f): brows(f); eyes_open(f); mouth_line(f)
    def blink(f): brows(f); eyes_closed(f); mouth_line(f)
    def happy(f): brows(f, 5); eyes_closed(f); f.rect(16,11,19,11,'R'); f.pts([(15,10),(20,10)], 'R')
    def sing(f): brows(f, 5); eyes_closed(f); f.rect(15,11,20,14,'K'); f.rect(15,11,20,11,'w'); f.rect(17,14,18,14,'q')
    def sing_mid(f): brows(f, 5); eyes_closed(f); f.rect(16,11,19,12,'K'); f.rect(16,11,19,11,'w')
    def scared(f):
        f.rect(13,7,15,9,'w'); f.px(14,8,'K'); f.rect(20,7,22,9,'w'); f.px(21,8,'K')
        f.px(12,6,'R'); f.rect(13,5,14,5,'R'); f.px(23,6,'R'); f.rect(21,5,22,5,'R')
        f.rect(16,11,19,13,'K'); f.pts([(17,11),(18,11)], 'w'); f.pts([(10,6),(10,7),(25,5),(25,6),(26,6)], 'c')
    def angry(f):
        f.pts([(12,6),(13,6),(14,7),(15,7),(23,6),(22,6),(21,7),(20,7)], 'R')
        f.rect(13,8,14,9,'y'); f.pts([(14,8),(14,9)], 'K'); f.rect(21,8,22,9,'y'); f.pts([(21,8),(21,9)], 'K')
        f.rect(16,11,19,12,'K'); f.pts([(16,11),(19,11),(17,12),(18,12)], 'w')
    def hurt(f):
        f.pts([(13,7),(14,8),(13,9),(22,7),(21,8),(22,9)], 'K'); brows(f, 6)
        f.rect(16,11,19,12,'K'); f.rect(16,11,19,11,'w')
    def dead(f):
        f.pts([(13,7),(15,7),(14,8),(13,9),(15,9),(20,7),(22,7),(21,8),(20,9),(22,9)], 'K')
        f.rect(16,11,19,11,'K'); f.rect(17,12,18,12,'q')
    FACES = {k: face(v) for k, v in dict(normal=n, blink=blink, happy=happy, sing=sing, sing_mid=sing_mid, scared=scared,
                                          angry=angry, hurt=hurt, dead=dead).items()}

    # props por kobold: (mano, layer). Los props se pegan al brazo (heredan su rotación).
    def L_(): return mk()
    props = {}
    def add(i, hand, fn):
        l = L_(); fn(l); props.setdefault(i, {})[hand] = l
    # 0 Julia: libro de cuentas + cucharón
    add(0, 'L', lambda l: (l.rect(3,16,8,22,'s'), l.rect(4,17,7,21,'w'), l.rect(5,18,6,18,'k'), l.rect(5,20,6,20,'k')))
    add(0, 'R', lambda l: (l.rect(28,10,28,20,'s'), l.rect(27,6,29,9,'A'), l.px(28,7,'k'), l.px(28,8,'k')))
    # 1 Piedrín: barril
    add(1, 'L', lambda l: (l.rect(0,14,8,24,'s'), l.rect(0,16,8,16,'k'), l.rect(0,22,8,22,'k'), l.rect(1,14,7,14,'Z')))
    # 2 Braulio: mandolina
    add(2, 'R', lambda l: (l.rect(27,18,33,24,'s'), l.rect(29,20,31,22,'K'), l.rect(31,8,32,17,'s'),
                           l.pts([(30,8),(33,9),(30,11),(33,12)], 'y')))
    # 3 Chispa: antorcha + barril de pólvora
    add(3, 'R', lambda l: (l.rect(28,10,28,20,'s'), l.rect(27,5,29,9,'y'), l.rect(28,6,28,8,'o'), l.px(28,4,'y')))
    add(3, 'L', lambda l: (l.rect(3,19,8,24,'k'), l.rect(3,20,8,20,'W'), l.rect(3,23,8,23,'W')))
    # 4 Zurdito: catalejo
    def cat(l):
        for i in range(9): l.px(27+i, 19-i, 's'); l.px(28+i, 19-i, 's')
        l.pts([(35,10),(34,10),(33,10)], 'A')
    add(4, 'R', cat)
    # 5 Pancho: martillo + tabla
    add(5, 'R', lambda l: (l.rect(28,12,28,20,'s'), l.rect(26,8,31,12,'W'), l.rect(26,8,31,8,'A')))
    add(5, 'L', lambda l: (l.rect(0,17,9,19,'Z'), l.rect(0,17,9,17,'T')))
    # 6 Lola: soga
    add(6, 'L', lambda l: (l.rect(4,11,9,16,'T'), l.rect(5,12,8,15,'R')))
    add(6, 'R', lambda l: (l.rect(28,19,29,27,'T'), l.px(30,27,'T')))

    layers = dict(P)
    for k, f in FACES.items(): layers[f"face_{k}"] = f
    for i, d in props.items():
        for hand, l in d.items(): layers[f"prop_{hand}_{i}"] = l
    rig = {
        "size": [36, 32], "feet": [18, 32],
        "parts": [  # orden = z (atrás → adelante)
            {"n": "tail",  "parent": "root",  "pivot": [23, 25]},
            {"n": "leg_L", "parent": "root",  "pivot": [13, 25]},
            {"n": "leg_R", "parent": "root",  "pivot": [21, 25]},
            {"n": "torso", "parent": "root",  "pivot": [18, 24]},
            {"n": "arm_L", "parent": "torso", "pivot": [9, 14]},
            {"n": "arm_R", "parent": "torso", "pivot": [26, 14]},
            {"n": "head",  "parent": "torso", "pivot": [18, 12]},
        ],
        "faces": list(FACES.keys()), "face_parent": "head",
        "props": {str(i): {h: f"prop_{h}_{i}" for h in d} for i, d in props.items()},
        "prop_parent": {"L": "arm_L", "R": "arm_R"},
        "anchors": {"hand_L": ["arm_L", 8, 22], "hand_R": ["arm_R", 27, 21], "head_top": ["head", 18, 0]},
    }
    return layers, rig

# ───────────────────────── IGUANA (28x30) ─────────────────────────
def iguana():
    mk = lambda: Layer(28, 30, IP)
    P = {}
    t = mk()
    for i, (x, y) in enumerate([(22,27),(23,28),(24,28),(25,27),(26,26),(26,24)]):
        c = 'g' if i % 2 == 0 else 'G'; t.px(x, y, c); t.px(x, y+1, c)
    P['tail'] = t
    c = mk()
    for r in range(19, 28):
        l = 6 - (r-19)//5; rr = 21 + (r-19)//5
        c.rect(l, r, rr, r, 'c'); c.rect(l, r, l+2, r, 'C')
    P['cape'] = c
    l = mk(); l.rect(8,27,11,28,'g'); l.pts([(8,29),(10,29)], 'K'); P['leg_L'] = l
    l = mk(); l.rect(16,27,19,28,'g'); l.pts([(16,29),(18,29)], 'K'); P['leg_R'] = l
    b = mk(); b.rect(10,19,16,26,'e'); b.pts([(13,20),(13,21)], 'o')
    for r in (22, 24): b.px(11, r, 'E'); b.px(15, r+1, 'E')
    P['torso'] = b
    k = mk(); k.rect(17,20,23,26,'b'); k.rect(18,21,22,25,'B'); k.rect(17,20,17,26,'M')
    for r in (22, 24): k.rect(18, r, 21, r, 'b')
    k.rect(14,23,17,24,'g'); P['book'] = k
    s = mk(); s.rect(2,5,2,29,'s'); s.rect(3,7,3,29,'S')
    s.pts([(2,0),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(4,2),(1,3),(2,3),(3,3),(2,4)], 'm')
    s.px(2,1,'i'); s.px(1,2,'M'); s.px(3,3,'M'); P['staff'] = s
    a = mk(); a.rect(4,20,7,21,'g'); a.pts([(3,20),(3,21)], 'g'); P['arm_s'] = a
    h = mk()
    rows = {4:(16,18),5:(14,17),6:(12,16),7:(11,16),8:(10,17),9:(9,18)}
    for y, (x0, x1) in rows.items(): h.rect(x0, y, x1, y, 'H')
    h.pts([(19,4),(19,3),(18,3)], 'h')
    for y, (x0, x1) in rows.items(): h.px(x1, y, 'h')
    h.rect(6,10,22,10,'h'); h.rect(7,10,21,10,'H'); h.rect(6,11,22,11,'h')
    P['hat'] = h
    d = mk()
    d.rect(8,11,20,17,'g'); d.rect(7,13,8,16,'g'); d.rect(10,16,18,17,'e'); d.rect(10,15,18,15,'G'); d.rect(11,18,15,18,'g')
    d.pts([(21,13),(22,14),(21,15),(22,16),(21,17),(6,14),(5,15),(6,16),(5,17)], 'p')
    P['head'] = d

    def face(fn):
        f = mk(); fn(f); return f
    def eyes(f):
        f.rect(10,12,12,14,'i'); f.rect(11,12,12,14,'u'); f.px(11,13,'K'); f.px(10,12,'i')
        f.rect(16,12,18,14,'i'); f.rect(17,12,18,14,'u'); f.px(17,13,'K'); f.px(16,12,'i')
    def n(f): eyes(f)
    def blink(f): f.rect(10,13,12,13,'G'); f.rect(16,13,18,13,'G')
    def cast(f):
        f.rect(10,12,12,14,'m'); f.px(11,13,'i'); f.rect(16,12,18,14,'m'); f.px(17,13,'i'); f.rect(12,18,14,19,'K')
    def angry(f):
        eyes(f); f.rect(10,12,12,12,'G'); f.rect(16,12,18,12,'G'); f.px(12,11,'G'); f.px(16,11,'G'); f.rect(11,18,15,18,'G')
    def scared(f):
        f.rect(10,12,12,14,'i'); f.px(11,13,'K'); f.rect(16,12,18,14,'i'); f.px(17,13,'K'); f.rect(12,18,14,19,'K')
    def sad(f):
        f.rect(10,13,12,14,'i'); f.rect(11,13,12,14,'u'); f.px(11,14,'K'); f.rect(16,13,18,14,'i'); f.rect(17,13,18,14,'u'); f.px(17,14,'K')
        f.rect(10,12,12,12,'g'); f.rect(16,12,18,12,'g'); f.pts([(10,11),(18,11)], 'G'); f.rect(11,18,15,18,'G'); f.pts([(11,17),(15,17)], 'G')
    def hollow(f):
        f.rect(10,12,12,14,'i'); f.px(11,14,'K'); f.rect(16,12,18,14,'i'); f.px(17,14,'K'); f.rect(11,18,15,18,'G')
    FACES = {k: face(v) for k, v in dict(normal=n, blink=blink, cast=cast, angry=angry, scared=scared, sad=sad, hollow=hollow).items()}

    layers = dict(P)
    for k, f in FACES.items(): layers[f"face_{k}"] = f
    rig = {
        "size": [28, 30], "feet": [14, 30],
        "parts": [
            {"n": "tail",  "parent": "root",  "pivot": [22, 27]},
            {"n": "cape",  "parent": "torso", "pivot": [14, 19]},
            {"n": "leg_L", "parent": "root",  "pivot": [10, 27]},
            {"n": "leg_R", "parent": "root",  "pivot": [17, 27]},
            {"n": "torso", "parent": "root",  "pivot": [13, 26]},
            {"n": "book",  "parent": "torso", "pivot": [15, 24]},
            {"n": "staff", "parent": "arm_s", "pivot": [3, 21]},
            {"n": "arm_s", "parent": "torso", "pivot": [8, 21]},
            {"n": "hat",   "parent": "head",  "pivot": [14, 11]},
            {"n": "head",  "parent": "torso", "pivot": [14, 18]},
        ],
        "faces": list(FACES.keys()), "face_parent": "head",
        "props": {}, "prop_parent": {},
        "anchors": {"crystal": ["staff", 2, 2], "hand_book": ["book", 15, 24]},
    }
    return layers, rig

if __name__ == "__main__":
    rig = {}
    for name, fn in (("kobold", kobold), ("iguana", iguana)):
        layers, r = fn(); save_all(f"{OUT}/{name}", layers); rig[name] = r
        print(name, len(layers), "capas")
    json.dump(rig, open(f"{OUT}/rig.json", "w"), indent=1)
    # hoja de contacto para ver las partes y caras
    sheet = Image.new("RGBA", (640, 200), (26, 22, 38, 255))
    def comp(name, order, faces, x0, y0):
        for k in order:
            sheet.alpha_composite(Image.open(f"{OUT}/{name}/{k}.png"), (x0, y0))
        for j, f in enumerate(faces):
            base = Image.new("RGBA", (36 if name == "kobold" else 28, 32 if name == "kobold" else 30), (0, 0, 0, 0))
            for k in order: base.alpha_composite(Image.open(f"{OUT}/{name}/{k}.png"))
            base.alpha_composite(Image.open(f"{OUT}/{name}/face_{f}.png"))
            sheet.alpha_composite(base, (x0 + 40 * j, y0 + 40))
    ko = [p["n"] for p in rig["kobold"]["parts"]]
    comp("kobold", ko, rig["kobold"]["faces"], 4, 4)
    io = [p["n"] for p in rig["iguana"]["parts"]]
    comp("iguana", io, rig["iguana"]["faces"], 4, 100)
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(f"{OUT}/contact_sheet.png")
