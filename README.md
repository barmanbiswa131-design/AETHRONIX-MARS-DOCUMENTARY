# AETHRONIX — Mars Documentary

Hindi cinematic documentary project: **MARS – क्या इंसान कभी लाल ग्रह पर रह पाएगा?**

## Non-negotiable production rules
- Use the supplied original narration audio unchanged (no speed/pitch change, no re-voicing, no omitted dialogue).
- Target master duration: 23:45. If the source audio is shorter, pad only the tail with silence; never time-stretch it.
- 1920x1080, 16:9, 24 fps, H.264 MP4.
- Visuals must follow the exact 11-part Hindi script. Do not invent narration.
- Hindi subtitles must be derived from the supplied script and checked against the original narration.

## Project inputs
Place these files in the Colab working folder:
- `narration.mp3` — the user's original voice recording.
- `script.txt` — the complete original 11-part script, verbatim.
- `scene_plan.json` — shot-by-shot visual plan keyed to the script sections.

## Render
The intended workflow is Google Colab (GPU optional). Install requirements, upload the three inputs, then run `python render.py`.

**Important:** the full narration script is not embedded in this repository yet. Do not render a final synchronized documentary until the exact script and scene plan have been supplied and checked. The renderer currently validates inputs and audio duration, and prepares the production timeline; it does not fabricate missing dialogue or claim unverified subtitle synchronization.

## Audio validation
The source recording previously inspected for this project is MP3, 48 kHz, mono, 320 kbps, approximately 23:44.4. The render target is 23:45. Audio must be copied without speed changes, with only a short silence pad at the end if required.
