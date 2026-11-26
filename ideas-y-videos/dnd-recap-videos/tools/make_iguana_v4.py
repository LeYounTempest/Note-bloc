#!/usr/bin/env python3
"""Mr. Iguana v4 (28x30 px nativos, mas pequeño que un kobold): ojos grandes con iris morado, barba de espinas,
vientre crema, capa azul abierta, sombrero con punta curva, libro al pecho, bastón con cristal magenta.
Uso: python3 tools/make_iguana_v4.py out_dir [scale]"""
import sys, json, os
from PIL import Image, ImageDraw
PAL=dict(g=(226,84,48),G=(160,50,40),e=(246,206,150),E=(222,170,112),u=(150,60,200),i=(255,255,255),K=(18,12,22),
 H=(70,84,168),h=(42,52,116),c=(84,104,178),C=(52,66,128),s=(122,66,52),S=(82,40,40),m=(236,74,208),M=(150,30,140),
 b=(132,72,176),B=(220,208,238),o=(250,150,40),p=(250,190,120))
W_,H_=28,30
def build():
    p={}
    def px(x,y,k):
        if 0<=x<W_ and 0<=y<H_: p[(x,y)]=k
    def rect(x0,y0,x1,y1,k):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): px(x,y,k)
    # bastón + cristal
    rect(2,5,2,29,'s'); rect(3,7,3,29,'S')
    for (x,y) in [(2,0),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(4,2),(1,3),(2,3),(3,3),(2,4)]: px(x,y,'m')
    px(2,1,'i'); px(1,2,'M'); px(3,3,'M')
    # sombrero (punta curva a la derecha)
    rows={4:(16,18),5:(14,17),6:(12,16),7:(11,16),8:(10,17),9:(9,18)}
    for y,(a,b) in rows.items(): rect(a,y,b,y,'H')
    px(19,4,'h'); px(19,3,'h'); px(18,3,'h')   # curl
    for y,(a,b) in rows.items(): px(b,y,'h')
    rect(6,10,22,10,'h'); rect(7,10,21,10,'H'); rect(6,11,22,11,'h')
    # cabeza (ancha) y mandíbula
    rect(8,11,20,17,'g'); rect(7,13,8,16,'g'); rect(10,16,18,17,'e')
    rect(10,15,18,15,'G')
    rect(11,18,15,18,'g')                                   # boca
    # ojos grandes
    rect(10,12,12,14,'i'); rect(11,12,12,14,'u'); px(11,13,'K'); px(10,12,'i')
    rect(16,12,18,14,'i'); rect(17,12,18,14,'u'); px(17,13,'K'); px(16,12,'i')
    # barba de espinas
    for (x,y) in [(21,13),(22,14),(21,15),(22,16),(21,17)]: px(x,y,'p')
    for (x,y) in [(6,14),(5,15),(6,16),(5,17)]: px(x,y,'p')
    # capa abierta + vientre
    for r in range(19,28):
        l=6-(r-19)//5; rr=21+(r-19)//5
        rect(l,r,rr,r,'c'); rect(l,r,l+2,r,'C')
    rect(10,19,16,26,'e'); px(13,20,'o'); px(13,21,'o')
    for r in (22,24): px(11,r,'E'); px(15,r+1,'E')
    # brazos, libro
    rect(4,20,7,21,'g'); px(3,20,'g'); px(3,21,'g')           # mano en el bastón
    rect(17,20,23,26,'b'); rect(18,21,22,25,'B'); rect(17,20,17,26,'M')
    for r in (22,24): rect(18,r,21,r,'b')
    rect(14,23,17,24,'g')                                     # mano sobre el libro
    # patas + garras
    rect(8,27,11,28,'g'); rect(16,27,19,28,'g')
    for x in (8,10,16,18): px(x,29,'K')
    # cola
    for i,(x,y) in enumerate([(22,27),(23,28),(24,28),(25,27),(26,26),(26,24)]): px(x,y,'g' if i%2==0 else 'G'); px(x,y+1,'g' if i%2==0 else 'G')
    return p
def render(sc=1):
    im=Image.new("RGBA",(W_,H_),(0,0,0,0))
    for (x,y),k in build().items(): im.putpixel((x,y),PAL[k]+(255,))
    return im.resize((W_*sc,H_*sc),Image.NEAREST) if sc>1 else im
if __name__=="__main__":
    out=sys.argv[1]; sc=int(sys.argv[2]) if len(sys.argv)>2 else 1
    os.makedirs(out,exist_ok=True)
    render(sc).save(f"{out}/iguana.png")
    if sc==1:
        # referencia: kobold 2x
        kob=Image.open(f"{out}/kobold_0.png").resize((36,32),Image.NEAREST) if os.path.exists(f"{out}/kobold_0.png") else None
        sheet=Image.new("RGBA",(120,40),(26,22,38,255)); sheet.alpha_composite(render(1),(4,5))
        if kob: sheet.alpha_composite(kob,(50,4))
        sheet.resize((480,160),Image.NEAREST).save("/tmp/cmp_v4.png")
