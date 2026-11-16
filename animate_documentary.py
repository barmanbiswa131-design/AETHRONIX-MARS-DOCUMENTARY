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

def poly(d, pts, fill, outline=None, width=1): d.polygon(pts,fill=fill,outline=outline,width=width)
def line(d, pts, fill, width=1): d.line(pts,fill=fill,width=width)
def circle(d, box, fill, outline=None, width=1): d.ellipse(box,fill=fill,outline=outline,width=width)

def make_bg(scene, seed):
    rr=np.random.default_rng(seed)
    y,x=np.mgrid[0:H,0:W]
    arr=np.zeros((H,W,3),dtype=np.uint8)
    # dark atmospheric gradient
    arr[:,:,0]=np.clip(8+(y/H)*35,0,255)
    arr[:,:,1]=np.clip(10+(y/H)*15,0,255)
    arr[:,:,2]=np.clip(22+(y/H)*18,0,255)
    im=Image.fromarray(arr,'RGB').convert('RGBA')
    d=ImageDraw.Draw(im,'RGBA')
    # star field
    for _ in range(100):
        sx=int(rr.integers(0,W)); sy=int(rr.integers(0,205)); a=int(rr.integers(60,210)); r=int(rr.integers(1,3))
        circle(d,(sx-r,sy-r,sx+r,sy+r),(220,226,255,a))
    if scene in ('planet','solar','cosmos'):
        # Mars horizon / globe, with shaded limb
        if scene=='planet':
            circle(d,(375,35,620,280),(151,61,36,255),(238,143,94,255),2)
            for k in range(18):
                xx=int(rr.integers(395,595)); yy=int(rr.integers(60,250)); r=int(rr.integers(4,22))
                circle(d,(xx-r,yy-r//2,xx+r,yy+r//2),(105,42,29,90))
        elif scene=='solar':
            circle(d,(490,55,605,170),(235,165,73,255))
            for cx,cy,r,c in [(190,145,42,(67,115,178,255)),(310,145,33,(167,65,40,255)),(410,145,22,(185,100,63,255))]:
                circle(d,(cx-r,cy-r,cx+r,cy+r),c,(240,190,145,200),1)
            circle(d,(470,35,625,190),None,(130,160,190,120),1)
        else:
            circle(d,(430,55,620,245),(7,10,28,255),(100,120,160,255),2)
            circle(d,(490,100,520,130),(180,190,220,255))
    # surface terrain with layers and mountain silhouettes
    ground=220 if scene not in ('mountains','water') else 235
    poly(d,[(0,ground),(90,ground-30),(170,ground-4),(260,ground-42),(350,ground-8),(450,ground-50),(540,ground-15),(640,ground-35),(640,360),(0,360)],(104,43,29,255))
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
    if scene=='habitat' or scene=='colony':
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

def draw_overlay(d,idx,title,t):
    # clean title band and live motion indicator
    d.rounded_rectangle((18,15,310,45),radius=8,fill=(4,8,15,190),outline=(218,135,90,220),width=1)
    d.text((29,23),f'AETHRONIX  |  CHAPTER {idx:02d}',font=small,fill=(255,225,200,255))
    # moving progress line
    d.rectangle((18,338,622,342),fill=(55,45,42,255))
    d.rectangle((18,338,18+int(604*((idx-1)+min(1,t/max(lengths[idx-1],.01)))/11),342),fill=(230,120,72,255))
    # scene-specific HUD labels
    labels=['MARS: THE RED WORLD','FOURTH PLANET FROM THE SUN','MARTIAN GRAVITY: 0.38 g','OLYMPUS MONS / VALLES MARINERIS','ANCIENT RIVER DELTAS','SEARCHING FOR BIOSIGNATURES','AUTONOMOUS ROVER EXPLORATION','INGENUITY FLIGHT TEST','PRESSURIZED HABITAT CONCEPT','HUMAN EXPLORATION SYSTEM','LOOKING BEYOND THE HORIZON']
    d.text((20,315),labels[idx-1],font=small,fill=(250,232,210,235))

def render_frame(idx,title,scene,t):
    im=make_bg(scene,idx); d=ImageDraw.Draw(im,'RGBA')
    # Animated dust grains / atmospheric particles drift across every surface scene.
    for k in range(32):
        x=(k*83 + int(t*(16+(k%4)*7)))%W; y=(k*47 + int(8*math.sin(t*.7+k)))%300
        circle(d,(x,y,x+2,y+2),(235,166,115,100))
    if scene=='planet':
        # animated orbital spacecraft and moving orbit trail
        a=t*.42; cx=490+100*math.cos(a); cy=155+52*math.sin(a)
        circle(d,(cx-5,cy-5,cx+5,cy+5),(220,225,225,255),(245,190,130,255),1)
        line(d,[(490,155),(cx,cy)],(225,170,120,90),1)
        draw_rover(d,t,scale=.82)
    elif scene=='solar':
        # orbiting planets move along elliptical paths
        for j,(rad,sz,col) in enumerate([(90,7,(90,140,200,255)),(145,10,(190,78,48,255)),(205,13,(180,105,75,255))]):
            a=t*(.35-j*.06)+j*1.5; x=310+math.cos(a)*rad; y=145+math.sin(a)*rad*.34
            circle(d,(x-sz,y-sz,x+sz,y+sz),col)
    elif scene=='gravity':
        draw_astronaut(d,t)
        # floating sample/tool demonstrates lower gravity
        x=390+int(18*math.sin(t*1.2)); y=190-int(24*abs(math.sin(t*.9)))
        circle(d,(x-10,y-10,x+10,y+10),(205,175,130,255),(65,55,48,255),2)
        line(d,[(x,y-20),(x,y+20)],(220,205,175,255),2)
    elif scene=='mountains':
        # aerial camera glides along canyon; rover traverses ridge
        shift=int((t*9)%180)
        line(d,[(0,270+int(5*math.sin(t))),(640,250+int(8*math.sin(t*.6)))],(225,140,95,170),2)
        draw_rover(d,t,scale=.62)
    elif scene=='water':
        # ancient river flows and ripples move downstream
        for k in range(15):
            x=(k*49+int(t*32))%640; y=264+int(8*math.sin(k+t*1.4))
            line(d,[(x,y),(x+24,y-2),(x+40,y+1)],(145,205,220,200),2)
        draw_rover(d,t,scale=.72)
    elif scene=='life': draw_life(d,t)
    elif scene=='rover':
        draw_rover(d,t,scale=1.05)
        # laser/scanner sweeps across a rock target
        x=480; y=252+int(4*math.sin(t*2))
        circle(d,(x-18,y-13,x+18,y+13),(96,67,48,255),(180,135,90,255),2)
        line(d,[(380,170),(x,y)],(90,230,245,220),2)
        circle(d,(x-4,y-4,x+4,y+4),(120,240,255,230))
    elif scene=='helicopter':
        draw_rover(d,t,scale=.68,arm=False); draw_helicopter(d,t)
        # rotor downwash dust ring
        x=int(130+(t%42)*9); y=int(145+28*math.sin(t*.55))
        for k in range(3):
            circle(d,(x-32-k*9,245-k*5,x+32+k*9,255+k*5),None,(220,160,110,100),1)
    elif scene=='habitat':
        draw_hab(d,t); draw_astronaut(d,t*.7)
        # solar arrays slowly track the sun
        a=.2*math.sin(t*.18); x=380; y=250
        line(d,[(x,y),(x+55*math.cos(a),y-55*math.sin(a))],(215,210,190,255),3)
        poly(d,[(x+45,y-65),(x+95,y-75),(x+103,y-47),(x+52,y-38)],(28,67,100,255),(170,200,220,255),2)
    elif scene=='colony':
        draw_hab(d,t); draw_rover(d,t,scale=.65)
        # cargo lander descent with animated engine plume
        lx=510+int(8*math.sin(t*.2)); ly=125+int(8*math.sin(t*.7))
        poly(d,[(lx-24,ly-20),(lx+24,ly-20),(lx+30,ly+10),(lx-30,ly+10)],(170,170,160,255),(45,45,45,255),2)
        for xx in (lx-20,lx+20): line(d,[(xx,ly+7),(xx-14,ly+30),(xx+14,ly+30)],(210,200,175,255),3)
        poly(d,[(lx-8,ly+10),(lx+8,ly+10),(lx+18,ly+50),(lx-18,ly+50)],(250,135,65,150))
    elif scene=='cosmos':
        # a distant Earth rises above Mars horizon, slow atmospheric glow
        earthx=500; earthy=120+int(9*math.sin(t*.12))
        circle(d,(earthx-32,earthy-32,earthx+32,earthy+32),(60,120,190,255),(180,215,240,255),2)
        circle(d,(earthx-20,earthy-8,earthx+4,earthy+12),(85,155,110,220))
        draw_rover(d,t,scale=.5)
    draw_overlay(d,idx,title,t)
    return im.convert('RGB')

# pipe frames straight to ffmpeg; 8fps motion is encoded at 24fps for compatibility.
def main():
    cmd=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','narration.mp3','-filter_complex',"[0:v]fps=24,scale=1280:720:flags=lanczos,format=yuv420p[v];[1:a]apad,atrim=duration=1425[a]",'-map','[v]','-map','[a]','-t','1425','-c:v','libx264','-preset','ultrafast','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for (idx,title,_),dur,scene in zip(chapters,lengths,SCENES):
        n=round(dur*FPS)
        for f in range(n):
            frame=render_frame(idx,title,scene,f/FPS)
            proc.stdin.write(frame.tobytes())
        print(f'CHAPTER {idx}/11 rendered: {dur:.1f}s',flush=True)
    proc.stdin.close(); code=proc.wait()
    if code: raise SystemExit(code)
    print('ANIMATED MASTER READY',OUT,flush=True)

if __name__ == '__main__':
    main()
