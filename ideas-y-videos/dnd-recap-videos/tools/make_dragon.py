#!/usr/bin/env python3
"""Dragón de cobre adulto (5e), perfil mirando a la IZQUIERDA, celda 248x128.
Se dibuja con primitivas (polígonos/curvas) y un pase de sombreado pixel art por material:
luz desde arriba, contorno oscuro, textura de escamas. Devuelve capas + definición de rig para make_rig.py.
Uso suelto: python3 tools/make_dragon.py [out_dir]  (genera PNG + hoja de contacto)"""
import sys, os, json, math
from PIL import Image, ImageDraw

W, H = 248, 128
def T(base, light, hl, dark, line, outline=True, scales=True): return dict(base=base, light=light, hl=hl, dark=dark, line=line, outline=outline, scales=scales)
def dim(t, f):
    c = lambda x: tuple(int(v * f) for v in x)
    return T(c(t['base']), c(t['light']), c(t['hl']), c(t['dark']), c(t['line']), t['outline'], t['scales'])
CU    = T((190,108,46), (226,146,68), (250,190,110), (136,74,34), (74,38,26))
BELLY = T((222,176,102), (240,204,132), (252,226,170), (176,130,70), (120,84,46), outline=False)
MEMB  = T((70,138,114), (108,174,144), (150,206,176), (42,96,80), (28,62,54), scales=False)
BONE  = T((198,116,52), (232,156,78), (252,196,118), (140,78,36), (74,38,26), scales=False)
HORN  = T((232,208,150), (248,232,186), (255,246,214), (186,154,98), (96,72,44), scales=False)
TEETH = T((244,240,224), (255,255,244), (255,255,255), (200,196,180), (110,100,90), scales=False)
MOUTH = T((150,44,52), (180,70,70), (200,90,90), (104,28,38), (60,16,24), outline=False, scales=False)
CLAW  = T((64,48,40), (96,74,60), (130,104,84), (40,30,26), (20,14,12), scales=False)

def canvas(): return Image.new("L", (W, H), 0)
def curve(d, pts, ws, n=48):
    """Catmull-Rom por pts con grosor interpolado ws; círculos a lo largo del trazo."""
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for s in range(n):
            t = s / n
            x = .5 * (2*p1[0] + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t*t + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t**3)
            y = .5 * (2*p1[1] + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t*t + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t**3)
            k = (i - 1 + t) / (len(P) - 3)
            wi = ws[0] + (ws[-1] - ws[0]) * k if len(ws) == 2 else ws[min(int(k * (len(ws) - 1)), len(ws) - 2)] + (ws[min(int(k * (len(ws) - 1)) + 1, len(ws) - 1)] - ws[min(int(k * (len(ws) - 1)), len(ws) - 2)]) * ((k * (len(ws) - 1)) % 1)
            r = wi / 2
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)

def shade(mask, tone, light_from_top=True):
    """Mask L → imagen RGBA sombreada según 'tone'."""
    w, h = mask.size; px = mask.load(); out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); o = out.load()
    on = lambda x, y: 0 <= x < w and 0 <= y < h and px[x, y] > 127
    def run(x, y, dx, dy, cap=5):
        n = 0
        while n < cap and on(x + dx * (n + 1), y + dy * (n + 1)): n += 1
        return n
    for y in range(h):
        for x in range(w):
            if not on(x, y): continue
            up, dn, lf, rt = run(x, y, 0, -1), run(x, y, 0, 1), run(x, y, -1, 0), run(x, y, 1, 0)
            c = tone['base']
            if tone['scales'] and up >= 2 and dn >= 2:
                sh = (x + 2 * ((y // 3) % 2)) % 4
                if y % 3 == 1 and sh == 0: c = tone['dark']
                elif y % 3 == 0 and sh == 2: c = tone['light']
            if up == 1: c = tone['hl']
            elif up == 2: c = tone['light']
            if dn == 1: c = tone['dark']
            elif dn == 2 and tone['scales']: c = tone['dark'] if (x + y) % 2 else tone['base']
            if lf == 0 and rt == 0 or (tone['outline'] and (up == 0 or dn == 0 or lf == 0 or rt == 0)):
                if tone['outline']: c = tone['line']
            o[x, y] = c + (255,)
    return out

def compose(layers):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for l in layers: im.alpha_composite(l)
    return im

def build(draws):
    """draws: [(fn(d), tone)] en orden → RGBA."""
    out = []
    for fn, tone in draws:
        m = canvas(); fn(ImageDraw.Draw(m)); out.append(shade(m, tone))
    return compose(out)

def tri(d, a, b, c): d.polygon([a, b, c], fill=255)

# ───────────── partes ─────────────
def part_body(f=1.0, dx=0, dy=0):
    def torso(d):
        d.ellipse([74, 60, 168, 96], fill=255)
        d.ellipse([78, 58, 114, 98], fill=255)                                                    # pecho
        curve(d, [(150, 66), (162, 74), (170, 82)], [22, 18, 12])                                 # grupa → cola
        for x in range(84, 162, 8): tri(d, (x, 62), (x+4, 54 + (x//8) % 2 * 2), (x+8, 62))        # espinas dorsales
    def belly(d):
        d.chord([80, 68, 162, 102], 0, 180, fill=255)
        d.rectangle([80, 68, 162, 84], fill=0)
    return build([(torso, dim(CU, f)), (belly, dim(BELLY, f))])

def tail_seg(a, b, wa, wb, f=1.0, spade=False):
    def fn(d):
        curve(d, [a, ((a[0]+b[0])/2, (a[1]+b[1])/2 + 2), b], [wa, wb])
        if spade:
            tri(d, (b[0]-1, b[1]-8), (b[0]+9, b[1]), (b[0]-1, b[1]+8))
    return build([(fn, dim(CU, f))])

def part_neck(f=1.0):
    def fn(d):
        curve(d, [(106, 72), (88, 64), (72, 54), (58, 47), (50, 44)], [20, 11])
        for (x, y) in [(94, 60), (82, 54), (70, 48), (60, 43), (53, 40)]: tri(d, (x, y), (x+3, y-7), (x+7, y-1))
    def bl(d):
        curve(d, [(104, 78), (88, 70), (72, 60), (58, 53), (50, 49)], [9, 5])
    return build([(fn, dim(CU, f)), (bl, dim(BELLY, f))])

def part_head(f=1.0):
    def skull(d):
        d.polygon([(54, 36), (46, 29), (34, 30), (21, 36), (9, 43), (3, 48), (5, 52), (16, 51), (30, 51), (42, 52), (54, 50)], fill=255)
        for (a, b, c) in [((44, 50), (52, 62), (54, 49)), ((38, 51), (42, 64), (46, 50)), ((32, 51), (33, 62), (38, 50))]: tri(d, a, b, c)   # gola
        tri(d, (30, 31), (34, 22), (38, 30)); tri(d, (20, 35), (22, 28), (26, 33))    # cresta/ceja
    def horn(d):
        curve(d, [(46, 33), (56, 26), (66, 21), (74, 22)], [7, 5, 2])
        curve(d, [(47, 40), (58, 38), (68, 40), (74, 46)], [6, 4, 2])
    def teeth(d):
        for x in range(8, 40, 5): tri(d, (x, 51), (x+2, 56), (x+4, 51))
    def nose(d): d.rectangle([7, 45, 9, 46], fill=255)
    return build([(horn, dim(HORN, f)), (skull, dim(CU, f)), (teeth, dim(TEETH, f)), (nose, dim(CLAW, f))])

def part_jaw(f=1.0):
    def jaw(d):
        d.polygon([(5, 52), (17, 52), (32, 52), (44, 54), (46, 61), (34, 63), (20, 61), (9, 58), (4, 55)], fill=255)
    def mouth(d):
        d.polygon([(8, 52), (40, 52), (40, 56), (12, 56)], fill=255)
    def teeth(d):
        for x in range(8, 38, 5): tri(d, (x, 56), (x+2, 51), (x+4, 56))
    return build([(jaw, dim(CU, f)), (mouth, dim(MOUTH, f)), (teeth, dim(TEETH, f))])

def leg(shoulder, pts, ws, foot, f=1.0, r=13):
    def fn(d):
        d.ellipse([shoulder[0]-r, shoulder[1]-r, shoulder[0]+r, shoulder[1]+r+2], fill=255)
        curve(d, pts, ws)
        d.polygon(foot, fill=255)
    def cl(d):
        x0 = min(p[0] for p in foot); y = max(p[1] for p in foot)
        for i in range(3): tri(d, (x0 + i*5 + 2, y - 3), (x0 + i*5 - 2, y + 1), (x0 + i*5 + 4, y))
    return build([(fn, dim(CU, f)), (cl, dim(CLAW, f))])

def wing(f=1.0, dx=0, dy=0, sc=1.0):
    S, E, Wr = (88+dx, 60+dy), (100+dx, 32+dy), (132+dx, 12+dy)
    tips = [(192+dx, 22+dy), (178+dx, 52+dy), (150+dx, 64+dy)]
    def memb(d):
        d.polygon([S, E, Wr, tips[0], (176+dx, 32+dy), tips[1], (162+dx, 50+dy), tips[2], (138+dx, 60+dy), (124+dx, 68+dy), (108+dx, 66+dy)], fill=255)
    def bones(d):
        curve(d, [S, (94+dx, 46+dy), E], [5, 4]); curve(d, [E, (116+dx, 22+dy), Wr], [4, 3])
        for t in tips + [(124+dx, 68+dy)]:
            curve(d, [Wr, ((Wr[0]+t[0])/2, (Wr[1]+t[1])/2 - 1), t], [3, 1])
        tri(d, (Wr[0]-3, Wr[1]), (Wr[0]+3, Wr[1]-9), (Wr[0]+5, Wr[1]+1))
    return build([(memb, dim(MEMB, f)), (bones, dim(BONE, f))])

# ───────────── caras ─────────────
EYE = (255, 208, 60); EYE_L = (255, 240, 150); DARK = (30, 14, 10); BROW = (90, 46, 26)
def face(kind):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ex, ey = 25, 37
    if kind == 'normal':
        d.ellipse([ex-4, ey-3, ex+3, ey+2], fill=EYE); d.line([ex, ey-3, ex, ey+2], fill=DARK); d.point((ex-3, ey-2), fill=EYE_L); d.line([ex-6, ey-5, ex+5, ey-4], fill=BROW, width=1)
    elif kind == 'blink':
        d.line([ex-4, ey, ex+3, ey], fill=DARK, width=1); d.line([ex-6, ey-3, ex+5, ey-2], fill=BROW)
    elif kind == 'angry':
        d.ellipse([ex-4, ey-2, ex+3, ey+2], fill=EYE); d.line([ex, ey-2, ex, ey+2], fill=DARK); d.polygon([(ex-7, ey-6), (ex+5, ey-1), (ex+5, ey-3), (ex-7, ey-8)], fill=DARK)
    elif kind == 'roar':
        d.ellipse([ex-4, ey-4, ex+4, ey+3], fill=(255, 150, 40)); d.line([ex, ey-4, ex, ey+3], fill=DARK); d.line([ex-6, ey-7, ex+5, ey-3], fill=DARK, width=2)
    elif kind == 'hurt':
        d.line([ex-4, ey-3, ex+2, ey], fill=DARK, width=2); d.line([ex+2, ey, ex-4, ey+3], fill=DARK, width=2)
    elif kind == 'dead':
        for a, b in (((ex-4, ey-3), (ex+3, ey+3)), ((ex+3, ey-3), (ex-4, ey+3))): d.line([a, b], fill=DARK, width=2)
    return im
FACES = ['normal', 'blink', 'angry', 'roar', 'hurt', 'dead']

def dragon():
    L = {}
    L['wing_far'] = wing(0.62, 38, -4)
    L['leg_far_F'] = leg((106, 88), [(108, 86), (110, 100), (105, 113), (103, 121)], [10, 8, 6, 5], [(92, 126), (108, 126), (108, 121), (96, 121)], 0.62, r=8)
    L['leg_far_H'] = leg((156, 90), [(158, 88), (162, 104), (151, 114), (147, 121)], [13, 10, 7, 6], [(134, 126), (152, 126), (152, 121), (139, 121)], 0.62, r=10)
    L['tail1'] = tail_seg((160, 76), (190, 86), 15, 11)
    L['tail2'] = tail_seg((188, 86), (218, 94), 11, 7)
    L['tail3'] = tail_seg((216, 94), (246, 86), 7, 2, spade=True)
    L['body'] = part_body()
    L['neck'] = part_neck()
    L['jaw'] = part_jaw()
    L['head'] = part_head()
    L['leg_near_H'] = leg((148, 90), [(150, 86), (154, 102), (143, 114), (139, 121)], [14, 10, 7, 6], [(126, 126), (144, 126), (144, 121), (131, 121)], r=11)
    L['leg_near_F'] = leg((98, 86), [(100, 84), (102, 100), (97, 113), (95, 121)], [11, 8, 6, 5], [(84, 126), (100, 126), (100, 121), (88, 121)], r=9)
    L['wing_near'] = wing(1.0, 22, 2)
    for k in FACES: L[f'face_{k}'] = face(k)
    rig = {
        "size": [W, H], "feet": [124, H],
        "parts": [
            {"n": "wing_far",   "parent": "body",  "pivot": [126, 56]},
            {"n": "leg_far_F",  "parent": "root",  "pivot": [106, 88]},
            {"n": "leg_far_H",  "parent": "root",  "pivot": [156, 90]},
            {"n": "tail1",      "parent": "body",  "pivot": [160, 76]},
            {"n": "tail2",      "parent": "tail1", "pivot": [188, 86]},
            {"n": "tail3",      "parent": "tail2", "pivot": [216, 94]},
            {"n": "body",       "parent": "root",  "pivot": [122, 90]},
            {"n": "neck",       "parent": "body",  "pivot": [104, 72]},
            {"n": "jaw",        "parent": "head",  "pivot": [42, 53]},
            {"n": "head",       "parent": "neck",  "pivot": [48, 44]},
            {"n": "leg_near_H", "parent": "root",  "pivot": [148, 90]},
            {"n": "leg_near_F", "parent": "root",  "pivot": [98, 86]},
            {"n": "wing_near",  "parent": "body",  "pivot": [110, 62]},
        ],
        "faces": FACES, "face_parent": "head", "props": {}, "prop_parent": {},
        "anchors": {"mouth": ["head", 5, 52], "eye": ["head", 25, 37], "chest": ["body", 92, 78], "wing_tip": ["wing_near", 214, 24], "tail_tip": ["tail3", 244, 88], "head_top": ["head", 40, 28]},
    }
    return L, rig

class ImgLayer:
    def __init__(self, im): self.im = im
    def save(self, path): self.im.save(path)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets/rig/dragon"; os.makedirs(out, exist_ok=True)
    L, rig = dragon()
    for k, im in L.items(): im.save(f"{out}/{k}.png")
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for p in rig["parts"]: base.alpha_composite(L[p["n"]])
    sheet = Image.new("RGBA", (W * 3 + 16, H + 8), (150, 190, 230, 255))
    for i, f in enumerate(['normal', 'angry', 'roar']):
        im = base.copy(); im.alpha_composite(L[f'face_{f}']); sheet.alpha_composite(im, (4 + i * (W + 4), 4))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(f"{out}/../contact_dragon.png")
    print(len(L), "capas ->", out)
