# boboplaylist MVP

Local Python MVP that generates one daily Instagram reel draft for a music discovery account.

## What it produces

For each run date (`output/YYYY-MM-DD/`):

- `reel.mp4` (1080x1920, silent, subtle zoom)
- `cover.png`
- `caption.txt`
- `metadata.json`

## Project structure

- `config/settings.json` - tunable pipeline settings
- `data/mock_candidates.json` - mock candidate tracks
- `data/history.json` - repeat-avoidance history
- `scripts/` - modular pipeline scripts
- `output/` - generated daily outputs

## Requirements

- Python 3.11+
- `ffmpeg` on PATH

Install `ffmpeg` on macOS:

```bash
brew install ffmpeg
```

## Setup

```bash
cp .env.example .env
```

No API keys are required for MVP. The pipeline uses deterministic local fallbacks.

## Run end-to-end pipeline

```bash
python3 scripts/pipeline.py
```

Optional date override:

```bash
python3 scripts/pipeline.py --date 2026-03-09
```

## Run scripts individually

```bash
python3 scripts/collect_tracks.py
python3 scripts/score_tracks.py
python3 scripts/generate_log.py
python3 scripts/generate_cover.py
python3 scripts/render_reel.py
python3 scripts/generate_caption.py
```

## Notes

- No Instagram publishing in MVP.
- No copyrighted audio embedding.
- If optional API keys are missing, the pipeline still runs from mock data.
- Candidate filtering defaults to tracks marked as available on both YouTube Music and Instagram music.
