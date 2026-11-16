# AETHRONIX — Mars Documentary

Hindi cinematic documentary project: **MARS – क्या इंसान कभी लाल ग्रह पर रह पाएगा?**

## Rendered master
The current rendered MP4 is 23:45 (1425 seconds), 16:9 at 1280×720, H.264 video + AAC mono audio. It uses the original narration recording without time-stretching; the final 0.6 seconds are silence padding.

**Download:** https://d2ol7oe51mr4n9.cloudfront.net/user_3946drpYxq1rUP4wFwPvFyvK6Kh/474624da-584e-4c3c-82c9-029e06afe9b7.mp4

The visual track contains 11 chapter-specific Mars/NASA imagery sequences with slow camera movement and chapter title overlays. It is a cinematic motion-still documentary, not full 3D character/spacecraft animation. The delivered MP4 currently has no burned-in subtitles; a speech-recognition pass was not completed reliably, so no unverified captions are claimed.

## Project files
- `script.txt` — the complete 11-part script supplied by the creator.
- `scene_plan.json` — shot concepts for all 11 parts.
- `render.py` — Python/FFmpeg renderer that downloads topical NASA imagery, creates moving chapter visuals, preserves the source narration, and attempts speech-timed subtitles.
- `requirements.txt` — Python dependencies.

## Source audio
The original 48 kHz mono MP3 is kept outside this public repository because it is a large source recording. Do not replace it with generated narration.

## Rebuild
Place the original recording in the working folder as `narration.mp3`, then run:

```bash
python3 render.py --audio narration.mp3 --script script.txt --scene-plan scene_plan.json --out AETHRONIX_MARS_DOCUMENTARY.mp4
```
