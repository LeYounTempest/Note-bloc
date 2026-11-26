#!/usr/bin/env python3
"""Genera sprites 8-bit de Mr. Iguana y kobolds (boceto). Uso: python3 tools/make_sprites.py out_dir"""
import sys
from PIL import Image
P = {'.':None,'H':(54,92,200),'h':(30,52,130),'g':(110,190,90),'G':(62,130,66),'y':(250,220,70),'K':(15,15,25),
     'c':(60,110,220),'C':(34,70,150),'s':(130,86,48),'l':(120,230,130),'b':(140,60,150),'B':(220,200,120),'w':(245,245,245),
     'r':(214,96,58),'R':(150,56,40),'o':(240,170,90),'t':(250,250,230),'m':(210,70,70)}
W,H=18,24
IGUANA=[
"........hh........",
".......hHHh.......",
"......hHHHHh......",
".....hHHHHHHh.....",
"....hHHHHHHHHh....",
"..hhhhhhhhhhhhhh..",
"....gggggggggg....",
"...ggyKgggyKgggg..",
"...gggggggggggggg.",
"....GggggggGGGGg..",
".....GGgggGG......",
"...ccccgggcccc..l.",
"..cccccgggccccbllls",
"..ccccccgcccbbBls.",
".cccCcccccccbbBBs.",
".ccCCcgggcccbbBBs.",
".cCCCcgGgcccccgGs.",
".cCCCccgGgcccgggs.",
"..CCCcccggcc..GGs.",
"..CCCcccGGGc...s..",
"...CCc.gg.gg...s..",
"....G..GG.GG...s..",
"...GGG.GGG.GGG.s..",
"..................",
]
IGUANA_B=IGUANA[:]
IGUANA_B[0:5]=[ "........hh........", ".......hHHh.......", "......hHHHHh......", ".....hHHHHHHh.....","....hHHHHHHHHh...." ]
KOBOLD=[
"..R.......R.......",
"..rR.....Rr.......",
"...rrrrrrr........",
"..rrrrrrrrrr......",
".rrKyrrrrKyrr.....",
".rrrrrrrrrrrrrr...",
".rrrrwwwwwrrrrrr..",
"..rrrrrrrrrrr.....",
"...rroorrrr.......",
"..rrrooorrrrr.....",
".rrrrooorrrrrr....",
".rrrrooorrrrrrr...",
"..rrrrrrrrrrrr....",
"...rr.rrrr.rr.....",
"...rr.....rr......",
"..RRR.....RRR.....",
]
def tint(c,k): return tuple(max(0,min(255,int(x*k))) for x in c)
def render(grid,pal,flip=False):
    w=max(len(r) for r in grid); im=Image.new("RGBA",(w,len(grid)),(0,0,0,0))
    for y,row in enumerate(grid):
        for x,ch in enumerate(row):
            c=pal.get(ch)
            if c: im.putpixel((w-1-x if flip else x,y),c+(255,))
    return im
out=sys.argv[1]; S=14
RED=dict(P); RED['g']=(214,64,56); RED['G']=(140,36,40); RED['y']=(250,220,70)
def canvas(w,h): return Image.new("RGBA",(w,h),(0,0,0,0))
def put(im,x,y,c):
    if 0<=x<im.width and 0<=y<im.height: im.putpixel((x,y),c+(255,))
def iguana_full(wings=False,fire=False,ox=8):
    im=canvas(36,24)
    base=render(IGUANA,RED); im.alpha_composite(base,(ox,0))
    if wings:
        WC=(170,40,48); WD=(110,26,36)
        # ala izquierda y derecha (dragon), simples
        for k in range(8):
            for j in range(k//2+2):
                put(im,ox+1-k,6+j+k//2-4+ (0 if k<4 else k-4),WC)
        for k in range(9):
            for j in range(5):
                put(im,ox+16+k,4+j+(k//3),WC if (j+k)%3 else WD)
        for k in range(9):
            for j in range(5):
                put(im,ox+1-k,4+j+(k//3),WC if (j+k)%3 else WD)
    if fire:
        cols=[(255,240,150),(250,180,60),(235,100,40),(190,50,40)]
        for k in range(12):
            for j in range(-(k//3),(k//3)+2):
                put(im,ox+17+k,8+j,cols[min(3,k//3)])
    return im
sheet=Image.new("RGBA",(S*36*3+60,S*24+20),(26,22,38,255))
x=10
for kw in (dict(),dict(wings=True),dict(wings=True,fire=True)):
    im=iguana_full(**kw).resize((36*S,24*S),Image.NEAREST); sheet.paste(im,(x,10),im); x+=36*S+10
sheet.save(out+"/mr_iguana_rojo.png")
