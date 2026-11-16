# AETHRONIX — Mars Documentary

**MARS – क्या इंसान कभी लाल ग्रह पर रह पाएगा?**

## Animated master video

**Watch / download:** https://d2ol7oe51mr4n9.cloudfront.net/user_3946drpYxq1rUP4wFwPvFyvK6Kh/f7ca90bd-f86d-40aa-980e-75fd4405c072.mp4

- Duration: 23:45
- 1280×720, 16:9, 24 fps, H.264 + AAC
- Original narration preserved; tail padded to exactly 23:45
- All visuals are procedural code-drawn animation — no real footage or NASA photos.
- Animated scenes include a moving Mars rover with rotating wheels and articulated science arm, low-gravity astronaut movement, orbiting planets, animated river ripples, rover laser scan, Ingenuity-style helicopter flight with spinning rotors and dust downwash, habitat modules, solar arrays, and a landing vehicle.
- This is stylized 2D motion-graphics animation, not photorealistic 3D CGI.

## Source files

- `script.txt` — complete 11-part narration script.
- `scene_plan.json` — original chapter shot plan.
- `animate_documentary.py` — procedural animation renderer. It draws the scenes and moving objects in Python/Pillow and encodes the full-length MP4 with FFmpeg.
- `render.py` — earlier NASA-still/slow-zoom renderer (kept for reference).

## Rebuild

Install Python packages from `requirements.txt` and make sure FFmpeg is installed. Put the original source recording in the project directory as `narration.mp3`, then run:

```bash
python3 animate_documentary.py
```

The output is `AETHRONIX_MARS_ANIMATED.mp4`.
