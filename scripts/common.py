from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "settings.json"
MOCK_CANDIDATES_PATH = ROOT / "data" / "mock_candidates.json"
HISTORY_PATH = ROOT / "data" / "history.json"


@dataclass
class Track:
    artist: str
    song: str
    monthly_listeners: int
    source: str = "mock"
    discovered_at: str = ""


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)


def load_config() -> dict[str, Any]:
    return load_json(CONFIG_PATH, {})


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_clock() -> str:
    return datetime.now().strftime("%I:%M%p").lower()


def output_dir_for(date_str: str) -> Path:
    out = ROOT / "output" / date_str
    out.mkdir(parents=True, exist_ok=True)
    return out


def track_to_dict(track: Track) -> dict[str, Any]:
    return asdict(track)


def dict_to_track(data: dict[str, Any]) -> Track:
    return Track(
        artist=str(data.get("artist", "Unknown Artist")),
        song=str(data.get("song", "Unknown Song")),
        monthly_listeners=int(data.get("monthly_listeners", 0)),
        source=str(data.get("source", "mock")),
        discovered_at=str(data.get("discovered_at", "")),
    )


def require_ffmpeg() -> None:
    result = subprocess.run(
        ["ffmpeg", "-version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "ffmpeg was not found. Install ffmpeg first (e.g. `brew install ffmpeg`)."
        )


def font_candidates() -> list[Path]:
    return [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Helvetica.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]


def pick_fontfile() -> str:
    for candidate in font_candidates():
        if candidate.exists():
            return str(candidate)
    return ""


def run_cmd(cmd: list[str], error_context: str) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"{error_context}: {message}")
