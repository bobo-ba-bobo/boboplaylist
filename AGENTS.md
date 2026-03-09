# AGENTS.md

## Repository expectations

- Build a local MVP first
- Keep everything simple and readable
- Avoid unnecessary frameworks
- Prefer Python scripts over a large app framework
- Use clear filenames and comments
- Use environment variables for API keys
- Never hardcode secrets
- Keep changes scoped
- Create runnable code, not pseudo-code
- Add a short setup section to README if new dependencies are introduced

## Coding rules

- Python 3.11+
- Use pathlib where reasonable
- Use JSON for lightweight storage
- Use a single config file for tunable settings
- Add basic error handling
- Favor deterministic output where possible
- If image generation is not configured, create a placeholder image flow so the pipeline still runs

## MVP priorities

1. Project structure
2. Config loading
3. Candidate track data model
4. Selection and scoring stub
5. Discovery log generator
6. Cover image creation or placeholder generation
7. Reel renderer with ffmpeg
8. Caption generator
9. End-to-end pipeline command

## Non-goals for now

- No Instagram publishing
- No web dashboard
- No database
- No background job infra
- No copyrighted audio embedding

## Output quality bar

The project should be runnable locally by a non-expert user with a short setup guide.