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


# ───────────────────────── KENKU PALADÍN (44x56) ─────────────────────────
NP = dict(W=(238,234,226),V=(196,192,190),L=(222,176,66),l=(150,110,40),B=(112,74,46),k=(28,26,36),F=(70,68,90),S=(204,208,218),s=(122,126,140),
          A=(244,247,252),a=(252,176,40),e=(255,226,140),K=(14,10,18),b=(66,60,74),g=(108,102,120),q=(200,90,100),H=(232,238,255),h=(160,172,214))
def kenku():
    mk = lambda: Layer(44, 56, NP)
    P = {}
    def shape(l, rows, c):
        for y, (x0, x1) in rows.items(): l.rect(x0, y, x1, y, c)
    # halo solar plateado (anillo + 8 rayos), centro (22,12)
    import math
    hl = mk(); cx, cy = 22, 12
    for y in range(0, 25):
        for x in range(8, 37):
            d = math.hypot(x - cx, y - cy)
            if 8.4 <= d <= 9.6: hl.px(x, y, 'H')
            elif 9.6 < d <= 10.4: hl.px(x, y, 'h')
    for k in range(8):
        a = k * math.pi / 4; ln = 12.6 if k % 2 == 0 else 11.6
        r = 10.5
        while r <= ln:
            hl.px(round(cx + math.cos(a) * r), round(cy + math.sin(a) * r), 'H'); r += 0.6
    P['halo'] = hl
    # cinta/capa
    cp = mk(); cp.rect(12,20,32,47,'V'); cp.rect(16,21,16,47,'L'); cp.rect(28,21,28,47,'L'); cp.rect(12,47,32,47,'L')
    for y in range(24, 47, 6): cp.rect(13,y,15,y,'W'); cp.rect(29,y,31,y,'W')
    P['cape'] = cp
    for side, sgn in (('L', -1), ('R', 1)):
        r = mk()
        for y in range(22, 47):
            off = (y - 22) // 3; x0 = 12 + 0 if sgn > 0 else 12 - off - 3
            if sgn < 0: r.rect(10 - off, y, 12, y, 'W'); r.px(10 - off, y, 'L'); r.px(11 - off, y, 'V')
            else: r.rect(32, y, 34 + off, y, 'W'); r.px(34 + off, y, 'L'); r.px(33 + off, y, 'V')
        P['ribbon_' + side] = r
    t = mk()
    for (x, y) in [(13,42),(14,44),(15,46),(29,42),(30,44),(31,46),(20,48),(22,49),(24,48)]:
        t.rect(x, y, x + 1, y + 3, 'k'); t.px(x, y, 'F')
    P['tail'] = t
    for side, x0 in (('L', 16), ('R', 24)):
        l = mk(); l.rect(x0, 40, x0 + 4, 51, 'W'); l.rect(x0, 40, x0, 51, 'V'); l.rect(x0, 43, x0 + 4, 44, 'L'); l.rect(x0 + 1, 44, x0 + 3, 44, 'W')
        l.rect(x0 - 1, 52, x0 + 5, 54, 'k'); l.pts([(x0 - 2, 55), (x0, 55), (x0 + 2, 55), (x0 + 4, 55), (x0 + 6, 55)], 'k'); l.pts([(x0 - 1, 52), (x0 + 3, 53)], 'F')
        P['leg_' + side] = l
    # torso
    b = mk()
    b.rect(15,19,29,37,'W'); b.rect(15,19,16,37,'V'); b.rect(17,20,17,37,'L'); b.rect(27,20,27,37,'L')
    b.rect(17,37,27,45,'W'); b.rect(17,45,27,45,'L'); b.rect(17,37,17,45,'V')
    for (x, y) in [(22,23),(22,29),(19,26),(25,26),(20,24),(24,24),(20,28),(24,28)]: b.px(x, y, 'L')
    b.rect(21,25,23,27,'L'); b.px(22,26,'e')
    for (x, y) in [(22,40),(22,42),(21,41),(23,41)]: b.px(x, y, 'L')
    for i in range(13): b.rect(16 + i, 20 + i, 17 + i, 20 + i, 'B')       # tahalí diagonal
    b.rect(15,32,29,33,'B'); b.rect(21,32,23,33,'L'); b.rect(26,34,28,37,'B')
    for rows, x_ in (({18:(11,15),19:(9,16),20:(9,16),21:(9,16),22:(9,16),23:(10,15)}, 0), ({18:(29,33),19:(28,35),20:(28,35),21:(28,35),22:(28,35),23:(29,34)}, 1)):
        shape(b, rows, 'W'); y0, y1 = (9, 16) if x_ == 0 else (28, 35)
        b.rect(y0, 21, y1, 21, 'L'); b.px(y0 + 1, 19, 'L'); b.px(y1 - 1, 19, 'L')
        b.rect(y0, 22, y0, 22, 'V') if x_ == 0 else b.rect(y1, 22, y1, 22, 'V')
    b.rect(17,17,27,19,'W'); b.rect(17,19,27,19,'L')
    P['torso'] = b
    # brazos
    a = mk(); a.rect(9,22,13,31,'W'); a.rect(9,22,9,31,'V'); a.rect(9,26,13,26,'L'); a.rect(8,31,12,35,'S'); a.rect(8,31,8,35,'s'); a.rect(8,31,12,31,'L')
    a.rect(8,36,12,38,'k'); a.pts([(8,39),(10,39),(12,39)], 'k'); a.px(9,36,'F'); P['arm_L'] = a
    a = mk(); a.rect(31,22,35,31,'W'); a.rect(35,22,35,31,'V'); a.rect(31,26,35,26,'L'); a.rect(32,31,36,35,'S'); a.rect(36,31,36,35,'s'); a.rect(32,31,36,31,'L')
    a.rect(32,36,36,38,'k'); a.pts([(32,39),(34,39),(36,39)], 'k'); a.px(33,36,'F'); P['arm_R'] = a
    # capucha (detrás de la cabeza) y cabeza
    hd = mk()
    shape(hd, {2:(20,24),3:(18,26),4:(17,27),5:(16,28),6:(15,29),7:(14,30),8:(14,30),9:(14,30),10:(14,30),11:(14,30),12:(14,30),13:(14,30),14:(14,30),15:(14,30),16:(14,30),17:(15,29),18:(15,29),19:(16,28)}, 'W')
    for y in range(7, 19): hd.px(14, y, 'V'); hd.px(15, y, 'V')
    for x in range(17, 28): hd.px(x, 4 if 17 < x < 27 else 5, 'W')
    hd.rect(20,2,24,2,'L'); hd.pts([(18,3),(26,3),(17,4),(27,4),(16,5),(28,5),(15,6),(29,6)], 'L')
    for y in range(7, 19): hd.px(16, y, 'L'); hd.px(28, y, 'L')
    hd.rect(16,19,28,19,'L'); hd.px(22,3,'e')
    P['hood'] = hd
    h = mk()
    shape(h, {6:(20,24),7:(18,26),8:(17,27),9:(17,27),10:(17,27),11:(17,27),12:(17,27),13:(18,26),14:(18,26),15:(19,25),16:(20,24),17:(19,25),18:(19,25)}, 'k')
    h.pts([(19,7),(18,8),(25,7),(26,8),(18,13),(26,13)], 'F'); h.pts([(16,11),(16,12),(28,11),(28,12)], 'k')
    P['head'] = h
    def face(fn):
        f = mk(); fn(f); return f
    def eyes(f, c='a'):
        for ex in (18, 25): f.rect(ex, 10, ex + 1, 11, c); f.px(ex, 10, 'e')
    def beak_closed(f):
        shape(f, {10:(21,23),11:(20,24),12:(20,24),13:(21,23),14:(21,23),15:(22,22),16:(22,22)}, 'b'); f.rect(21,11,21,14,'g'); f.px(22,10,'g')
    def beak_open(f):
        shape(f, {10:(21,23),11:(20,24),12:(20,24),13:(21,23)}, 'b'); f.rect(21,11,21,12,'g')
        f.rect(21,14,23,15,'K'); f.px(22,15,'q'); shape(f, {16:(21,23),17:(22,22)}, 'b')
    def n(f): eyes(f); beak_closed(f)
    def blink(f): f.rect(18,11,19,11,'a'); f.rect(25,11,26,11,'a'); beak_closed(f)
    def angry(f): f.pts([(18,11),(19,11),(19,10),(26,11),(25,11),(25,10)], 'a'); f.pts([(18,10),(26,10)], 'K'); beak_closed(f)
    def serene(f): f.rect(18,10,19,10,'a'); f.rect(18,11,19,11,'l'); f.rect(25,10,26,10,'a'); f.rect(25,11,26,11,'l'); beak_closed(f)
    def hurt(f): f.pts([(18,10),(19,11),(18,12),(26,10),(25,11),(26,12)], 'a'); beak_open(f)
    def speak(f): eyes(f); beak_open(f)
    def dead(f): f.pts([(18,10),(20,10),(19,11),(18,12),(20,12),(24,10),(26,10),(25,11),(24,12),(26,12)], 'l'); beak_open(f)
    FACES = {k: face(v) for k, v in dict(normal=n, blink=blink, angry=angry, serene=serene, hurt=hurt, speak=speak, dead=dead).items()}
    # props: lanza solar (mano izq) y escudo de sol (mano der)
    sp = mk(); sp.rect(9,8,9,50,'S'); sp.rect(10,8,10,50,'s'); sp.pts([(9,14),(9,22),(9,30),(10,18),(10,26)], 'L')
    shape(sp, {0:(9,9),1:(8,10),2:(8,10),3:(8,10),4:(8,10),5:(9,10),6:(9,10),7:(9,10)}, 'A'); sp.rect(10,1,10,6,'S'); sp.rect(8,7,11,7,'L')
    for (x, y) in [(5,10),(6,9),(7,8),(4,11),(5,12),(6,13),(7,14),(11,8),(12,9),(13,10),(14,11),(13,12),(12,13),(11,14)]: sp.px(x, y, 'L')
    sp.rect(7,10,11,12,'L'); sp.px(9,11,'e')
    sp.rect(8,36,12,37,'k'); sp.pts([(8,38),(10,38),(12,38)], 'k')        # puño sobre el asta
    sh = mk(); rows = {23:(34,40),24:(32,42),36:(32,42),37:(32,42),38:(33,41),39:(33,41),40:(34,40),41:(35,39),42:(36,38),43:(37,37)}
    for y in range(25, 36): rows[y] = (31, 43)
    for y, (x0, x1) in rows.items():
        sh.rect(x0, y, x1, y, 'W'); sh.px(x0, y, 'L'); sh.px(x1, y, 'L')
        if y in (23, 43): sh.rect(x0, y, x1, y, 'L')
    sh.rect(32,24,42,24,'L'); sh.rect(33,38,41,38,'L'); sh.rect(34,25,34,36,'V'); sh.rect(35,25,35,36,'V')
    for (x, y) in [(37,26),(37,36),(32,31),(42,31),(33,27),(41,27),(33,35),(41,35),(35,29),(39,29),(35,33),(39,33)]: sh.px(x, y, 'L')
    sh.rect(36,30,38,32,'L'); sh.px(37,31,'e'); sh.rect(37,23,37,24,'L')
    layers = dict(P)
    for k, f in FACES.items(): layers[f"face_{k}"] = f
    layers["prop_L_0"] = sp; layers["prop_R_0"] = sh
    rig = {
        "size": [44, 56], "feet": [22, 56],
        "parts": [
            {"n": "halo",     "parent": "head",  "pivot": [22, 12]},
            {"n": "ribbon_L", "parent": "torso", "pivot": [12, 22]},
            {"n": "ribbon_R", "parent": "torso", "pivot": [32, 22]},
            {"n": "cape",     "parent": "torso", "pivot": [22, 20]},
            {"n": "tail",     "parent": "root",  "pivot": [22, 38]},
            {"n": "leg_L",    "parent": "root",  "pivot": [18, 39]},
            {"n": "leg_R",    "parent": "root",  "pivot": [26, 39]},
            {"n": "torso",    "parent": "root",  "pivot": [22, 38]},
            {"n": "arm_L",    "parent": "torso", "pivot": [12, 22]},
            {"n": "arm_R",    "parent": "torso", "pivot": [32, 22]},
            {"n": "hood",     "parent": "head",  "pivot": [22, 18]},
            {"n": "head",     "parent": "torso", "pivot": [22, 18]},
        ],
        "faces": list(FACES.keys()), "face_parent": "head",
        "props": {"0": {"L": "prop_L_0", "R": "prop_R_0"}}, "prop_parent": {"L": "arm_L", "R": "arm_R"},
        "anchors": {"halo": ["halo", 22, 12], "spear_tip": ["arm_L", 9, 0], "shield": ["arm_R", 37, 31]},
    }
    return layers, rig

def shrink(layer, f, pal, accent=('L', 'a', 'e', 'A', 'H', 'p')):
    """Reescala una capa pixel art por f<1 (filtro de moda; los colores de acento ganan para no perder detalles finos)."""
    from collections import Counter
    W, H = max(1, round(layer.w * f)), max(1, round(layer.h * f))
    out = Layer(W, H, pal)
    for ty in range(H):
        for tx in range(W):
            x0, x1, y0, y1 = int(tx / f), int((tx + 1) / f + 0.999), int(ty / f), int((ty + 1) / f + 0.999)
            cs = [layer.p[(x, y)] for y in range(y0, y1) for x in range(x0, x1) if (x, y) in layer.p]
            tot = (x1 - x0) * (y1 - y0)
            if len(cs) < 0.4 * tot: continue
            cnt = Counter(cs); acc = [c for c in cnt if c in accent]
            out.px(tx, ty, acc[0] if acc and cnt[acc[0]] >= 0.3 * len(cs) else cnt.most_common(1)[0][0])
    return out

def kenku_small(f=0.75):
    layers, rig = kenku()
    sc = lambda v: round(v * f)
    new = {}
    for k, l in layers.items():
        if k.startswith("face_"): continue
        new[k] = shrink(l, f, NP)
    W, H = new["torso"].w, new["torso"].h
    mk = lambda: Layer(W, H, NP)
    def face(fn):
        q = mk(); fn(q); return q
    # cabeza reducida: centro x=16/17, ojos y=8, pico y 7-12
    def eyes(q, c='a'): q.rect(13, 8, 14, 8, c); q.rect(19, 8, 20, 8, c); q.px(13, 7, 'e'); q.px(20, 7, 'e')
    def beak_closed(q):
        q.rect(16,7,17,7,'b'); q.rect(15,8,18,9,'b'); q.rect(16,10,17,11,'b'); q.px(16,12,'b'); q.px(16,8,'g'); q.px(16,9,'g')
    def beak_open(q):
        q.rect(16,7,17,7,'b'); q.rect(15,8,18,8,'b'); q.px(16,8,'g'); q.rect(16,9,17,9,'K'); q.px(16,10,'q'); q.rect(16,11,17,11,'b'); q.px(16,12,'b')
    def n(q): eyes(q); beak_closed(q)
    def blink(q): q.rect(13,8,14,8,'l'); q.rect(19,8,20,8,'l'); beak_closed(q)
    def angry(q): q.pts([(13,8),(14,8),(14,7),(19,8),(20,8),(19,7)], 'a'); beak_closed(q)
    def serene(q): q.rect(13,8,14,8,'l'); q.rect(19,8,20,8,'l'); q.px(13,7,'a'); q.px(20,7,'a'); beak_closed(q)
    def hurt(q): q.pts([(13,7),(14,8),(13,9),(20,7),(19,8),(20,9)], 'a'); beak_open(q)
    def speak(q): eyes(q); beak_open(q)
    def dead(q): q.pts([(13,7),(14,8),(13,9),(14,7),(20,7),(19,8),(20,9),(19,7)], 'l'); beak_open(q)
    FACES = dict(normal=n, blink=blink, angry=angry, serene=serene, hurt=hurt, speak=speak, dead=dead)
    for k, fn in FACES.items(): new[f"face_{k}"] = face(fn)
    r = rig
    r["size"] = [W, H]; r["feet"] = [sc(r["feet"][0]), H]
    for p_ in r["parts"]: p_["pivot"] = [sc(p_["pivot"][0]), sc(p_["pivot"][1])]
    for a, v in r["anchors"].items(): r["anchors"][a] = [v[0], sc(v[1]), sc(v[2])]
    return new, r

# ───────────────────────── DEI (48x64): dracónido bardo ─────────────────────────
DP = dict(u=(88,56,128),D=(40,28,64),U=(140,100,188),m=(112,76,150),p=(236,110,255),W=(244,240,236),w=(214,208,214),J=(26,24,34),j=(60,58,74),
          c=(156,40,52),v=(112,32,54),L=(222,176,66),K=(14,10,18),O=(198,136,64),o=(118,74,38),S=(200,204,214),q=(210,90,110),Z=(150,232,255),z=(250,255,255))
def dei():
    mk = lambda: Layer(48, 64, DP)
    P = {}
    t = mk()
    for i, (x, y) in enumerate([(29,44),(31,46),(33,48),(35,50),(37,52),(39,53),(41,53),(43,52),(44,50)]):
        t.rect(x, y, x + 2, y + 2, 'u' if i % 2 == 0 else 'D')
    t.px(44, 49, 'U'); P['tail'] = t
    for side, x0 in (('L', 18), ('R', 25)):
        l = mk(); l.rect(x0, 44, x0 + 4, 59, 'J'); l.rect(x0, 44, x0, 59, 'j'); l.rect(x0 - 2, 59, x0 + 5, 62, 'K'); l.rect(x0 - 2, 59, x0 + 5, 59, 'j')
        P['leg_' + side] = l
    b = mk()
    b.rect(12,19,36,23,'J'); b.rect(14,23,34,40,'J'); b.rect(14,23,15,40,'j'); b.rect(33,23,34,40,'j')
    b.rect(20,21,28,40,'v'); b.rect(21,21,27,24,'W'); b.pts([(21,21),(22,22),(26,22),(27,21)], 'w')      # chaleco + camisa
    b.rect(23,22,25,31,'J'); b.rect(24,22,24,22,'j')                                                    # corbata
    for y in (26, 30, 34, 38): b.px(24, y, 'L')
    b.rect(18,21,20,32,'j'); b.rect(28,21,30,32,'j')                                                    # solapas
    b.rect(15,40,23,48,'J'); b.rect(25,40,33,48,'J'); b.rect(15,40,15,48,'j'); b.rect(33,40,33,48,'j'); b.rect(15,44,15,44,'c')
    P['torso'] = b
    for side, x0, hx in (('L', 9, 8), ('R', 34, 34)):
        a = mk(); a.rect(x0, 21, x0 + 4, 34, 'J'); a.rect(x0 if side == 'L' else x0 + 4, 21, x0 if side == 'L' else x0 + 4, 34, 'j')
        a.rect(x0, 34, x0 + 4, 36, 'c'); a.rect(x0, 37, x0 + 4, 37, 'W')
        a.rect(hx, 38, hx + 5, 41, 'u'); a.rect(hx, 38, hx + 5, 38, 'U'); a.pts([(hx, 42), (hx + 2, 42), (hx + 4, 42), (hx + 5, 42)], 'K')
        P['arm_' + side] = a
    # laúd (parte del torso, se puede ocultar)
    lu = mk()
    import math
    for y in range(36, 56):
        for x in range(16, 40):
            d = ((x - 28) / 9.0) ** 2 + ((y - 45) / 7.2) ** 2
            if d <= 1: lu.px(x, y, 'O' if d < .8 else 'o')
    for k in range(14): lu.rect(24 - k, 40 - k, 25 - k, 41 - k, 'o')                          # mástil diagonal
    lu.rect(8,24,14,27,'o'); lu.pts([(7,23),(9,22),(11,22),(13,22)], 'L')                       # clavijero
    lu.rect(26,42,29,46,'K'); lu.rect(27,43,28,45,'o'); lu.px(35, 42, 'S'); lu.rect(32,47,38,47,'S')
    P['lute'] = lu
    # cabeza dracónida
    h = mk()
    h.pts([(18,5),(17,4),(16,3),(15,2),(14,1),(14,0)], 'D'); h.pts([(30,5),(31,4),(32,3),(33,2),(34,1),(34,0)], 'D')
    h.pts([(19,5),(18,4),(17,3),(16,2),(15,1)], 'u'); h.pts([(29,5),(30,4),(31,3),(32,2),(33,1)], 'u')
    for x in (22, 24, 26): h.rect(x, 1, x, 4, 'D')
    rows = {4:(19,29),5:(18,30),6:(17,31),7:(17,31),8:(17,31),9:(17,31),10:(18,30),11:(19,29),12:(19,29),13:(20,28),14:(20,28),15:(20,28),16:(21,27),17:(21,27),18:(21,27),19:(20,28)}
    for y, (x0, x1) in rows.items(): h.rect(x0, y, x1, y, 'u')
    for y in range(11, 18): h.rect(20, y, 28, y, 'm')
    h.rect(18,6,18,9,'D'); h.rect(30,6,30,9,'D'); h.rect(21,4,27,5,'U'); h.pts([(19,9),(29,9)], 'D')
    h.pts([(22,12),(26,12)], 'D')                                                              # fosas nasales
    P['head'] = h
    def face(fn):
        f = mk(); fn(f); return f
    def eyes(f, c='p'):
        f.rect(19,7,21,8,c); f.px(21,7,'W'); f.rect(27,7,29,8,c); f.px(27,7,'W'); f.rect(19,6,21,6,'D'); f.rect(27,6,29,6,'D')
    def mouth_closed(f): f.rect(22,16,26,16,'D'); f.pts([(22,17),(26,17)], 'w')
    def mouth_open(f): f.rect(21,16,27,19,'K'); f.rect(21,16,27,16,'w'); f.rect(23,19,25,19,'q'); f.pts([(21,17),(27,17)], 'w')
    def n(f): eyes(f); mouth_closed(f)
    def blink(f): f.rect(19,8,21,8,'p'); f.rect(27,8,29,8,'p'); mouth_closed(f)
    def smirk(f): eyes(f); f.rect(22,16,26,16,'D'); f.pts([(27,15),(21,17)], 'D'); f.px(26,17,'w')
    def angry(f): eyes(f); f.pts([(19,6),(20,6),(21,7),(29,6),(28,6),(27,7)], 'K'); f.rect(21,16,27,17,'K'); f.pts([(21,16),(27,16),(23,17),(25,17)], 'w')
    def sing(f): eyes(f); mouth_open(f)
    def cast(f): eyes(f, 'z'); f.rect(19,7,21,8,'Z'); f.rect(27,7,29,8,'Z'); mouth_open(f)
    def hurt(f): f.pts([(19,7),(20,8),(19,9),(29,7),(28,8),(29,9)], 'p'); mouth_open(f)
    def dead(f): f.pts([(19,7),(21,7),(20,8),(19,9),(21,9),(27,7),(29,7),(28,8),(27,9),(29,9)], 'p'); f.rect(22,16,26,16,'K'); f.rect(24,17,25,18,'q')
    FACES = {k: face(v) for k, v in dict(normal=n, blink=blink, smirk=smirk, angry=angry, sing=sing, cast=cast, hurt=hurt, dead=dead).items()}
    layers = dict(P)
    for k, f in FACES.items(): layers[f"face_{k}"] = f
    rig = {"size": [48, 64], "feet": [24, 64],
        "parts": [
            {"n": "tail",  "parent": "root",  "pivot": [30, 44]},
            {"n": "leg_L", "parent": "root",  "pivot": [21, 43]},
            {"n": "leg_R", "parent": "root",  "pivot": [27, 43]},
            {"n": "torso", "parent": "root",  "pivot": [24, 42]},
            {"n": "lute",  "parent": "torso", "pivot": [24, 44]},
            {"n": "arm_L", "parent": "torso", "pivot": [12, 22]},
            {"n": "arm_R", "parent": "torso", "pivot": [36, 22]},
            {"n": "head",  "parent": "torso", "pivot": [24, 19]},
        ],
        "faces": list(FACES.keys()), "face_parent": "head", "props": {}, "prop_parent": {},
        "anchors": {"hand_L": ["arm_L", 10, 41], "hand_R": ["arm_R", 36, 41], "head_top": ["head", 24, 0], "eyes": ["head", 24, 8], "lute": ["lute", 28, 45]}}
    return layers, rig

# ───────────────────────── HANS (40x58): semielfo rubio de traje verde ─────────────────────────
HP = dict(p=(238,200,168),P=(206,164,136),h=(236,198,84),H=(252,228,132),g=(188,146,50),e=(70,164,96),w=(246,244,238),G=(54,124,76),F=(32,84,50),
          f=(78,160,102),L=(222,176,66),B=(104,68,42),b=(34,62,46),c=(150,36,52),K=(18,14,20),q=(210,100,110),S=(214,222,232))
def hans():
    mk = lambda: Layer(40, 58, HP)
    P = {}
    for side, x0 in (('L', 14), ('R', 21)):
        l = mk(); l.rect(x0, 44, x0 + 4, 54, 'G'); l.rect(x0, 44, x0, 54, 'F'); l.rect(x0 - 1, 54, x0 + 5, 57, 'B'); l.rect(x0 - 1, 54, x0 + 5, 54, 'K')
        P['leg_' + side] = l
    b = mk()
    b.rect(11,19,29,24,'G'); b.rect(12,24,28,40,'G'); b.rect(12,24,13,40,'F'); b.rect(27,24,28,40,'F')
    b.rect(17,20,23,40,'w'); b.rect(17,20,17,40,'S'); b.rect(19,22,21,24,'L'); b.rect(19,26,21,26,'c')    # camisa + broche + cravat
    b.rect(14,20,17,32,'f'); b.rect(23,20,26,32,'f'); b.rect(14,20,14,32,'F'); b.rect(26,20,26,32,'F')   # solapas
    b.pts([(20,30),(20,34)], 'L'); b.rect(12,38,28,39,'B'); b.rect(19,38,21,39,'L')
    b.rect(13,40,19,47,'G'); b.rect(21,40,27,47,'G'); b.rect(13,40,13,47,'F'); b.rect(27,40,27,47,'F')   # faldones
    b.rect(12,36,13,41,'B'); b.rect(11,35,14,35,'L'); b.px(12,42,'S')                                    # daga enfundada en el cinto
    P['torso'] = b
    for side, x0, hx in (('L', 7, 6), ('R', 29, 29)):
        a = mk(); a.rect(x0, 21, x0 + 4, 33, 'G'); a.rect(x0 if side == 'L' else x0 + 4, 21, x0 if side == 'L' else x0 + 4, 33, 'F')
        a.rect(x0, 33, x0 + 4, 34, 'w'); a.rect(hx, 35, hx + 5, 38, 'p'); a.rect(hx, 38, hx + 5, 38, 'P')
        P['arm_' + side] = a
    h = mk()
    h.rect(15,6,25,17,'p'); h.rect(16,17,24,18,'p'); h.rect(16,18,24,18,'P')
    h.pts([(13,9),(12,10),(11,10),(10,9),(27,9),(28,10),(29,10),(30,9)], 'p'); h.rect(13,9,14,12,'p'); h.rect(26,9,27,12,'p')   # orejas semielfas
    hair = {2:(17,23),3:(15,25),4:(13,27),5:(13,27),6:(13,27),7:(13,27),8:(12,28),9:(12,14),10:(12,14),11:(12,14),12:(12,14),13:(12,14),14:(13,14),15:(13,14)}
    for y, (x0, x1) in hair.items(): h.rect(x0, y, x1, y, 'h')
    for y in range(9, 16): h.rect(26, y, 28, y, 'h') if y > 9 else None
    h.rect(15,5,25,6,'h'); h.rect(15,7,25,7,'H'); h.pts([(15,8),(16,8),(24,8),(25,8),(20,7)], 'h')
    h.rect(14,6,14,8,'g'); h.rect(26,6,26,8,'g'); h.rect(12,9,12,15,'g'); h.rect(28,10,28,15,'g'); h.rect(15,4,25,4,'H'); h.rect(18,3,22,3,'H')
    h.pts([(20,10),(20,11),(20,12)], 'P')
    P['head'] = h
    def face(fn):
        f = mk(); fn(f); return f
    def eyes(f):
        for x in (17, 22): f.rect(x, 10, x + 1, 11, 'w'); f.px(x + (1 if x == 17 else 0), 10, 'e'); f.px(x + (1 if x == 17 else 0), 11, 'e')
        f.rect(17,9,18,9,'g'); f.rect(22,9,23,9,'g')
    def mouth(f): f.rect(19,15,21,15,'q')
    def n(f): eyes(f); mouth(f)
    def blink(f): f.rect(17,11,18,11,'K'); f.rect(22,11,23,11,'K'); mouth(f)
    def smile(f): eyes(f); f.rect(18,15,22,15,'q'); f.pts([(17,14),(23,14)], 'q')
    def angry(f): eyes(f); f.pts([(17,9),(18,10),(23,9),(22,10)], 'g'); f.rect(19,15,21,15,'K')
    def scared(f): eyes(f); f.rect(19,15,21,16,'K'); f.rect(17,8,18,8,'g'); f.rect(22,8,23,8,'g')
    def hurt(f): f.pts([(17,10),(18,11),(17,12),(23,10),(22,11),(23,12)], 'K'); f.rect(19,15,21,16,'K')
    def dead(f): f.pts([(17,10),(18,10),(17,12),(18,12),(23,10),(22,10),(23,12),(22,12)], 'K'); f.rect(19,15,21,15,'K')
    FACES = {k: face(v) for k, v in dict(normal=n, blink=blink, smile=smile, angry=angry, scared=scared, hurt=hurt, dead=dead).items()}
    bt = mk(); bt.rect(33,28,35,40,'b'); bt.rect(34,22,34,28,'b'); bt.rect(33,21,35,21,'B'); bt.rect(33,31,35,36,'c'); bt.px(33,29,'H')
    dg = mk(); dg.rect(31,23,32,34,'S'); dg.rect(31,23,31,34,'w'); dg.px(31,22,'w'); dg.rect(29,35,34,35,'L'); dg.rect(31,36,32,38,'B')
    gl = mk(); gl.rect(1,30,5,33,'w'); gl.rect(2,31,4,33,'c'); gl.rect(3,34,3,37,'w'); gl.rect(1,38,5,38,'w')
    layers = dict(P)
    for k, f in FACES.items(): layers[f"face_{k}"] = f
    layers["prop_R_0"] = bt; layers["prop_L_0"] = gl; layers["prop_R_1"] = dg
    rig = {"size": [40, 58], "feet": [20, 58],
        "parts": [
            {"n": "leg_L", "parent": "root",  "pivot": [16, 43]},
            {"n": "leg_R", "parent": "root",  "pivot": [23, 43]},
            {"n": "torso", "parent": "root",  "pivot": [20, 42]},
            {"n": "arm_L", "parent": "torso", "pivot": [9, 22]},
            {"n": "arm_R", "parent": "torso", "pivot": [31, 22]},
            {"n": "head",  "parent": "torso", "pivot": [20, 18]},
        ],
        "faces": list(FACES.keys()), "face_parent": "head", "props": {"0": {"L": "prop_L_0", "R": "prop_R_0"}, "1": {"R": "prop_R_1"}}, "prop_parent": {"L": "arm_L", "R": "arm_R"},
        "anchors": {"hand_R": ["arm_R", 31, 38], "hand_L": ["arm_L", 8, 38], "head_top": ["head", 20, 2]}}
    return layers, rig

if __name__ == "__main__":
    rig = {}
    for name, fn in (("kobold", kobold), ("iguana", iguana), ("kenku", kenku_small), ("dei", dei), ("hans", hans)):
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
    # kenku: figura completa + caras, ampliada
    kw, kh = rig["kenku"]["size"]; ks = Image.new("RGBA", (kw * 8 + 40, kh * 2 + 12), (26, 22, 38, 255)); kr = rig["kenku"]
    order = [p["n"] for p in kr["parts"]] + ["prop_L_0", "prop_R_0"]
    order.insert(order.index("head"), order.pop(order.index("prop_L_0"))); order.insert(order.index("head"), order.pop(order.index("prop_R_0")))
    for j, f in enumerate([None] + kr["faces"]):
        im = Image.new("RGBA", (kw, kh), (0, 0, 0, 0))
        for k in order: im.alpha_composite(Image.open(f"{OUT}/kenku/{k}.png"))
        if f: im.alpha_composite(Image.open(f"{OUT}/kenku/face_{f}.png"))
        ks.alpha_composite(im, (4 + (j % 8) * (kw + 2), 4 + (j // 8) * (kh + 2)))
    ks.resize((ks.width * 3, ks.height * 3), Image.NEAREST).save(f"{OUT}/contact_kenku.png")
    # dei + hans: figura completa + caras
    for nm in ("dei", "hans"):
        r = rig[nm]; w, h = r["size"]; sh = Image.new("RGBA", (w * 8 + 20, h * 2 + 12), (26, 22, 38, 255))
        order = [p["n"] for p in r["parts"]]
        for j, f in enumerate([None] + r["faces"]):
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            for k in order: im.alpha_composite(Image.open(f"{OUT}/{nm}/{k}.png"))
            for pn in r["props"].get("0", {}).values(): im.alpha_composite(Image.open(f"{OUT}/{nm}/{pn}.png"))
            if f: im.alpha_composite(Image.open(f"{OUT}/{nm}/face_{f}.png"))
            sh.alpha_composite(im, (4 + (j % 8) * (w + 2), 4 + (j // 8) * (h + 2)))
        sh.resize((sh.width * 3, sh.height * 3), Image.NEAREST).save(f"{OUT}/contact_{nm}.png")
