# AETHRONIX — Mars Documentary

Hindi cinematic documentary project: **MARS – क्या इंसान कभी लाल ग्रह पर रह पाएगा?**

## Production requirements
- Preserve the user's original narration audio: no re-voicing, speed change, pitch change, or omitted dialogue.
- Target master duration: 23:45. The supplied source is approximately 23:44.4; pad only the tail with silence if needed.
- 1920x1080, 16:9, 24 fps, H.264 MP4.
- Follow all 11 parts of `script.txt`; do not invent narration.
- Hindi subtitles must be aligned to the actual recording and reviewed for accuracy.

## Project files
- `script.txt` — the complete 11-part script supplied in chat.
- `scene_plan.json` — cinematic shot concepts for all 11 parts.
- `render.py` — currently validates the input files, script structure, audio metadata, and scene-plan structure.
- `requirements.txt` — Python dependencies.

## Required local/Colab input
Place the original audio file in the working folder as:
- `narration.mp3`

The audio is not committed to GitHub because it is a large personal source recording. Use the original uploaded recording; do not replace it with generated narration.

## Current project status
The script and 11-part visual plan are now in the repository. The current `render.py` is an input-validation/preparation stage only. It does **not** yet render the finished animated MP4 or produce verified synchronized subtitles. Do not describe the documentary as complete until the visual render and subtitle alignment have both been generated and checked.

## Source audio details
Previously inspected source: MP3, 48 kHz, mono, 320 kbps, approximately 23:44.4. Target duration is 23:45. Preserve the full original audio and add only a short silence pad at the end if required.
