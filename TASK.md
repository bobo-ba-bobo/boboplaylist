# TASK.md

Build the first MVP for boboplaylist.

## What to build

Create a local Python project that generates one daily Instagram reel draft for a music discovery account.

## Required scripts

Create these or equivalent:

- scripts/collect_tracks.py
- scripts/score_tracks.py
- scripts/generate_log.py
- scripts/generate_cover.py
- scripts/render_reel.py
- scripts/generate_caption.py
- scripts/pipeline.py

## Required folders

- config/
- data/
- assets/
- scripts/
- output/

## Requirements

### 1. Config
Create a config file for:
- min/max monthly listeners
- reel duration
- resolution
- visual style
- hashtags

### 2. Candidate collection
For MVP, it is okay to support:
- a mock local candidate list
- optional Spotify integration behind env vars

The pipeline must still run even if Spotify credentials are missing.

### 3. Scoring
Implement a basic scoring system using fields like:
- obscurity
- recency or freshness placeholder
- aesthetic fit placeholder
- repeat avoidance based on history

### 4. Discovery log generation
Generate a short minimal discovery log text block.

If no LLM key is configured, use a deterministic template fallback.

### 5. Cover generation
If image generation is configured, generate a vertical cover image.
If not, create a placeholder cover image locally with text.

### 6. Reel rendering
Use ffmpeg to create a silent vertical MP4 with:
- cover image
- text overlay
- subtle zoom or pan
- 6 to 8 second duration

### 7. Caption generation
Generate a short caption and hashtags into caption.txt.

### 8. Metadata
Save metadata.json containing:
- date
- selected artist
- selected song
- monthly listeners
- generated note
- file paths

### 9. History
Save a history file to reduce repeat artist selection.

## Deliverables

- working code
- requirements.txt
- sample .env.example
- setup instructions in README
- example output generated from mock data

## Important

Favor a fully runnable local MVP over ambitious integrations.