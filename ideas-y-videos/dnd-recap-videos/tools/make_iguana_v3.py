#!/usr/bin/env python3
"""Mr. Iguana v3: cuerpo ancho tipo dragón barbudo, barba de espinas, vientre crema, capa abierta, libro al pecho, bastón con cristal.
Diseño propio a partir de la descripción del autor (colores editables en PAL). Uso: python3 tools/make_iguana_v3.py out_dir"""
import sys
from PIL import Image, ImageDraw
PAL=dict(g=(226,84,48),G=(160,50,40),e=(246,206,150),E=(222,170,112),u=(150,60,190),i=(250,240,255),K=(18,12,22),
 H=(70,84,160),h=(42,52,112),c=(84,100,170),C=(52,64,124),s=(120,52,50),S=(80,34,36),m=(230,70,200),M=(150,30,140),
 b=(130,70,170),B=(214,200,236),o=(250,150,40),W=(196,60,56),w=(120,30,40),f1=(255,244,160),f2=(252,190,60),f3=(236,106,40),f4=(190,52,40))
class Cv:
    def __init__(s,w=64,h=46): s.w,s.h,s.p=w,h,{}
    def px(s,x,y,k):
        if 0<=x<s.w and 0<=y<s.h: s.p[(x,y)]=k
    def rect(s,x0,y0,x1,y1,k):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): s.px(x,y,k)
    def poly(s,pts,k):
        m=Image.new("L",(s.w,s.h),0); ImageDraw.Draw(m).polygon(pts,fill=255)
        for y in range(s.h):
            for x in range(s.w):
                if m.getpixel((x,y)): s.px(x,y,k)
    def line(s,a,b,k):
        n=max(abs(b[0]-a[0]),abs(b[1]-a[1]),1)
        for i in range(n+1): s.px(round(a[0]+(b[0]-a[0])*i/n),round(a[1]+(b[1]-a[1])*i/n),k)
    def img(s,sc=10):
        im=Image.new("RGBA",(s.w,s.h),(0,0,0,0))
        for (x,y),k in s.p.items(): im.putpixel((x,y),PAL[k]+(255,))
        return im.resize((s.w*sc,s.h*sc),Image.NEAREST)

def mr_iguana(wings=0,fire=0,t=0,ox=16,sc=10):
    c=Cv(); X=lambda x:x+ox
    if wings:
        up=wings==2
        L=[(14,22),(3,10),(1,2),(6,6),(8,0),(12,8),(15,5),(18,22)] if up else [(14,22),(6,16),(5,10),(8,12),(10,8),(13,14),(16,12),(18,22)]
        c.poly([(X(x-8),y) for x,y in L],'W')
        for p in ([(2,22),(1,2)] if up else []) : pass
        for tip in ([(3,2),(8,0),(15,5)] if up else [(5,10),(10,8),(16,12)]): c.line((X(14-8),22),(X(tip[0]-8),tip[1]),'w')
        if up:
            R=[(30,22),(41,10),(43,2),(38,6),(36,0),(32,8),(29,5),(26,22)]
            c.poly([(X(x),y) for x,y in R],'W')
            for tip in [(41,2),(36,0),(29,5)]: c.line((X(30),22),(X(tip[0]),tip[1]),'w')
    # cola
    for i,(x,y) in enumerate([(30,40),(32,41),(34,41),(36,40),(38,38),(39,36),(39,34)]):
        c.rect(X(x),y,X(x+1),y+2,'g' if i%2==0 else 'G')
    # bastón
    c.rect(X(5),8,X(6),44,'s'); c.rect(X(6),8,X(6),44,'S')
    c.poly([(X(2),7),(X(5),2),(X(9),7),(X(5),11)],'m'); c.line((X(5),3),(X(5),10),'M'); c.px(X(4),5,'i')
    # sombrero (cono con punta curva)
    c.poly([(X(12),13),(X(20),3),(X(24),2),(X(28),3),(X(27),5),(X(24),6),(X(28),13)],'H')
    c.poly([(X(24),6),(X(28),3),(X(31),4),(X(30),6),(X(27),7)],'h')
    c.poly([(X(8),13),(X(32),13),(X(34),15),(X(6),15)],'h'); c.rect(X(8),13,X(32),13,'H')
    # cabeza
    c.poly([(X(10),16),(X(14),14),(X(26),14),(X(30),16),(X(31),22),(X(26),26),(X(14),26),(X(9),22)],'g')
    c.poly([(X(11),21),(X(29),21),(X(27),26),(X(13),26)],'e')            # mandíbula crema
    c.rect(X(12),21,X(28),21,'G')                                         # boca
    for i,(x,y) in enumerate([(31,17),(32,19),(32,21),(31,23),(30,25)]): c.px(X(x),y,'e'); c.px(X(x+1),y,'e')  # barba
    for i,(x,y) in enumerate([(9,18),(8,20),(8,22),(9,24)]): c.px(X(x),y,'e')
    c.rect(X(14),16,X(17),19,'i'); c.rect(X(15),17,X(16),19,'u'); c.px(X(15),17,'i'); c.px(X(16),18,'K')   # ojo grande
    c.rect(X(23),17,X(25),19,'i'); c.rect(X(24),17,X(25),19,'u'); c.px(X(24),18,'K')
    c.px(X(18),20,'G'); c.px(X(22),20,'G')
    # capa abierta con vientre crema
    for r in range(26,43):
        l=9-(r-26)//3; rr=31+(r-26)//3
        c.rect(X(l),r,X(rr),r,'c'); c.rect(X(l),r,X(l+4),r,'C')
    c.rect(X(15),27,X(25),41,'e'); 
    for r in range(28,41,3): c.px(X(18),r,'E'); c.px(X(22),r+1,'E')
    c.rect(X(15),26,X(25),26,'e'); c.rect(X(19),27,X(21),28,'o')       # broche
    # brazos
    c.rect(X(8),28,X(14),31,'g'); c.rect(X(5),29,X(8),32,'g')           # mano en el bastón
    c.rect(X(24),30,X(31),33,'g')                                       # brazo derecho
    c.rect(X(22),29,X(30),38,'b'); c.rect(X(23),30,X(29),37,'B'); c.rect(X(22),29,X(22),38,'M')
    for r in (32,34,36): c.rect(X(24),r,X(28),r,'b')
    c.rect(X(20),34,X(25),37,'g')                                       # mano sobre libro
    # patas
    c.rect(X(10),41,X(16),43,'g'); c.rect(X(24),41,X(30),43,'g')
    for x in (10,12,14,24,26,28): c.px(X(x),44,'K')
    if fire:
        cols=['f1','f2','f3','f4']
        for k in range(20):
            sp=int(k*0.5+(t%2)); wob=1 if (k+t)%2 else 0
            for j in range(-sp,sp+1):
                if abs(j)==sp and k>5 and (j+k+t)%2: continue
                c.px(X(33+k),21+j-wob,cols[min(3,k*4//20)])
    return c.img(sc)

if __name__=='__main__':
  out=sys.argv[1]
  ims=[mr_iguana(), mr_iguana(fire=1)]
  sheet=Image.new("RGBA",(sum(i.width for i in ims)+40,ims[0].height+20),(26,22,38,255))
  x=10
  for im in ims: sheet.paste(im,(x,10),im); x+=im.width+10
  sheet.save(out+"/mr_iguana_v3.png")
