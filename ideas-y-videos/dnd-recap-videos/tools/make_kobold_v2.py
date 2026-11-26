#!/usr/bin/env python3
"""Kobold v2 (36x32): escamas rojas, dos cuernos curvos, hocico, vendas grises, taparrabos amarillo, daga, cola larga.
Los siete kobolds son iguales. Uso: python3 tools/make_kobold_v2.py out_dir"""
import sys, os
from PIL import Image
PAL=dict(q=(230,100,110),c=(150,210,250),o=(250,140,40),T=(212,172,112),r=(196,62,52),R=(132,38,40),n=(222,120,102),y=(250,222,70),K=(18,12,20),k=(44,30,34),w=(244,240,226),
 W=(150,152,164),Y=(228,190,62),Z=(160,120,36),A=(214,220,232),s=(110,70,44))
def build(dagger=True, arms_up=False):
    p={}
    def px(x,y,c):
        if 0<=x<36 and 0<=y<32: p[(x,y)]=c
    def rect(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): px(x,y,c)
    # cola (detrás)
    for i,(x,y) in enumerate([(23,25),(24,26),(25,27),(26,27),(27,26),(28,25),(29,24),(30,23),(30,22)]):
        rect(x,y,x+1,y+1,'r' if i<7 else 'R')
    # cuernos
    for (x,y) in [(12,4),(11,3),(10,2),(10,1),(9,0)]: px(x,y,'k'); px(x+1,y,'k')
    for (x,y) in [(23,4),(24,3),(25,2),(25,1),(26,0)]: px(x,y,'k'); px(x-1,y,'k')
    # cabeza
    rect(12,5,23,11,'r'); rect(11,7,11,10,'r'); rect(24,7,24,10,'r')
    rect(15,9,20,12,'n'); px(16,10,'K'); px(19,10,'K'); rect(15,12,20,12,'R'); px(16,12,'w'); px(19,12,'w')
    rect(13,6,15,6,'R'); rect(20,6,22,6,'R')
    rect(13,7,14,8,'y'); px(14,7,'K'); px(14,8,'K'); rect(21,7,22,8,'y'); px(21,7,'K'); px(21,8,'K')
    # hombros y torso
    rect(10,12,25,14,'r'); rect(12,14,23,21,'r'); rect(15,14,20,20,'n')
    for (x,y) in [(13,15),(22,16),(14,18),(21,19),(11,13),(24,13)]: px(x,y,'R')
    for y in range(15,21,2): rect(16,y,19,y,'R')
    # brazo izq con vendas
    if not arms_up:
        rect(7,13,10,20,'r'); rect(7,16,10,18,'W'); rect(6,20,10,22,'r'); px(6,23,'K'); px(8,23,'K'); px(10,23,'K')
    else:
        rect(6,6,9,13,'r'); rect(6,9,9,10,'W'); rect(5,3,10,6,'r'); px(5,2,'K'); px(7,2,'K'); px(10,2,'K')
    # brazo der con daga
    if not arms_up:
        rect(25,13,28,19,'r'); rect(25,15,28,17,'W'); rect(26,19,29,21,'r')
    else:
        rect(26,6,29,13,'r'); rect(26,9,29,10,'W'); rect(25,3,30,6,'r'); px(25,2,'K'); px(28,2,'K'); px(30,2,'K')
    if dagger: rect(28,9,28,16,'A'); px(28,8,'A'); rect(27,17,29,17,'K'); rect(28,18,28,20,'s')
    # taparrabos
    rect(12,21,23,21,'Z'); rect(13,22,22,27,'Y'); rect(15,28,20,28,'Y'); rect(17,22,18,27,'Z')
    # piernas y pies
    rect(12,26,15,29,'r'); rect(20,26,23,29,'r'); rect(10,30,16,31,'r'); rect(19,30,25,31,'r')
    for x in (10,12,14,19,21,23): px(x,31,'K')
    return p
def variant(n,expr='normal'):
    p=build(dagger=False,arms_up=(expr=='scared'))
    def px(x,y,c):
        if 0<=x<36 and 0<=y<32: p[(x,y)]=c
    def rect(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): px(x,y,c)
    if n==0:   # Julia: libreta + cucharon
        rect(3,16,8,22,'s'); rect(4,17,7,21,'w'); rect(5,18,6,18,'k'); rect(5,20,6,20,'k')
        rect(28,10,28,20,'s'); rect(27,6,29,9,'A'); px(28,7,'k'); px(28,8,'k')
    elif n==1: # Piedrin: robusto + barril
        rect(9,14,10,22,'r'); rect(25,14,26,22,'r'); rect(11,22,24,23,'r')
        rect(0,14,8,24,'s'); rect(0,16,8,16,'k'); rect(0,22,8,22,'k'); rect(1,14,7,14,'Z')
    elif n==2: # Braulio: mandolina desafinada
        rect(27,18,33,24,'s'); rect(29,20,31,22,'K'); rect(31,8,32,17,'s'); px(30,8,'y'); px(33,9,'y'); px(30,11,'y'); px(33,12,'y')
    elif n==3: # Chispa: antorcha + barril de polvora
        rect(28,10,28,20,'s'); rect(27,5,29,9,'y'); rect(28,6,28,8,'o'); px(28,4,'y')
        rect(3,19,8,24,'k'); rect(3,20,8,20,'W'); rect(3,23,8,23,'W')
    elif n==4: # Zurdito: catalejo
        for i in range(9): px(27+i//1,19-i,'s'); px(28+i,19-i,'s')
        px(36-1,10,'A'); px(34,10,'A'); px(33,10,'A')
    elif n==5: # Pancho: martillo + tabla
        rect(28,12,28,20,'s'); rect(26,8,31,12,'W'); rect(26,8,31,8,'A')
        rect(0,17,9,19,'Z'); rect(0,17,9,17,'T')
    elif n==6: # Lola: soga
        for (x0,y0,x1,y1) in [(4,11,9,16)]:
            rect(x0,y0,x1,y1,'T'); rect(x0+1,y0+1,x1-1,y1-1,'R')
        rect(28,19,29,27,'T'); px(30,27,'T')
    if expr=='scared':
        p={k:v for k,v in p.items() if not (k[0]<=10 and k[1]>=11 and k[1]<=24 and v in ('s','Z','T','k','W','w','A','R','Y') and False)}
    def px2(x,y,c): p[(x,y)]=c
    def rect2(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): p[(x,y)]=c
    if expr=='sing':
        rect2(13,7,14,8,'r'); rect2(21,7,22,8,'r'); rect2(13,8,14,8,'K'); rect2(21,8,22,8,'K')
        rect2(13,5,15,5,'R'); rect2(20,5,22,5,'R')
        rect2(15,11,20,14,'K'); rect2(15,11,20,11,'w'); rect2(17,14,18,14,'q')
    elif expr=='scared':
        rect2(13,7,15,9,'w'); px2(14,8,'K'); rect2(20,7,22,9,'w'); px2(21,8,'K')
        px2(12,6,'R'); rect2(13,5,14,5,'R'); px2(23,6,'R'); rect2(21,5,22,5,'R')
        rect2(16,12,19,14,'K'); px2(17,12,'w'); px2(18,12,'w')
        for (x,y) in [(10,6),(10,7),(25,5),(25,6),(26,6)]: px2(x,y,'c')
    return p
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
sheet=Image.new("RGBA",(36*7+8*8,40*3),(26,22,38,255))
for row,expr in enumerate(('normal','sing','scared')):
    for n in range(7):
        im=Image.new("RGBA",(36,32),(0,0,0,0))
        for (x,y),c in variant(n,expr).items(): im.putpixel((x,y),PAL[c]+(255,))
        im.save(f"{out}/kobold_{n}"+("" if expr=='normal' else "_"+expr)+".png"); sheet.alpha_composite(im,(8+n*(36+8),4+row*40))
sheet.resize((sheet.width*3,sheet.height*3),Image.NEAREST).save("/tmp/kobolds_v4.png")
