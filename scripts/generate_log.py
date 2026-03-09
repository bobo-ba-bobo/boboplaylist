from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

from common import ROOT, Track, dict_to_track, load_env_file, load_json

NOTES = [
    "feels like neon rain on an empty street",
    "sounds like the city after the last train",
    "quiet but dangerous in the right headphones",
    "the kind of track that appears at 1:43am",
    "minimal and cinematic, no wasted movement",
]


def deterministic_note(track: Track) -> str:
    seed = f"{track.artist}|{track.song}"
    idx = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16) % len(NOTES)
    return NOTES[idx]


def build_log(track: Track, count: int = 1, found_source: str = "spotify radio") -> tuple[str, str]:
    load_env_file(ROOT / ".env")
    _llm_configured = bool(os.getenv("OPENAI_API_KEY"))

    note = deterministic_note(track)
    clock_time = track.discovered_at[11:16] if track.discovered_at else "01:43"

    text = (
        f"discovery log #{count:03d}\n\n"
        f"found:\n{found_source}\n\n"
        f"time:\n{clock_time}\n\n"
        f"artist:\n{track.artist}\n\n"
        f"song:\n{track.song}\n\n"
        f"monthly listeners:\n{track.monthly_listeners:,}\n\n"
        f"note:\n{note}"
    )
    return text, note


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate discovery log")
    parser.add_argument("--in", dest="in_path", default=str(Path("data") / "selected.json"))
    parser.add_argument("--out", default=str(Path("data") / "log.txt"))
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    selected = load_json(Path(args.in_path), {})
    track = dict_to_track(selected)
    log_text, _note = build_log(track, args.count)
    Path(args.out).write_text(log_text, encoding="utf-8")
    print(f"Generated log -> {args.out}")


if __name__ == "__main__":
    main()
