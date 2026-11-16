#!/usr/bin/env python3
"""Render the AETHRONIX Mars documentary from the original narration."""
import argparse, json, os, re, subprocess, sys, textwrap, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H, FPS = 1280, 720, 24
NASA_API = "https://images-api.nasa.gov/search"

def sh(cmd):
    subprocess.run(cmd, check=True)

def get_font(size, bold=False):
    choices = (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] if bold else
               ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"])
    for f in choices:
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def load_nasa_image(query, out):
    try:
        url = NASA_API + "?" + urllib.parse.urlencode({"q": query, "media_type": "image", "page_size": 8})
        req = urllib.request.Request(url, headers={"User-Agent":"AETHRONIX-documentary/1.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        for item in data.get("collection", {}).get("items", []):
            links = item.get("links", [])
            asset = next((x.get("href") for x in links if x.get("render") == "image"), None)
            if not asset: continue
            try:
                raw = urllib.request.urlopen(asset, timeout=40).read()
                im = Image.open(__import__("io").BytesIO(raw)).convert("RGB")
                if im.width >= 500 and im.height >= 250:
                    im.thumbnail((W,H), Image.Resampling.LANCZOS)
                    bg = Image.new("RGB",(W,H),(8,10,18))
                    bg.paste(im,((W-im.width)//2,(H-im.height)//2))
                    bg.save(out, quality=92)
                    return True
            except Exception: pass
    except Exception as e:
        print("NASA image fallback:", query, str(e)[:160])
    return False

def procedural_mars(out, seed):
    rng=np.random.default_rng(seed)
    y,x=np.mgrid[0:H,0:W]
    base=np.zeros((H,W,3),dtype=np.uint8)
    horizon=int(H*(.55+rng.random()*.12))
    noise=rng.normal(0,10,(H,W))
    base[:,:,0]=np.clip(18+noise,0,255)
    base[:,:,1]=np.clip(10+noise*.45,0,255)
    base[:,:,2]=np.clip(12+noise*.35,0,255)
    sky=y<horizon
    base[:,:,0][sky]=np.clip(18+(y[sky]/H)*35+noise[sky]*.25,0,255)
    base[:,:,1][sky]=np.clip(12+(y[sky]/H)*18+noise[sky]*.2,0,255)
    base[:,:,2][sky]=np.clip(24+(y[sky]/H)*20+noise[sky]*.2,0,255)
    ground=~sky
    slope=(y-H*.55)*.22 + 18*np.sin(x/130)
    base[:,:,0][ground]=np.clip(92+slope[ground]+noise[ground],0,255)
    base[:,:,1][ground]=np.clip(35+slope[ground]*.32+noise[ground]*.4,0,255)
    base[:,:,2][ground]=np.clip(23+slope[ground]*.2+noise[ground]*.3,0,255)
    im=Image.fromarray(base).filter(ImageFilter.GaussianBlur(1.2))
    d=ImageDraw.Draw(im,"RGBA")
    for _ in range(120):
        xx=int(rng.integers(0,W)); yy=int(rng.integers(horizon,H))
        rr=int(rng.integers(2,22))
        d.ellipse((xx-rr,yy-rr//3,xx+rr,yy+rr//3),fill=(38,17,13,80))
    im.save(out,quality=90)

def make_card(src, out, title, part):
    im=Image.open(src).convert("RGB").resize((W,H),Image.Resampling.LANCZOS)
    # Cinematic contrast and dark lower-third for legible title.
    overlay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(overlay)
    for yy in range(430,H):
        a=int(190*(yy-430)/(H-430))
        d.line((0,yy,W,yy),fill=(3,5,10,a))
    d.rounded_rectangle((55,48,245,94),radius=18,fill=(130,42,25,220))
    d.text((75,58),f"AETHRONIX  /  PART {part:02d}",font=get_font(19,True),fill=(255,235,220,255))
    # De-emphasize top and bottom edges.
    im=Image.alpha_composite(im.convert("RGBA"),overlay)
    draw=ImageDraw.Draw(im)
    draw.text((60,560),title,font=get_font(37,True),fill=(255,248,238,255),stroke_width=2,stroke_fill=(20,10,8,220))
    im.convert("RGB").save(out,quality=94)

def parse_parts(path):
    raw=Path(path).read_text(encoding="utf-8")
    matches=list(re.finditer(r"(?im)^\s*(?:PART[\s-]*\d+|भाग[\s-]*\d+|पार्ट[\s-]*\d+)[^\n]*",raw))
    if len(matches)!=11: raise RuntimeError(f"Expected 11 script parts, found {len(matches)}")
    parts=[]
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(raw)
        body=raw[m.end():end].strip()
        parts.append((m.group(0).strip(),body))
    return parts

def subtitles_from_audio(audio, out_srt, script):
    # Use speech recognition timing from the supplied recording, not guessed timing.
    try:
        from faster_whisper import WhisperModel
        model=WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio, beam_size=3, vad_filter=True)
        with open(out_srt,"w",encoding="utf-8") as f:
            n=0
            for seg in segments:
                txt=(seg.text or "").strip()
                if not txt: continue
                n+=1
                def stamp(t):
                    ms=int(round(t*1000)); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
                    return f"{h:02}:{m:02}:{s:02},{ms:03}"
                f.write(f"{n}\n{stamp(seg.start)} --> {stamp(seg.end)}\n{txt}\n\n")
        return True
    except Exception as e:
        print("Whisper subtitles unavailable:",repr(e))
        return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio",default="narration.mp3")
    ap.add_argument("--script",default="script.txt")
    ap.add_argument("--scene-plan",default="scene_plan.json")
    ap.add_argument("--out",default="AETHRONIX_MARS_DOCUMENTARY.mp4")
    args=ap.parse_args()
    audio=Path(args.audio)
    if not audio.exists(): raise SystemExit("Missing narration audio")
    parts=parse_parts(args.script)
    plan=json.loads(Path(args.scene_plan).read_text(encoding="utf-8"))
    if len(plan)!=11: raise SystemExit("Scene plan must have 11 parts")
    os.makedirs("build/stills",exist_ok=True); os.makedirs("build/clips",exist_ok=True)
    # The 11 NASA image searches are topical, one per chapter.
    queries=["Mars planet from space","Mars surface landscape","Mars atmosphere dust storm","Olympus Mons Mars","Mars ancient river delta","Mars Perseverance rover rock","Mars Curiosity rover","Ingenuity Mars helicopter","Mars habitat concept","Perseverance rover Jezero crater","Mars horizon space"]
    durations=[max(35,len(body)) for _,body in parts]
    total=sum(durations)
    durations=[len(body)/sum(len(x[1]) for x in parts)*1425 for _,body in parts]
    # Ensure exact final duration; audio itself is preserved and padded only if short.
    for i,((heading,body),query) in enumerate(zip(parts,queries),1):
        raw=f"build/stills/raw_{i:02}.jpg"
        if not load_nasa_image(query,raw): procedural_mars(raw,i)
        title=heading
        make_card(raw,f"build/stills/part_{i:02}.jpg",title,i)
    clips=[]
    for i,dur in enumerate(durations,1):
        clip=f"build/clips/part_{i:02}.mp4"
        frames=max(1,int(round(dur*FPS)))
        # Slow, continuous camera push-in across each chapter.
        vf=f"zoompan=z='min(zoom+0.00012,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
        sh(["ffmpeg","-y","-loop","1","-i",f"build/stills/part_{i:02}.jpg","-vf",vf,"-frames:v",str(frames),"-an","-c:v","libx264","-preset","ultrafast","-crf","24",clip])
        clips.append(clip)
    with open("build/concat.txt","w") as f:
        for p in clips: f.write("file '"+os.path.abspath(p)+"'\n")
    sh(["ffmpeg","-y","-f","concat","-safe","0","-i","build/concat.txt","-c","copy","build/visual.mp4"])
    srt="build/subtitles.srt"
    has_subs=subtitles_from_audio(str(audio),srt,args.script)
    duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],text=True).strip())
    # Original narration is never sped up, slowed down, or replaced.
    audio_filter="apad,atrim=duration=1425"
    video_in="build/visual.mp4"
    if has_subs:
        # Use a clean, readable subtitle style; preserve ASR wording from the actual audio.
        sh(["ffmpeg","-y","-i",video_in,"-i",str(audio),"-vf",f"subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=35'","-af",audio_filter,"-t","1425","-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",args.out])
    else:
        sh(["ffmpeg","-y","-i",video_in,"-i",str(audio),"-af",audio_filter,"-t","1425","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart",args.out])
    print("DONE",args.out, "audio_seconds",duration, "chapters",len(parts), "subtitles",has_subs)

if __name__=="__main__": main()
