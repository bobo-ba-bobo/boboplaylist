from __future__ import annotations

import argparse
from pathlib import Path

from common import load_config, pick_fontfile, require_ffmpeg, run_cmd


def compact(text: str, max_lines: int = 10) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\\n".join(lines[:max_lines])


def generate_cover(log_text: str, out_path: Path) -> None:
    cfg = load_config()
    width, height = cfg.get("resolution", "1080x1920").split("x")
    width_i = int(width)
    height_i = int(height)

    require_ffmpeg()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    log_compact = compact(log_text)
    log_for_ffmpeg = log_compact.replace("'", "\\'").replace(":", "\\:")

    fontfile = pick_fontfile()
    drawtext = (
        "drawtext="
        f"fontfile='{fontfile}':" if fontfile else "drawtext="
    )
    drawtext += (
        f"text='{log_for_ffmpeg}':"
        "fontcolor=white:fontsize=42:line_spacing=12:"
        "x=70:y=120:box=1:boxcolor=black@0.35:boxborderw=20"
    )

    vf = (
        f"drawbox=x=0:y=0:w={width_i}:h={height_i}:color=black@1:t=fill,"
        f"drawbox=x=0:y={int(height_i*0.58)}:w={width_i}:h={int(height_i*0.42)}:color=0x1a1a1a@1:t=fill,"
        f"{drawtext}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x0e0e0e:s={width_i}x{height_i}:d=1",
        "-vf",
        "".join(vf),
        "-frames:v",
        "1",
        str(out_path),
    ]

    try:
        run_cmd(cmd, "cover generation failed")
    except RuntimeError:
        fallback = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x0e0e0e:s={width_i}x{height_i}:d=1",
            "-frames:v",
            "1",
            str(out_path),
        ]
        run_cmd(fallback, "cover fallback generation failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate vertical cover image")
    parser.add_argument("--log", default=str(Path("data") / "log.txt"))
    parser.add_argument("--out", default=str(Path("data") / "cover.png"))
    args = parser.parse_args()

    log_text = Path(args.log).read_text(encoding="utf-8")
    generate_cover(log_text, Path(args.out))
    print(f"Generated cover -> {args.out}")


if __name__ == "__main__":
    main()
