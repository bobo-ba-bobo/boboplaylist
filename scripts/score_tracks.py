from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from common import HISTORY_PATH, Track, dict_to_track, load_config, load_json, save_json, track_to_dict


def stable_unit(*parts: str) -> float:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def recent_artists(history: dict[str, Any], lookback: int = 7) -> set[str]:
    items = history.get("entries", [])
    tail = items[-lookback:]
    return {str(item.get("artist", "")).lower() for item in tail}


def score_track(track: Track, min_l: int, max_l: int, recent: set[str]) -> dict[str, float]:
    span = max(max_l - min_l, 1)
    obscurity = 1.0 - ((track.monthly_listeners - min_l) / span)
    obscurity = max(0.0, min(1.0, obscurity))

    freshness = stable_unit(track.artist, track.song, "freshness")
    aesthetic = stable_unit(track.artist, track.song, "aesthetic")
    repeat_penalty = 0.45 if track.artist.lower() in recent else 0.0

    total = (0.55 * obscurity) + (0.25 * freshness) + (0.20 * aesthetic) - repeat_penalty
    return {
        "obscurity": round(obscurity, 4),
        "freshness": round(freshness, 4),
        "aesthetic": round(aesthetic, 4),
        "repeat_penalty": round(repeat_penalty, 4),
        "total": round(total, 4),
    }


def score_and_select(tracks: list[Track]) -> tuple[Track, list[dict[str, Any]]]:
    cfg = load_config()
    min_l = int(cfg.get("min_monthly_listeners", 0))
    max_l = int(cfg.get("max_monthly_listeners", 10**9))
    history = load_json(HISTORY_PATH, {"entries": []})
    recent = recent_artists(history)

    scored: list[dict[str, Any]] = []
    for track in tracks:
        score = score_track(track, min_l, max_l, recent)
        scored.append({"track": track_to_dict(track), "score": score})

    scored.sort(key=lambda x: x["score"]["total"], reverse=True)
    selected = dict_to_track(scored[0]["track"])
    return selected, scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Score and select one track")
    parser.add_argument("--in", dest="in_path", default=str(Path("data") / "candidates.json"))
    parser.add_argument("--out", default=str(Path("data") / "selected.json"))
    parser.add_argument("--scored", default=str(Path("data") / "scored_tracks.json"))
    args = parser.parse_args()

    raw_tracks = load_json(Path(args.in_path), [])
    tracks = [dict_to_track(item) for item in raw_tracks]
    if not tracks:
        raise RuntimeError("No candidates found. Run collect_tracks first.")

    selected, scored = score_and_select(tracks)
    save_json(Path(args.out), track_to_dict(selected))
    save_json(Path(args.scored), scored)
    print(f"Selected: {selected.artist} - {selected.song}")


if __name__ == "__main__":
    main()
