from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path

from common import (
    MOCK_CANDIDATES_PATH,
    ROOT,
    Track,
    dict_to_track,
    load_config,
    load_env_file,
    load_json,
    save_json,
    track_to_dict,
)


def collect_candidates() -> list[Track]:
    """
    MVP collection:
    - If Spotify env vars exist, this is where integration would run.
    - Always falls back to local mock candidates to keep the pipeline runnable.
    """
    load_env_file(ROOT / ".env")
    _spotify_enabled = bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"))

    mock_data = load_json(MOCK_CANDIDATES_PATH, [])
    tracks = [dict_to_track(item) for item in mock_data]

    now_iso = datetime.now().isoformat(timespec="seconds")
    for track in tracks:
        if not track.discovered_at:
            track.discovered_at = now_iso
    return tracks


def filter_by_config(tracks: list[Track]) -> list[Track]:
    cfg = load_config()
    min_l = int(cfg.get("min_monthly_listeners", 0))
    max_l = int(cfg.get("max_monthly_listeners", 10**9))
    return [t for t in tracks if min_l <= t.monthly_listeners <= max_l]


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect candidate tracks")
    parser.add_argument("--out", default=str(Path("data") / "candidates.json"))
    args = parser.parse_args()

    tracks = filter_by_config(collect_candidates())
    save_json(Path(args.out), [track_to_dict(t) for t in tracks])
    print(f"Collected {len(tracks)} candidate tracks -> {args.out}")


if __name__ == "__main__":
    main()
