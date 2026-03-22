#!/usr/bin/env python3
"""
make_reel.py

Drop files into ClipGrab/ and run:

  Photos (jpg/png/webp)  →  slideshow reel ~1 min, blur top/bottom, text
  Video  (mp4/mov/etc.)  →  9:16 blur treatment + text overlay, trimmed to 1 min

Usage:
    python3 scripts/make_reel.py --artist "The Pharcyde" --song "Y" --release "1995"
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

ROOT     = Path(__file__).resolve().parent.parent
CLIPGRAB = ROOT / "ClipGrab"
OUTPUT   = ROOT / "output"

FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FONT   = "/System/Library/Fonts/Helvetica.ttc"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}

REEL_W, REEL_H = 1080, 1920
TARGET_SECS    = 60
TRANSITION     = 1       # seconds for crossfade between photos
FPS            = 24

TRANSITIONS = [
    "fade", "fadeblack", "dissolve",
    "wipeleft", "wiperight",
    "zoomin", "horzopen", "horzclose",
    "circleopen", "circleclose",
]


# ── helpers ───────────────────────────────────────────────────────────────────

def scan_clipgrab() -> tuple[list[Path], list[Path]]:
    CLIPGRAB.mkdir(exist_ok=True)
    files  = [f for f in CLIPGRAB.iterdir() if f.is_file() and not f.name.startswith(".")]
    photos = sorted([f for f in files if f.suffix.lower() in IMAGE_EXTS], key=lambda f: f.name)
    videos = sorted([f for f in files if f.suffix.lower() in VIDEO_EXTS], key=lambda f: f.name)
    return photos, videos


def composite_photo(img_path: Path, out_path: Path):
    """Blur-filled 9:16 canvas with the original photo centered on top."""
    img = Image.open(img_path).convert("RGB")

    # background: scale to fill, blur, darken
    bg_scale = max(REEL_W / img.width, REEL_H / img.height)
    bg = img.resize((int(img.width * bg_scale), int(img.height * bg_scale)), Image.LANCZOS)
    bx, by = (bg.width - REEL_W) // 2, (bg.height - REEL_H) // 2
    bg = bg.crop((bx, by, bx + REEL_W, by + REEL_H))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)

    # foreground: scale to fit inside frame
    fg_scale = min(REEL_W / img.width, REEL_H / img.height)
    fg = img.resize((int(img.width * fg_scale), int(img.height * fg_scale)), Image.LANCZOS)

    canvas = bg.copy()
    canvas.paste(fg, ((REEL_W - fg.width) // 2, (REEL_H - fg.height) // 2))
    canvas = ImageEnhance.Color(canvas).enhance(0.85)
    canvas = ImageEnhance.Contrast(canvas).enhance(1.08)
    canvas.save(out_path, "JPEG", quality=95)


def text_overlay_filters(text_files: dict) -> str:
    """Return comma-chained drawtext filters for song / artist / release."""
    parts = []

    def dt(key, size, alpha, y_from_bottom):
        if key not in text_files:
            return None
        return (
            f"drawtext=textfile={text_files[key]}"
            f":fontfile={FONT}:fontsize={size}"
            f":fontcolor=white@{alpha}:borderw=2:bordercolor=black@0.45"
            f":x=60:y=h-{y_from_bottom}"
        )

    for f in [dt("song", 82, 1.0, 400), dt("artist", 46, 0.9, 300), dt("release", 32, 0.65, 244)]:
        if f:
            parts.append(f)
    return ",".join(parts)


# ── photo slideshow mode ──────────────────────────────────────────────────────

def render_photos(frames: list[Path], text_files: dict, output_path: Path):
    n = len(frames)

    # spread photos to fill TARGET_SECS
    # total = n * dur - (n-1) * TRANSITION  →  dur = (TARGET + (n-1)*T) / n
    clip_dur = (TARGET_SECS + (n - 1) * TRANSITION) / n
    clip_f   = int(clip_dur * FPS)

    inputs = []
    for f in frames:
        inputs += ["-loop", "1", "-t", str(clip_dur + TRANSITION), "-i", str(f)]

    parts = []

    # Ken Burns: slow zoom-in per photo
    zoom = "if(eq(on\\,1)\\,1\\,min(zoom+0.0008\\,1.12))"
    for i in range(n):
        parts.append(
            f"[{i}:v]zoompan=z='{zoom}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
            f":d={clip_f}:s={REEL_W}x{REEL_H}:fps={FPS}[z{i}]"
        )

    # xfade chain
    last = "z0"
    for i in range(n - 1):
        trans  = TRANSITIONS[i % len(TRANSITIONS)]
        offset = (i + 1) * (clip_dur - TRANSITION)
        src    = "z0" if i == 0 else f"xf{i-1}"
        parts.append(
            f"[{src}][z{i+1}]xfade=transition={trans}:duration={TRANSITION}:offset={offset:.3f}[xf{i}]"
        )
        last = f"xf{i}"

    # grade + text
    overlay = text_overlay_filters(text_files)
    parts.append(f"[{last}]eq=saturation=0.88:contrast=1.05,{overlay}[out]")

    cmd = [FFMPEG, "-y"] + inputs + [
        "-filter_complex", ";".join(parts),
        "-map", "[out]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-r", str(FPS), "-movflags", "+faststart",
        str(output_path),
    ]
    _run(cmd)


# ── video mode ────────────────────────────────────────────────────────────────

def render_video(video: Path, text_files: dict, output_path: Path):
    overlay = text_overlay_filters(text_files)

    vf = (
        "split=2[orig][blur];"
        "[blur]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=20:3[bg];"
        "[orig]scale=1080:-2[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        f"eq=saturation=0.88:contrast=1.05,{overlay}[out]"
    )

    cmd = [
        FFMPEG, "-y",
        "-i", str(video),
        "-t", str(TARGET_SECS),
        "-vf", vf,
        "-map", "0:v", "-map", "0:a?",   # keep audio if present
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    _run(cmd)


def _run(cmd: list):
    print("Rendering reel...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr[-4000:])
        sys.exit("ffmpeg render failed.")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artist",  required=True)
    parser.add_argument("--song",    required=True)
    parser.add_argument("--release", default="", help="Release date or year")
    args = parser.parse_args()

    photos, videos = scan_clipgrab()

    if not photos and not videos:
        sys.exit("Nothing found in ClipGrab/.\nAdd photos or a video and run again.")

    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir  = OUTPUT / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    # write text files (avoids ffmpeg special-char escaping)
    text_files: dict = {}
    for key, val in [("song", args.song), ("artist", args.artist), ("release", args.release)]:
        if val:
            tf = out_dir / f"text_{key}.txt"
            tf.write_text(val, encoding="utf-8")
            text_files[key] = tf

    output_video = out_dir / "reel.mp4"

    # ── photo mode ────────────────────────────────────────────────────────────
    if photos:
        print(f"Photo mode — {len(photos)} photo(s): {[p.name for p in photos]}")
        frames = []
        for i, photo in enumerate(photos):
            dest = out_dir / f"frame_{i:03d}.jpg"
            print(f"  Compositing {photo.name}...")
            composite_photo(photo, dest)
            frames.append(dest)
        render_photos(frames, text_files, output_video)

    # ── video mode ────────────────────────────────────────────────────────────
    else:
        video = videos[0]
        print(f"Video mode — {video.name}")
        render_video(video, text_files, output_video)

    meta = {
        "artist": args.artist, "song": args.song, "release": args.release,
        "mode":   "photos" if photos else "video",
        "inputs": [p.name for p in (photos or videos)],
        "date":   date_str, "output": str(output_video),
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"\nDone → {output_video}")


if __name__ == "__main__":
    main()
