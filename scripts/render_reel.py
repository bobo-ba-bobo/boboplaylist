from __future__ import annotations

import argparse
from pathlib import Path

from common import load_config, require_ffmpeg, run_cmd


def render_reel(cover_path: Path, log_text: str, reel_path: Path) -> None:
    cfg = load_config()
    duration = float(cfg.get("reel_duration_seconds", 7))
    width, height = cfg.get("resolution", "1080x1920").split("x")
    width_i = int(width)
    height_i = int(height)

    require_ffmpeg()
    reel_path.parent.mkdir(parents=True, exist_ok=True)

    overlay_text = "\\n".join([ln.strip() for ln in log_text.splitlines() if ln.strip()][:9])
    overlay_text = overlay_text.replace("'", "\\'").replace(":", "\\:")

    vf = (
        f"scale={width_i}:{height_i},"
        f"zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width_i}x{height_i}:fps=30,"
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=40:line_spacing=10:"
        "x=60:y=h-th-140:box=1:boxcolor=black@0.35:boxborderw=24"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(cover_path),
        "-vf",
        vf,
        "-t",
        str(duration),
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(reel_path),
    ]

    try:
        run_cmd(cmd, "reel render failed")
    except RuntimeError:
        fallback_vf = (
            f"scale={width_i}:{height_i},"
            f"zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width_i}x{height_i}:fps=30"
        )
        fallback = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(cover_path),
            "-vf",
            fallback_vf,
            "-t",
            str(duration),
            "-r",
            "30",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(reel_path),
        ]
        run_cmd(fallback, "reel fallback render failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render silent vertical reel")
    parser.add_argument("--cover", default=str(Path("data") / "cover.png"))
    parser.add_argument("--log", default=str(Path("data") / "log.txt"))
    parser.add_argument("--out", default=str(Path("data") / "reel.mp4"))
    args = parser.parse_args()

    log_text = Path(args.log).read_text(encoding="utf-8")
    render_reel(Path(args.cover), log_text, Path(args.out))
    print(f"Rendered reel -> {args.out}")


if __name__ == "__main__":
    main()
