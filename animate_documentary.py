#!/usr/bin/env python3
"""Procedural Mars documentary animation: all moving objects are drawn in code."""
import os, json, math, subprocess, sys, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W,H,FPS=640,360,8
OUT='AETHRONIX_MARS_ANIMATED.mp4'
SCRIPT=Path('script.txt').read_text(encoding='utf-8')
parts=re.split(r'(?im)^\s*PART\s+(\d+)\s*[–-].*$',SCRIPT)
chapters=[]
for i in range(1,len(parts),2):
    num=int(parts[i]); body=parts[i+1]
    heading=re.search(rf'(?im)^\s*PART\s+{num}\s*[–-]\s*(.+)$',SCRIPT)
    chapters.append((num,heading.group(1).strip() if heading else f'CHAPTER {num}',body))
if len(chapters)!=11: raise RuntimeError(f'Expected 11 chapters, got {len(chapters)}')
weights=[max(1,len(x[2])) for x in chapters]
lengths=[1425*w/sum(weights) for w in weights]
lengths[-1]+=1425-sum(lengths)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(font_path,15)
small=ImageFont.truetype(font_path,10)
rng=np.random.default_rng(20261116)

# Palette / environments: each chapter gets a bespoke hand-built animated scene.
SCENES=[
 'planet','solar','gravity','mountains','water','life','rover','helicopter','habitat','colony','cosmos'
]
# Sentence-level storyboard: every spoken sentence becomes its own visual beat.
# Scene categories are selected from the actual narration text, not a repeating loop.
SHOT_SECONDS=6.0

def split_beats(body):
    raw=re.split(r'(?<=[।?!…])\s+|[,;:，]\s*|\n+', body.strip())
    beats=[]
    for item in raw:
        item=item.strip(' —–-')
        if len(item)>105:
            bits=re.split(r'\s+(?=(?:और|लेकिन|क्योंकि|इसलिए|यानी|हालाँकि|इसके अलावा)\s+)',item)
            beats.extend(x.strip() for x in bits if len(x.strip())>2)
        elif len(item)>2: beats.append(item)
    return beats

def classify_beat(text, chapter):
    q=text.lower()
    rules=[
      (r'आयरन ऑक्साइड|लोहे वाले खनिज|जंग|ऑक्सीकरण|लाल-भूरा', 'iron_oxide'),
      (r'सूर्य से चौथा|चौथा ग्रह|सौर
…[1 chars truncated — re-run with head/grep/tail for full output]…
5))
    poly(d,[(0,ground+28),(120,ground+4),(250,ground+24),(390,ground-2),(520,ground+20),(640,ground+1),(640,360),(0,360)],(139,58,34,255))
    for _ in range(110):
        xx=int(rr.integers(0,W)); yy=int(rr.integers(ground-15,H)); r=int(rr.integers(1,5))
        circle(d,(xx-r,yy-r//2,xx+r,yy+r//2),(48,22,19,int(rr.integers(40,120))))
    if scene=='mountains':
        poly(d,[(0,255),(120,70),(175,180),(280,20),(400,190),(520,75),(640,235),(640,360),(0,360)],(77,35,31,255))
        poly(d,[(250,90),(280,20),(320,100),(290,78)],(195,135,110,255))
        # canyon fissure
        poly(d,[(0,300),(170,245),(290,280),(430,225),(640,280),(640,315),(420,270),(250,325),(100,285)],(36,19,20,255))
    if scene=='water':
        poly(d,[(0,265),(110,238),(210,260),(310,230),(420,250),(540,225),(640,240),(640,292),(530,278),(420,302),(300,275),(180,305),(0,285)],(49,87,105,220))
        for yy in range(250,290,8): line(d,[(20,yy),(180,yy-4),(300,yy+3),(500,yy-3)],(145,190,198,120),2)
    if scene in ('habitat','colony','mars_farm','water_system','oxygen_factory','solar_power'):
        # distant habitat domes
        for cx,cy,rad in [(440,210,43),(535,216,34),(350,222,27)]:
            circle(d,(cx-rad,cy-rad,cx+rad,cy+rad),(95,144,155,95),(210,225,225,230),2)
            line(d,[(cx-rad,cy),(cx+rad,cy)],(220,235,235,180),1)
            line(d,[(cx,cy-rad),(cx,cy+rad)],(220,235,235,180),1)
    return im

def draw_rover(d,t,xoff=0,scale=1.0,arm=True):
    x=int(190+90*math.sin(t*.32)+xoff); y=248
    s=scale
    # suspension and body
    line(d,[(x-42*s,y),(x+42*s,y)],(40,28,25,255),4)
    for wx in (x-35*s,x,x+35*s):
        r=14*s; circle(d,(wx-r,y-r,wx+r,y+r),(28,28,30,255),(205,160,116,255),2)
        circle(d,(wx-5*s,y-5*s,wx+5*s,y+5*s),(175,115,65,255))
        a=t*5+wx*.02
        for k in range(6):
            aa=a+k*math.pi/3
            line(d,[(wx,y),(wx+math.cos(aa)*r*.8,y+math.sin(aa)*r*.8)],(210,175,130,255),2)
    poly(d,[(x-44*s,y-38*s),(x+28*s,y-38*s),(x+42*s,y-9*s),(x-50*s,y-9*s)],(181,139,87,255),(54,42,35,255),2)
    poly(d,[(x-27*s,y-58*s),(x+18*s,y-58*s),(x+31*s,y-38*s),(x-40*s,y-38*s)],(198,164,112,255),(45,38,33,255),2)
    # solar panel
    poly(d,[(x-72*s,y-59*s),(x-33*s,y-59*s),(x-27*s,y-39*s),(x-78*s,y-39*s)],(25,61,93,255),(175,190,195,255),2)
    for k in range(1,4): line(d,[(x-72*s+k*11*s,y-59*s),(x-72*s+k*11*s,y-39*s)],(140,185,210,220),1)
    # articulated science arm: two moving joints
    if arm:
        a1=-.8+.28*math.sin(t*1.1); a2=.7+.45*math.sin(t*.8+1)
        p0=(x-15*s,y-54*s); p1=(p0[0]+math.cos(a1)*35*s,p0[1]+math.sin(a1)*35*s); p2=(p1[0]+math.cos(a1+a2)*27*s,p1[1]+math.sin(a1+a2)*27*s)
        line(d,[p0,p1,p2],(212,190,155,255),5); circle(d,(p1[0]-5*s,p1[1]-5*s,p1[0]+5*s,p1[1]+5*s),(65,65,60,255))
        circle(d,(p2[0]-4*s,p2[1]-4*s,p2[0]+4*s,p2[1]+4*s),(230,190,110,255))
    # camera mast pans
    mastx=x+18*s; line(d,[(mastx,y-56*s),(mastx+4*s,y-83*s)],(185,185,175,255),3)
    circle(d,(mastx-8*s,y-91*s,mastx+16*s,y-77*s),(42,60,68,255),(230,210,175,255),2)
    circle(d,(mastx+2*s,y-88*s,mastx+8*s,y-82*s),(50,150,210,255))
    # dust trail
    for k in range(8):
        xx=x-55*s-((t*22+k*17)%90); yy=y-2-(k%3)*5
        circle(d,(xx-3,yy-2,xx+3,yy+2),(222,147,93,95))

def draw_astronaut(d,t):
    x=int(155+42*math.sin(t*.7)); y=247
    # slow low-gravity hop
    hop=abs(math.sin(t*1.05))*22
    yy=y-hop
    circle(d,(x-12,yy-60,x+12,yy-36),(214,222,219,255),(55,65,68,255),2)
    circle(d,(x-7,yy-54,x+7,yy-44),(30,65,80,255))
    line(d,[(x,yy-36),(x,yy+3)],(220,220,210,255),12)
    line(d,[(x,yy-27),(x-19,yy-10),(x-25,yy+1)],(210,215,210,255),7)
    line(d,[(x,yy-25),(x+18,yy-9),(x+25,yy-3)],(210,215,210,255),7)
    line(d,[(x,yy+2),(x-13,yy+22),(x-22,yy+22)],(220,220,210,255),8)
    line(d,[(x,yy+2),(x+14,yy+18),(x+25,yy+18)],(220,220,210,255),8)
    circle(d,(x+12,yy-24,x+19,yy-17),(195,160,105,255))

def draw_helicopter(d,t):
    x=int(130+(t%42)*9); y=int(118+28*math.sin(t*.55))
    # Ingenuity-like drone: body, legs, four blades rotating
    line(d,[(x,y+3),(x-17,y+25),(x+17,y+25),(x,y+3)],(215,195,150,255),3)
    poly(d,[(x-12,y-8),(x+12,y-8),(x+16,y+7),(x-16,y+7)],(185,150,98,255),(45,38,30,255),2)
    line(d,[(x,y-8),(x,y-28)],(220,205,170,255),2)
    for arm in (-1,1): line(d,[(x,y-26),(x+arm*30,y-26)],(220,205,170,255),2)
    a=t*18
    for arm in (-1,1):
        cx=x+arm*30; line(d,[(cx-26*math.cos(a),y-26-8*math.sin(a)),(cx+26*math.cos(a),y-26+8*math.sin(a))],(235,235,225,220),3)

def draw_hab(d,t):
    # foreground pressurized habitat module with blinking status lights
    x=150+int(5*math.sin(t*.2)); y=226
    circle(d,(x-55,y-45,x+55,y+45),(105,150,160,115),(225,235,228,255),3)
    line(d,[(x-55,y),(x+55,y)],(235,235,220,200),2)
    line(d,[(x,y-45),(x,y+45)],(235,235,220,200),2)
    # airlock
    poly(d,[(x+48,y-12),(x+82,y-12),(x+82,y+28),(x+48,y+28)],(140,155,150,255),(220,220,205,255),2)
    circle(d,(x+72,y-4,x+78,y+2),(60,240,150,255) if int(t*3)%2 else (240,170,60,255))
    # antenna dish rotates
    line(d,[(x-30,y-42),(x-45,y-75)],(210,205,185,255),3)
    circle(d,(x-58,y-88,x-32,y-68),None,(230,220,190,255),2)

def draw_life(d,t):
    # microscope-style scientific callout plus rover sampling a rock
    draw_rover(d,t,scale=.78)
    circle(d,(455,75,595,215),(22,33,45,210),(170,195,205,255),3)
    for k in range(18):
        a=k*2.4+t*.25; rr=18+(k%4)*12
        cx=525+math.cos(a)*rr; cy=145+math.sin(a)*rr
        circle(d,(cx-4,cy-4,cx+4,cy+4),(90,215,165,220))
    line(d,[(465,180),(430,225)],(210,225,220,220),2)

def draw_special(d,scene,t,shot_no):
    # Distinct bespoke documentary compositions, with continuous motion in each shot.
    pulse=(math.sin(t*2.0)+1)/2
    if scene=='iron_oxide':
        # macro mineral cross-section and drifting red dust
        for i in range(7):
            x=65+i*78; y=105+int(8*math.sin(t+i))
            circle(d,(x-34,y-34,x+34,y+34),(130+i*5,55+i*2,32,255),(230,145,90,255),2)
            for k in range(9): circle(d,(x-24+(k*17)%48,y-20+(k*13)%40,x-19+(k*17)%48,y-15+(k*13)%40),(230,120,66,220))
        line(d,[(70,250),(570,250)],(235,190,150,180),2)
    elif scene=='solar_system':
        circle(d,(250,80,390,220),(255,177,70,255),(255,220,150,255),3)
        for r,col,sz,spd in [(100,(80,140,210,255),12,.5),(165,(180,70,42,255),15,.3),(225,(170,125,95,255),8,.22)]:
            circle(d,(320-r,150-r*.32,320+r,150+r*.32),None,(170,175,190,120),1)
            a=t*spd+shot_no; x=320+r*math.cos(a); y=150+r*.32*math.sin(a); circle(d,(x-sz,y-sz,x+sz,y+sz),col)
    elif scene=='planet_scale':
        circle(d,(75,75,265,265),(45,105,170,255),(190,220,240,255),2); circle(d,(360,105,530,275),(160,65,43,255),(240,155,105,255),2)
        line(d,[(270,175),(350,175)],(240,230,210,255),3); poly(d,[(338,165),(355,175),(338,185)],(240,230,210,255))
    elif scene=='mars_clock':
        cx,cy=320,175; circle(d,(cx-105,cy-105,cx+105,cy+105),(28,34,43,255),(235,200,160,255),5)
        for k in range(12):
            a=k*math.pi/6; line(d,[(cx+85*math.sin(a),cy-85*math.cos(a)),(cx+95*math.sin(a),cy-95*math.cos(a))],(240,225,200,255),3)
        a=t*1.0; line(d,[(cx,cy),(cx+70*math.sin(a),cy-70*math.cos(a))],(250,170,90,255),5)
        line(d,[(cx,cy),(cx+50*math.sin(a*12),cy-50*math.cos(a*12))],(130,210,245,255),3)
    elif scene=='mars_year':
        circle(d,(270,110,370,210),(240,170,65,255))
        a=t*.55; x=320+180*math.cos(a); y=160+60*math.sin(a); circle(d,(x-28,y-28,x+28,y+28),(170,65,42,255),(245,160,110,255),2)
        circle(d,(130,80,510,240),None,(190,180,160,150),2)
    elif scene=='seasons':
        for i,c in enumerate([(190,95,50,255),(205,145,65,255),(130,95,75,255),(90,125,155,255)]):
            x=55+i*145; poly(d,[(x,260),(x+60,145),(x+120,260)],c); circle(d,(x+45,80,x+75,110),(255,195,90,255))
        for k in range(22): circle(d,(int((k*29+t*18)%640),int(80+(k*31)%170),int((k*29+t*18)%640)+3,int(83+(k*31)%170)),(230,220,210,170))
    elif scene=='gravity':
        draw_astronaut(d,t)
        for k in range(4):
            x=410+k*42; y=210-int(28*abs(math.sin(t*.8+k*.7)))
            circle(d,(x-8,y-8,x+8,y+8),(205,180,140,255),(55,55,55,255),2)
        line(d,[(380,275),(565,275)],(230,205,175,180),2)
    elif scene=='temperature':
        for x in (235,405):
            circle(d,(x-22,90,x+22,220),(235,235,220,255),(65,75,85,255),3); circle(d,(x-31,198,x+31,260),(205,85,58,255),(65,75,85,255),3)
            d.rectangle((x-9,125,x+9,210-int(18*pulse)),fill=(215,70,48,255))
        d.text((260,285),'−60°C',font=font,fill=(245,225,205,255))
    elif scene=='atmosphere':
        circle(d,(220,95,420,295),(155,65,43,255),(230,150,105,255),2)
        for r,a in [(120,80),(140,65),(160,45)]: circle(d,(320-r,195-r,320+r,195+r),None,(120,185,220,a),4)
        for k in range(35):
            x=(k*47+int(t*9))%640; y=35+(k*31)%280; circle(d,(x,y,x+4,y+4),(100,195,220,180))
    elif scene=='radiation':
        circle(d,(255,125,385,255),(155,65,43,255),(220,145,100,255),2)
        for k in range(9):
            x=30+k*70; line(d,[(x,35),(x+30,90),(x+10,125)],(100,220,255,210),3); poly(d,[(x+10,125),(x,111),(x+22,115)],(100,220,255,230))
    elif scene=='olympus':
        poly(d,[(0,275),(95,245),(180,190),(235,100),(280,75),(330,100),(390,190),(485,240),(640,275),(640,360),(0,360)],(120,62,48,255),(230,155,115,255),2)
        circle(d,(270,58,330,118),(48,25,25,255),(225,160,125,255),3)
        for k in range(20): line(d,[(280+k*4,120),(265+k*5,205)],(195,105,76,100),2)
    elif scene=='everest':
        poly(d,[(40,290),(160,110),(235,220),(320,65),(425,220),(500,130),(610,290)],(100,110,115,255),(225,230,220,255),2)
        poly(d,[(285,125),(320,65),(350,130),(325,112)],(240,245,245,255))
        poly(d,[(80,310),(150,260),(220,300),(300,250),(380,300),(470,260),(560,310)],(135,60,42,255))
    elif scene=='canyon':
        poly(d,[(0,80),(130,130),(180,250),(250,220),(330,295),(420,235),(500,130),(640,75),(640,360),(0,360)],(145,65,47,255))
        poly(d,[(0,180),(130,200),(205,315),(285,285),(360,340),(455,280),(520,180),(640,160),(640,360),(0,360)],(35,25,30,255))
        line(d,[(0,185),(640,165)],(230,140,105,200),2)
    elif scene=='geology':
        for i,c in enumerate([(130,60,40,255),(180,85,48,255),(205,125,75,255),(95,55,45,255)]):
            y=145+i*42; poly(d,[(0,y),(130,y-12),(250,y+5),(390,y-15),(520,y+4),(640,y-8),(640,y+45),(0,y+45)],c)
        circle(d,(390,120,500,230),(65,42,35,255),(225,170,120,255),3)
    elif scene=='ancient_water':
        poly(d,[(0,190),(110,145),(200,175),(300,125),(410,160),(520,115),(640,145),(640,295),(0,295)],(115,60,45,255))
        poly(d,[(0,245),(120,220),(230,245),(350,205),(470,230),(640,195),(640,285),(0,285)],(50,115,140,225))
        for k in range(16):
            x=(k*48+int(t*30))%650; y=235+int(8*math.sin(t+k)); line(d,[(x,y),(x+25,y-3),(x+48,y)],(170,220,225,230),2)
    elif scene=='subsurface_ice':
        poly(d,[(0,190),(640,190),(640,360),(0,360)],(145,65,45,255)); poly(d,[(0,245),(640,245),(640,360),(0,360)],(95,145,175,255))
        for k in range(8): poly(d,[(40+k*78,250),(70+k*78,215),(95+k*78,250)],(205,230,240,230))
        line(d,[(0,190),(640,190)],(235,185,140,255),3)
    elif scene=='biosignature':
        draw_life(d,t)
        for k in range(5): circle(d,(430+k*24,50+k%2*22,448+k*24,68+k%2*22),None,(130,235,180,220),2)
    elif scene=='sample_collection':
        draw_rover(d,t,scale=1.0); x=460; y=240
        line(d,[(300,200),(370,215),(x,y)],(225,210,175,255),5); circle(d,(x-12,y-12,x+12,y+12),(230,195,120,255))
        for i in range(4): poly(d,[(455+i*22,285),(468+i*22,285),(468+i*22,325),(455+i*22,325)],(190,205,210,255),(55,65,75,255),1)
    elif scene=='spacecraft':
        circle(d,(65,55,185,175),(55,115,170,255),(170,205,230,255),2); circle(d,(475,210,595,330),(155,65,43,255),(225,145,95,255),2)
        x=320+int(70*math.sin(t*.6)); y=160+int(30*math.cos(t*.8)); poly(d,[(x,y-18),(x+18,y),(x,y+18),(x-18,y)],(205,205,195,255),(60,65,75,255),2)
        for side in (-1,1): poly(d,[(x+side*18,y-7),(x+side*65,y-14),(x+side*65,y+14),(x+side*18,y+7)],(35,85,125,255),(175,205,220,255),1)
    elif scene=='landing':
        x=320+int(10*math.sin(t)); y=80+int(75*(1-math.cos(t*.25))); poly(d,[(x-35,y-35),(x+35,y-35),(x+40,y+20),(x-40,y+20)],(190,185,165,255),(50,55,60,255),3)
        for xx in (x-30,x+30): line(d,[(xx,y+15),(xx-22,y+55),(xx+22,y+55)],(220,205,170,255),4)
        poly(d,[(x-15,y+18),(x+15,y+18),(x+28,y+85),(x-28,y+85)],(245,130,55,150))
    elif scene=='mars_farm':
        for i in range(6):
            x=70+i*90; line(d,[(x,280),(x,205-int(10*math.sin(t+i)))],(75,185,95,255),5);
            for side in (-1,1): circle(d,(x+side*18-13,225-int(10*math.sin(t+i)),x+side*18+13,245-int(10*math.sin(t+i))),(65,170,85,255))
        poly(d,[(25,290),(615,290),(615,320),(25,320)],(85,55,40,255))
    elif scene=='water_system':
        circle(d,(110,110,270,270),(55,130,160,255),(210,230,230,255),3); line(d,[(190,270),(190,320)],(200,220,225,255),6)
        for k in range(4): line(d,[(300,160+k*35),(580,160+k*35)],(85,175,205,220),8)
    elif scene=='oxygen_factory':
        for i in range(3):
            x=140+i*170; d.rounded_rectangle((x-45,120,x+45,270),radius=12,fill=(95,130,140,255),outline=(220,225,220,255),width=3)
            circle(d,(x-15,90,x+15,120),(80,220,245,255)); line(d,[(x,120),(x,85)],(210,220,220,255),3)
        for k in range(12): circle(d,(80+k*42,60+int(10*math.sin(t+k)),86+k*42,66+int(10*math.sin(t+k))),(120,225,240,180))
    elif scene=='solar_power':
        for i in range(4):
            x=70+i*145; poly(d,[(x,150),(x+100,130),(x+110,205),(x+10,225)],(25,75,115,255),(190,215,225,255),2)
            for k in range(1,4): line(d,[(x+k*25,145-k*5),(x+10+k*25,220-k*4)],(140,195,220,255),1)
        circle(d,(460,45,560,145),(255,190,85,255))
    elif scene=='human_exploration':
        draw_astronaut(d,t); draw_rover(d,t+3,scale=.55,arm=False)
        circle(d,(475,50,575,150),(65,125,190,255),(180,220,240,255),2)
    elif scene=='mars_wilderness':
        draw_astronaut(d,t); draw_rover(d,t+2,scale=.6)
    elif scene=='cosmos':
        draw_rover(d,t,scale=.45); circle(d,(480,65,555,140),(60,125,195,255),(190,220,240,255),2)


def draw_overlay(d,idx,title,t,shot_no=1,shot_total=1):
    # clean title band and live motion indicator
    d.rounded_rectangle((18,15,310,45),radius=8,fill=(4,8,15,190),outline=(218,135,90,220),width=1)
    d.text((29,23),f'AETHRONIX  |  CHAPTER {idx:02d}  |  SHOT {shot_no:03d}/{shot_total:03d}',font=small,fill=(255,225,200,255))
    # moving progress line
    d.rectangle((18,338,622,342),fill=(55,45,42,255))
    d.rectangle((18,338,18+int(604*((idx-1)+min(1,t/max(lengths[idx-1],.01)))/11),342),fill=(230,120,72,255))
    # scene-specific HUD labels
    labels=['MARS: THE RED WORLD','FOURTH PLANET FROM THE SUN','MARTIAN GRAVITY: 0.38 g','OLYMPUS MONS / VALLES MARINERIS','ANCIENT RIVER DELTAS','SEARCHING FOR BIOSIGNATURES','AUTONOMOUS ROVER EXPLORATION','INGENUITY FLIGHT TEST','PRESSURIZED HABITAT CONCEPT','HUMAN EXPLORATION SYSTEM','LOOKING BEYOND THE HORIZON']
    d.text((20,315),labels[idx-1],font=small,fill=(250,232,210,235))

def render_frame(idx,title,scene,t,shot_no=1,shot_total=1):
    seed=idx*1009+shot_no*37
    im=make_bg(scene,seed); d=ImageDraw.Draw(im,'RGBA')
    # Every shot has independently seeded dust and a different camera drift.
    drift=int(10*math.sin(t*.45+shot_no));
    for k in range(24):
        x=(k*83 + int(t*(12+(k%5)*5))+shot_no*19)%W; y=(k*47 + int(7*math.sin(t*.7+k+shot_no)))%300
        circle(d,(x,y,x+2,y+2),(235,166,115,115))
    # Continuous motion in the selected scene.
    if scene in ('rover','planet','mountains','water','helicopter','habitat','colony'):
        if scene=='rover': draw_rover(d,t,scale=.8+0.25*((shot_no%3)/2))
        elif scene=='planet': draw_rover(d,t,scale=.65)
        elif scene=='mountains': draw_rover(d,t,scale=.55)
        elif scene=='water': draw_rover(d,t,scale=.65)
        elif scene=='helicopter': draw_helicopter(d,t); draw_rover(d,t,scale=.55,arm=False)
        elif scene in ('habitat','colony'): draw_hab(d,t); draw_astronaut(d,t*.8)
    draw_special(d,scene,t,shot_no)
    # shot-specific moving scan beam / subtle camera sweep
    if scene in ('sample_collection','biosignature','geology'):
        x=200+int((t*65)%300); line(d,[(x,65),(x+35,290)],(100,225,245,110),2)
    draw_overlay(d,idx,title,t,shot_no,shot_total)
    return im.convert('RGB')

# pipe frames straight to ffmpeg; 8fps motion is encoded at 24fps for compatibility.
def main():
    storyboard=build_storyboard()
    print(f'STORYBOARD: {len(storyboard)} individual narration-matched shots',flush=True)
    cmd=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','narration.mp3','-filter_complex',"[0:v]fps=24,scale=1280:720:flags=lanczos,format=yuv420p[v];[1:a]apad,atrim=duration=1425[a]",'-map','[v]','-map','[a]','-t','1425','-c:v','libx264','-preset','ultrafast','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    chapter_totals={i:sum(1 for x in storyboard if x['chapter']==i) for i in range(1,12)}
    chapter_seen={i:0 for i in range(1,12)}
    for shot in storyboard:
        idx,title,scene,dur=shot['chapter'],shot['title'],shot['scene'],shot['duration']
        chapter_seen[idx]+=1; shot_no=chapter_seen[idx]; shot_total=chapter_totals[idx]
        n=max(1,round(dur*FPS))
        for f in range(n):
            frame=render_frame(idx,title,scene,f/FPS,shot_no,shot_total)
            proc.stdin.write(frame.tobytes())
        print(f"CHAPTER {idx}/11 | SHOT {shot_no}/{shot_total} | {scene} | {dur:.1f}s",flush=True)
    proc.stdin.close(); code=proc.wait()
    if code: raise SystemExit(code)
    print('ANIMATED MASTER READY',OUT,flush=True)

if __name__ == '__main__':
    main()
