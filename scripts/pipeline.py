from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from collect_tracks import collect_candidates, filter_by_config
from common import HISTORY_PATH, Track, output_dir_for, save_json, today_str
from generate_caption import build_caption
from generate_cover import generate_cover
from generate_log import build_log
from render_reel import render_reel
from score_tracks import score_and_select


def load_history() -> dict:
    if HISTORY_PATH.exists():
        import json

        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    return {"entries": []}


def save_history(entry: dict) -> None:
    history = load_history()
    entries = history.get("entries", [])
    entries.append(entry)
    history["entries"] = entries[-120:]
    save_json(HISTORY_PATH, history)


def latest_log_count() -> int:
    history = load_history()
    return len(history.get("entries", [])) + 1


def run(date_str: str) -> Path:
    out_dir = output_dir_for(date_str)

    candidates = filter_by_config(collect_candidates())
    if not candidates:
        raise RuntimeError("No candidates after filtering. Check config/settings.json.")

    selected, _scored = score_and_select(candidates)

    log_text, note = build_log(selected, count=latest_log_count())
    cover_path = out_dir / "cover.png"
    reel_path = out_dir / "reel.mp4"
    caption_path = out_dir / "caption.txt"
    metadata_path = out_dir / "metadata.json"

    generate_cover(log_text, cover_path)
    render_reel(cover_path, log_text, reel_path)

    caption = build_caption(selected, note)
    caption_path.write_text(caption, encoding="utf-8")

    metadata = {
        "date": date_str,
        "selected_artist": selected.artist,
        "selected_song": selected.song,
        "monthly_listeners": selected.monthly_listeners,
        "generated_note": note,
        "paths": {
            "reel": str(reel_path),
            "cover": str(cover_path),
            "caption": str(caption_path),
            "metadata": str(metadata_path),
        },
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_json(metadata_path, metadata)

    save_history(
        {
            "date": date_str,
            "artist": selected.artist,
            "song": selected.song,
            "monthly_listeners": selected.monthly_listeners,
            "note": note,
            "output_dir": str(out_dir),
        }
    )
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run boboplaylist MVP pipeline")
    parser.add_argument("--date", default=today_str(), help="YYYY-MM-DD")
    args = parser.parse_args()

    out_dir = run(args.date)
    print(f"Pipeline complete -> {out_dir}")


if __name__ == "__main__":
    main()
