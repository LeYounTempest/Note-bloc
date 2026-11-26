#!/usr/bin/env python3
"""Mr. Iguana v2 (perfil de iguana: hocico largo, papada, cresta dorsal, cola anillada). Uso: python3 tools/make_iguana.py out_dir"""
import sys
from PIL import Image
PAL=dict(g=(214,64,56),G=(140,36,40),p=(244,150,70),d=(246,130,100),y=(250,225,80),K=(15,12,20),
 H=(54,92,200),h=(28,48,125),c=(60,110,220),C=(32,66,150),s=(128,84,46),l=(120,230,130),L=(60,160,80),
 b=(140,60,150),B=(226,206,130),W=(178,44,56),w=(112,26,40),f1=(255,244,160),f2=(252,190,60),f3=(236,106,40),f4=(190,52,40),t=(250,250,240))
class Cv:
    def __init__(s,w=56,h=30): s.w,s.h,s.p=w,h,{}
    def px(s,x,y,k):
        if 0<=x<s.w and 0<=y<s.h: s.p[(x,y)]=k
    def rect(s,x0,y0,x1,y1,k):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): s.px(x,y,k)
    def img(s,scale=12):
        im=Image.new("RGBA",(s.w,s.h),(0,0,0,0))
        for (x,y),k in s.p.items(): im.putpixel((x,y),PAL[k]+(255,))
        return im.resize((s.w*scale,s.h*scale),Image.NEAREST)

def iguana(wings=0,fire=0,t=0,ox=8):
    c=Cv(); X=lambda x:x+ox
    # alas (detras)
    if wings:
        from PIL import ImageDraw
        m=Image.new("L",(c.w,c.h),0); d=ImageDraw.Draw(m)
        if wings==2: poly=[(9,13),(0,6),(0,1),(4,3),(5,-1),(8,4),(11,1),(11,11)]; bones=[((9,13),(0,2)),((9,13),(5,0)),((9,13),(11,2))]
        else: poly=[(9,13),(3,9),(2,5),(5,6),(6,3),(8,7),(10,5),(11,11)]; bones=[((9,13),(2,5)),((9,13),(6,3)),((9,13),(10,5))]
        d.polygon([(X(px_),py_) for px_,py_ in poly],fill=255)
        for (x,y) in [(xx,yy) for yy in range(c.h) for xx in range(c.w) if m.getpixel((xx,yy))]: c.px(x,y,'W')
        for (p0,p1) in bones:
            n=max(abs(p1[0]-p0[0]),abs(p1[1]-p0[1]),1)
            for i in range(n+1): c.px(X(round(p0[0]+(p1[0]-p0[0])*i/n)),round(p0[1]+(p1[1]-p0[1])*i/n),'w')
    # cola anillada (curva al fondo)
    tail=[(8,22),(7,23),(6,24),(5,25),(4,25),(3,26),(2,26),(1,25),(0,24),(0,23)]
    for i,(x,y) in enumerate(tail):
        k='g' if i%2==0 else 'G'; c.px(X(x),y,k); c.px(X(x),y+1,k)
    # cresta dorsal
    for (x,y) in [(6,6),(5,8),(5,10),(5,12),(5,14),(5,16)]: c.px(X(x),y,'p')
    # sombrero
    for r,wd in enumerate([2,4,6,8,10]): c.rect(X(12-wd//2),r,X(12+wd//2-1),r,'H'); c.px(X(12+wd//2-1),r,'h')
    c.rect(X(5),5,X(20),5,'h')
    # cabeza + hocico largo
    c.rect(X(8),6,X(16),9,'g'); c.rect(X(17),7,X(23),9,'g'); c.rect(X(17),9,X(23),9,'G')
    c.px(X(22),7,'K'); c.px(X(8),6,'G')
    c.px(X(13),7,'y'); c.px(X(14),7,'K'); c.px(X(13),8,'G'); c.px(X(14),8,'G')
    # papada naranja
    c.rect(X(11),10,X(16),11,'d'); c.rect(X(12),12,X(15),12,'d'); c.rect(X(13),13,X(14),13,'d')
    # cuello y capa
    c.rect(X(9),10,X(10),12,'g')
    for r in range(11,21):
        L=7-(r-11)//4; R=17+(r-11)//4
        c.rect(X(L),r,X(R),r,'c'); c.rect(X(L),r,X(L+3),r,'C')
    c.rect(X(11),11,X(16),11,'c'); c.px(X(13),12,'y')  # broche
    # bastón druida (der) con hojas
    c.rect(X(25),9,X(25),28,'s'); c.px(X(24),10,'s'); c.px(X(26),12,'s')
    for (x,y) in [(24,5),(25,4),(26,5),(23,6),(25,6),(27,6),(24,7),(26,7),(25,8)]: c.px(X(x),y,'l' if (x+y)%2 else 'L')
    c.px(X(25),6,'t')
    # brazos
    c.rect(X(19),15,X(24),16,'g'); c.px(X(25),15,'g'); c.px(X(25),16,'g')
    c.rect(X(5),16,X(7),17,'g')
    # libro (izq)
    c.rect(X(1),14,X(5),19,'b'); c.rect(X(2),15,X(5),18,'B'); c.rect(X(1),14,X(1),19,'b')
    # patas
    c.rect(X(9),21,X(11),26,'g'); c.rect(X(14),21,X(16),26,'g')
    c.rect(X(8),27,X(12),27,'G'); c.rect(X(13),27,X(17),27,'G')
    # fuego
    if fire:
        cols=['f1','f2','f3','f4']
        import math
        for k in range(16):
            sp=int(k*0.55+ (t%2)); wob=1 if (k+t)%2 else 0
            for j in range(-sp,sp+1):
                if abs(j)==sp and k>4 and (j+k+t)%2: continue
                c.px(X(27+k),8+j-wob,cols[min(3,k*4//16)])
    return c.img()

out=sys.argv[1]
sheet=Image.new("RGBA",(12*56*3+40,12*30+20),(26,22,38,255))
x=10
for kw in (dict(),dict(wings=2),dict(wings=1,fire=1)):
    im=iguana(**kw); sheet.paste(im,(x,10),im); x+=12*56+10
sheet.save(out+"/mr_iguana_v2.png")
