# Contributing

Thanks for helping improve Reddit Comment Console.

## Development setup

```bash
git clone https://github.com/Seeking-Leverage/reddit-comment-bot.git
cd reddit-comment-bot

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Add LLM_API_KEY for manual generation tests

./scripts/setup-data.sh

cd web && npm install && cd ..
./scripts/dev.sh
```

- Web UI: http://localhost:5173
- API: http://127.0.0.1:8000

## Project layout

| Path | Purpose |
|------|---------|
| `web/src/pages/` | React UI pages |
| `src/api/` | FastAPI routes and JSON storage |
| `src/bot/` | Comment generation, safety, optional Reddit CLI |
| `tests/` | Smoke and unit tests |

## Before opening a PR

```bash
pytest -q
cd web && npm run build
```

CI runs the same checks on every push to `main`.

## Guidelines

- Keep the human-review workflow — no auto-posting from the web UI
- Document known limitations in README if you defer work
- Match existing code style; small focused PRs preferred
- Never commit `.env`, `data/*.json`, or API keys

## Responsible use

Contributions that encourage spam, ban evasion, or undisclosed promotion will not be merged. See README **Responsible use**.