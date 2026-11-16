#!/usr/bin/env python3
"""AETHRONIX Mars documentary render preparation.

This safe first-stage renderer validates the supplied narration and exact script.
It deliberately refuses to invent scene timings or subtitles when the verbatim
script/scene plan is missing. Final visual rendering is the next pipeline stage.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

TARGET_SECONDS = 23 * 60 + 45
FPS = 24
WIDTH, HEIGHT = 1920, 1080

def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return p.stdout.strip()

def probe_audio(path: Path) -> dict:
    raw = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,format_name:stream=codec_name,sample_rate,channels,bit_rate",
        "-of", "json", str(path)
    ])
    data = json.loads(raw)
    stream = data["streams"][0]
    return {
        "duration": float(data["format"]["duration"]),
        "format": data["format"]["format_name"],
        "codec": stream.get("codec_name"),
        "sample_rate": int(stream.get("sample_rate", 0)),
        "channels": int(stream.get("channels", 0)),
        "bit_rate": int(stream.get("bit_rate", 0) or 0),
    }

def parse_script(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("script.txt is empty.")
    # Preserve the user's wording. Sections are identified by headings such as
    # PART 1 / PART 2, PART-1, भाग 1, etc. No text is rewritten.
    import re
    matches = list(re.finditer(
        r"(?im)^\s*(?:PART[\s-]*\d+|भाग[\s-]*\d+|पार्ट[\s-]*\d+)[^\n]*",
        text
    ))
    if len(matches) != 11:
        raise ValueError(
            f"Expected exactly 11 clearly headed script parts; found {len(matches)}. "
            "Keep the original script verbatim and label its 11 part headings."
        )
    sections = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end].strip()
        if not body:
            raise ValueError(f"Script section {i+1} has no dialogue.")
        sections.append({"part": i + 1, "heading": m.group(0).strip(), "text": body})
    return sections

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default="narration.mp3")
    ap.add_argument("--script", default="script.txt")
    ap.add_argument("--scene-plan", default="scene_plan.json")
    ap.add_argument("--out", default="build")
    args = ap.parse_args()

    audio, script, plan = map(Path, (args.audio, args.script, args.scene_plan))
    missing = [str(p) for p in (audio, script, plan) if not p.is_file()]
    if missing:
        print("Missing required input(s): " + ", ".join(missing), file=sys.stderr)
        print("Upload the original narration.mp3, exact script.txt and scene_plan.json.")
        raise SystemExit(2)
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("FFmpeg and FFprobe must be installed.")

    info = probe_audio(audio)
    sections = parse_script(script)
    scene_data = json.loads(plan.read_text(encoding="utf-8"))
    if not isinstance(scene_data, list) or len(scene_data) != 11:
        raise SystemExit("scene_plan.json must contain exactly 11 part objects.")
    for i, item in enumerate(scene_data, 1):
        if item.get("part") != i or not item.get("shots"):
            raise SystemExit(f"Part {i}: expected matching part number and non-empty shots.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "project": "AETHRONIX — MARS",
        "target_seconds": TARGET_SECONDS,
        "video": {"width": WIDTH, "height": HEIGHT, "fps": FPS},
        "audio": info,
        "script_parts": [
            {"part": s["part"], "heading": s["heading"], "characters": len(s["text"])}
            for s in sections
        ],
        "status": "INPUTS_VALIDATED — ready for shot timing and final render",
        "audio_policy": "copy original audio; tail-pad only; never time-stretch",
    }
    (out / "production_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
