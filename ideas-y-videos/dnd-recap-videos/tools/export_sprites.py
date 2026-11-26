#!/usr/bin/env python3
"""Exporta sprites nativos (sin escalar) para el motor: iguana.png, kobold_0..6.png y meta.json. Uso: python3 tools/export_sprites.py assets/sprites/native"""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
import make_iguana_v3 as mi
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
im=mi.mr_iguana(sc=1); bb=im.getbbox(); crop=im.crop(bb); crop.save(f"{out}/iguana.png")
meta={"iguana":{"w":crop.width,"h":crop.height,"crystal":[21-bb[0],7-bb[1]]}}
KOBOLD=[
"..R.......R.......","..rR.....Rr.......","...rrrrrrr........","..rrrrrrrrrr......",".rrKyrrrrKyrr.....",
".rrrrrrrrrrrrrr...",".rrrrwwwwwrrrrrr..","..rrrrrrrrrrr.....","...rroorrrr.......","..rrrooorrrrr.....",
".rrrrooorrrrrr....",".rrrrooorrrrrrr...","..rrrrrrrrrrrr....","...rr.rrrr.rr.....","...rr.....rr......","..RRR.....RRR.....",
]
COLS=[((214,96,58),(150,56,40)),((168,86,46),(110,50,34)),((190,80,120),(130,44,80)),
      ((90,150,110),(60,100,76)),((200,170,70),(140,116,40)),((120,110,190),(80,72,140)),((160,160,170),(110,110,120))]
for n,(r,R) in enumerate(COLS):
    pal={'r':r,'R':R,'o':(240,170,90),'w':(245,245,245),'K':(15,15,25),'y':(250,220,70)}
    k=Image.new("RGBA",(18,16),(0,0,0,0))
    for y,row in enumerate(KOBOLD):
        for x,ch in enumerate(row):
            if ch in pal: k.putpixel((x,y),pal[ch]+(255,))
    k.save(f"{out}/kobold_{n}.png")
meta["kobold"]={"w":18,"h":16}
json.dump(meta,open(f"{out}/meta.json","w"))
print(meta)
