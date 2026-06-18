# Experiments

Runnable code for each milestone. One folder or file per experiment, named by milestone.

## Conventions (production habits from day one)

- **Never hardcode API keys.** Use a `.env` file (git-ignored) + `python-dotenv`.
- One virtual environment for the whole roadmap: `.venv/`
- Each experiment prints: the input, the output, and any usage/metadata (tokens, latency).
- Keep a short "Observations" comment at the bottom of each script.

## Index

| Milestone | File | What it does |
|-----------|------|--------------|
| M1 | `m1_first_api_call.py` | First live LLM API call (Groq) |

## Setup (do once)

```bash
# from the roadmap root
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
pip install groq python-dotenv
```

Create a `.env` file (this file must NOT be committed):

```
GROQ_API_KEY=your_key_here
```
