# Reddit Comment Bot

Operator console + CLI for Reddit engagement. **Clone one repo per client** — fill in brand, playbooks, and credentials locally.

## What's included

| Layer | Purpose |
|-------|---------|
| **Web console** (`web/`) | Generator, brand profile, playbooks, campaign tracker |
| **API** (`src/api/`) | FastAPI backend, JSON storage in `data/` |
| **CLI** (`src/bot/`) | Optional automated scan + dry-run/post via Reddit API |

## Quick start

### 1. Python API

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# Set LLM_API_KEY (any OpenAI-compatible provider)

reddit-api
# API → http://127.0.0.1:8000
```

### 2. Web console

**Dev (hot reload) — run both:**
```bash
./scripts/dev.sh
# UI → http://localhost:5173  ← open this URL
# API → http://127.0.0.1:8000  (backend only, not the UI)
```

Or manually:
```bash
reddit-api          # terminal 1
cd web && npm run dev   # terminal 2 → http://localhost:5173
```

**Single URL (after build):**
```bash
cd web && npm run build
reddit-api
# UI + API → http://127.0.0.1:8000
```

### 3. Workflow

1. **Brand** — product, company, expertise, campaign goals
2. **Playbooks** — per-subreddit tone, angles, dos/donts
3. **Generator** — paste a Reddit post → generate → edit → copy → post manually
4. **Tracker** — log impressions, installs, upvotes vs goals

Data is stored in `data/*.json` (one repo = one client).

## CLI (optional automation)

```bash
cp config/clients/example-client.yaml config/clients/client.yaml
reddit-bot validate client
reddit-bot run client          # dry run
reddit-bot run client --live
```

## Project structure

```
web/                 React console (Vite)
src/api/             FastAPI routes + JSON storage
src/bot/             Reddit scanner + CLI
data/                brand.json, playbooks.json, history.json, tracker.json
config/clients/      YAML for CLI automation only
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET/PUT | `/api/brand` | Brand profile |
| GET/PUT | `/api/playbooks` | Subreddit playbooks |
| POST | `/api/generate-comment` | Generate comment draft |
| GET/POST | `/api/history` | Comment history |
| GET | `/api/tracker` | Tracker summary |
| PUT | `/api/tracker/goals` | Campaign goals |
| POST | `/api/tracker/entries` | Log metrics |

## LLM providers

Uses the OpenAI Python SDK against any **OpenAI-compatible** chat API. Configure via `.env`:

| Provider | `LLM_BASE_URL` | Example `LLM_MODEL` |
|----------|----------------|---------------------|
| OpenAI | *(unset)* | `gpt-4o-mini` |
| OpenRouter | `https://openrouter.ai/api/v1` | `anthropic/claude-3-5-haiku` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Azure OpenAI | your deployment URL | your deployment name |

`OPENAI_*` env vars still work for older clones.

## New client setup

```bash
git clone <this-repo> client-acme
cd client-acme
# Fill .env, run API + web, configure brand + playbooks in UI
```