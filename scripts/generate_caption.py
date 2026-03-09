from __future__ import annotations

import argparse
from pathlib import Path

from common import Track, dict_to_track, load_config, load_json


def build_caption(track: Track, note: str) -> str:
    cfg = load_config()
    tags = cfg.get("hashtags", [])
    hashtag_line = " ".join(tags)
    return (
        f"found this at night: {track.artist} - {track.song}\n"
        f"{note}\n\n"
        f"{hashtag_line}".strip()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate caption")
    parser.add_argument("--selected", default=str(Path("data") / "selected.json"))
    parser.add_argument("--note", default="")
    parser.add_argument("--out", default=str(Path("data") / "caption.txt"))
    args = parser.parse_args()

    track = dict_to_track(load_json(Path(args.selected), {}))
    note = args.note or "new late-night find"
    caption = build_caption(track, note)

    Path(args.out).write_text(caption, encoding="utf-8")
    print(f"Generated caption -> {args.out}")


if __name__ == "__main__":
    main()
