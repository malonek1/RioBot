# RioBot

Discord bot for the Project Rio (Mario Superstar Baseball) community: matchmaking
queues, stat lookups, ladders, and assorted randomizer/utility commands.

Code lives under `main/`. Run from there (`python RioBot.py`).

## Layout

- `cogs/` — discord.py `commands.Cog` modules; one feature area each. Listed in
  `RioBot.py`'s `cog_files` and loaded via `load_extension`.
- `services/` — stateless helpers cogs call (embeds, randomness, images).
- `helpers/` — lower-level calculation/building logic (stat calcs, team builder).
- `models/` — Pydantic models, grouped by feature (e.g. `matchmaking.py` holds
  `QueuedPlayer` + `MatchAnnouncement`).
- `resources/` — config + data loaded at import (`ladders`, `characters`,
  `EnvironmentVariables`).

## Naming conventions

- **Functions and variables: `snake_case`.** No Hungarian prefixes. (Older code
  used `rf*`/`if*` prefixes and camelCase — these are being migrated to
  snake_case opportunistically when a file is edited, not in a big-bang pass.)
- **Modules: lowercase, feature-named, no redundant `_functions` suffix.** A
  feature is sliced across layer directories by repeating the name — e.g.
  `cogs/matchmaking.py`, `models/matchmaking.py`, `services/matchmaking_embeds.py`.
  The directory disambiguates the role.
- **Classes: `PascalCase`.**
- **Module-level constants: `UPPER_SNAKE_CASE`.**
- Prefer explicit imports over `from x import *` in new/edited code.

## Config & secrets

- Non-secret config: `resources/prod.json` (committed, live) or
  `resources/test.json` (local dev, gitignored, shadows prod when present).
  Read via `EnvironmentVariables`. New keys should use `.get(...)` with a
  fallback so a stale prod config can't crash boot.
- Secrets (`BOT_TOKEN`, `RIO_KEY`): `.env_PROD` via dotenv, deployed manually to
  prod. Never log secret values.

## Logging

Use the `logging` module (`logger = logging.getLogger(__name__)`), not `print`.
The root logger is configured by `bot.run(..., root_logger=True)` in `RioBot.py`.

## External data

Ladder/stat data comes from the Project Rio API (`https://api.projectrio.app`).
`resources/ladders.py` fetches game modes at import (with startup retries) and
refreshes ladders on a loop.

## Development

Runtime deps live in `requirements.txt`; dev-only tooling (ruff, pytest) lives in
`requirements-dev.txt` and is never installed on the bot runtime. Install both
locally with `pip install -r requirements.txt -r requirements-dev.txt`.

- **Lint/format:** `ruff check .` and `ruff format .`. Config is in
  `pyproject.toml`. CI enforces `ruff check` on every PR.
- **Tests:** `pytest` from the repo root. Tests live in `tests/` (outside `main/`,
  so they don't ship to prod) and import app modules via the `pythonpath = ["main"]`
  setting in `pyproject.toml`. CI runs the suite on every PR.
- Tests cover pure logic (stat calcs, sorting, model validation) and stay offline.
  Modules that hit the Project Rio API or Discord at import (`resources/ladders.py`,
  the cogs) are intentionally untested for now — they'd need mocking.
