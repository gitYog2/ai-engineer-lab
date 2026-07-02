# AI Engineer Roadmap

A self-directed, **build-first** journey into AI engineering: every concept is
turned into small, runnable Python. Coming from a Java background, the goal is
deep understanding of how real AI products work — one milestone, one experiment
at a time.

> **Phase 1 — Build the Mental Map of AI Engineering.** Progress: **~52%
> (Milestones M1–M6 done).**

---

## What's inside

| Area | Where |
|------|-------|
| Concept notes (one per topic) | [`notes/`](notes/) |
| Runnable experiments (one per milestone) | [`experiments/`](experiments/) |
| Progress tracker / dashboard | [`notes/00-phase-1-index.md`](notes/00-phase-1-index.md) |
| Resume/handover for future sessions | [`notes/HANDOVER.md`](notes/HANDOVER.md) |

---

## Milestones

| # | Milestone | Experiment | Status |
|---|-----------|-----------|--------|
| M1 | Environment + first live API call | `experiments/m1_first_api_call.py` | ✅ |
| M2 | Multi-provider abstraction (one interface, many models) | `experiments/llm.py`, `m2_multi_provider.py` | ✅ |
| M3 | Tokenization (see & count tokens) | `experiments/m3_tokenization.py` | ✅ |
| M4 | Temperature / sampling | `experiments/m4_temperature.py` | ✅ |
| M5 | Context windows + cost math | `experiments/m5_context_and_cost.py` | ✅ |
| M6 | Model comparison (head-to-head) | `experiments/m6_model_comparison.py` | ✅ |
| M7 | Retrieval & embeddings | _next_ | ⬜ |
| M8 | Orchestration frameworks (concept) | — | ⬜ |
| M9 | AI product reverse-engineering | — | ⬜ |
| M10 | Phase-1 capstone (mini app) | — | ⬜ |

---

## Setup

Windows (PowerShell), from the repo root:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r experiments\requirements.txt
Copy-Item experiments\.env.example .env
```

Then open `.env` and add a key for at least one provider (free **Groq** is the
easiest — get one at https://console.groq.com). `.env` is git-ignored; secrets
are never committed.

Run any experiment:

```powershell
python experiments\m6_model_comparison.py
```

---

## Providers

All providers are reached through **one uniform `chat()` interface**
(`experiments/llm.py`). A provider "turns on" simply when its key (or base URL)
is present in `.env` — no code changes.

| Provider | Key in `.env` | Notes |
|----------|---------------|-------|
| **Groq** | `GROQ_API_KEY` | Free tier, fast, OpenAI-compatible. The default workhorse. |
| **Ollama** (local/remote) | `OLLAMA_BASE_URL` | Self-hosted open models via an OpenAI-compatible API. No API key. |
| **OpenAI** | `OPENAI_API_KEY` | Needs billing/credits. |
| **Anthropic** | `ANTHROPIC_API_KEY` | Direct Claude API (a Claude Pro subscription does **not** provide an API key). |
| **NovaRelay** | `NOVARELAY_API_KEY` | OpenAI-compatible relay that fronts Claude/GPT/Gemini via one key. |

---

## What each experiment teaches

- **M1 — first call:** the shape of every chat request (`messages`, roles),
  token usage, error handling.
- **M2 — abstraction:** the Strategy/Adapter pattern — Groq/OpenAI/NovaRelay/Ollama
  share one "OpenAI-compatible" adapter; Anthropic has its own dialect.
- **M3 — tokenization:** models read **tokens**, not characters; non-English text
  and code cost far more tokens.
- **M4 — temperature:** `temperature = 0` is deterministic (extraction, code);
  higher is creative (brainstorming).
- **M5 — context + cost:** the fixed token budget per request, and how `usage`
  becomes dollars (model choice = ~100× cost swings).
- **M6 — comparison:** the same prompts across models — speed vs quality vs the
  reliability trade-offs of self-hosting.

---

## Concept notes

- [`01` — The AI Application Stack](notes/01-ai-application-stack.md)
- [`02` — Proprietary vs Open-Source Models](notes/02-proprietary-vs-opensource-models.md)
- [`04` — Tokens, Context, Temperature & Cost](notes/04-tokens-context-temperature-cost.md)

---

## Tech

Python 3.14 · `groq` · `openai` · `anthropic` · `tiktoken` · `python-dotenv`.

_This is a learning repo — code favors clarity and heavy comments over cleverness.
Any pricing figures in the experiments are illustrative; check provider pages for
current rates._
