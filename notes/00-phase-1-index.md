# Phase 1 — Build My Mental Map of AI Engineering

> **Goal:** Deeply understand the AI application stack and how real AI products are
> built *before* moving into advanced topics. Learn by building, not just reading.

---

## 0. Learner Profile (calibration — 2026-06-17)

- **Python:** Java developer — reads Python fluently but doesn't write it day-to-day. Mentor writes the Python; explains with Java analogies; structures for reuse.
- **LLM APIs:** Brand new (never called one from code)
- **AI concepts:** None yet (theory built from zero)
- **Pace:** Steady — ~1–2 focused hours/day
- **Tooling:** Python, OpenAI API, Anthropic API, Groq API, Claude
- **Principle:** Build everything myself. Every concept must become runnable code.

---

## 1. The 7 Core Concepts (one note each)

| # | Concept | Note file | Status |
|---|---------|-----------|--------|
| 01 | The AI Application Stack | `01-ai-application-stack.md` | 🟡 In progress |
| 02 | Proprietary vs Open-Source Models | `02-proprietary-vs-opensource-models.md` | ⚪ Not started |
| 03 | How AI APIs Work | `03-how-ai-apis-work.md` | ⚪ Not started |
| 04 | Tokenization, Context Windows, Temperature & Cost | `04-tokens-context-temperature-cost.md` | 🟡 In progress (Part 1 tokenization done) |
| 05 | Retrieval & Embeddings (conceptual) | `05-retrieval-and-embeddings.md` | ⚪ Not started |
| 06 | Orchestration Frameworks (conceptual) | `06-orchestration-frameworks.md` | ⚪ Not started |
| 07 | AI Product Architecture (reverse engineering) | `07-ai-product-architecture.md` | ⚪ Not started |

Legend: ⚪ Not started · 🟡 In progress · 🟢 Done

---

## 2. Milestone Tracker (the execution path)

| M | Milestone | Concept(s) | Deliverable | Status |
|---|-----------|-----------|-------------|--------|
| M1 | Environment + first API call | 01, 03 | One working live call to a provider (Groq) | 🟢 Done (2026-06-18) |
| M2 | Multi-provider integration | 02, 03 | Clean OpenAI + Anthropic + Groq calls, one pattern | 🟢 Done (2026-06-25) — `llm.py` one-pattern abstraction; Groq + novarelay(→Claude) wired & proven; paid providers gated only by $0 account balance |
| M3 | Tokenization deep-dive | 04 | Token-counting experiments | 🟡 Current |
| M4 | Sampling controls | 04 | Temperature / top_p experiments | ⚪ |
| M5 | Context windows + cost | 04 | Context-limit experiments + cost math | ⚪ |
| M6 | Model comparison | 02, 04 | Quality/speed/cost comparison across providers | ⚪ |
| M7 | Retrieval & embeddings | 05 | Tiny embeddings + similarity-search experiment | ⚪ |
| M8 | Orchestration frameworks | 06 | Conceptual map + "when NOT to use a framework" note | ⚪ |
| M9 | Product reverse-engineering | 07 | Architecture teardowns of 7 real products | ⚪ |
| M10 | Phase 1 capstone | all | Small multi-provider mini-app + synthesized mental map | ⚪ |

---

## 3. Practical Deliverables Checklist

- [x] API integrations: **Groq ✅ live (free)** · OpenAI + Anthropic + **novarelay→Claude** adapters built via one pattern (`llm.py`); paid ones gated only by account balance
- [ ] Model comparison experiments
- [~] Token counting experiments (M3 — in progress)
- [ ] Temperature experiments
- [ ] Context window experiments
- [ ] AI product reverse-engineering exercises
- [ ] Personal notes & observations (this folder)

---

## 4. Progress

**Phase 1 completion: ~25%** (M1 + M2 done. M2: `llm.py` Strategy/Adapter — one `chat()` over Groq + OpenAI + Anthropic + novarelay; Groq live (free); novarelay reaches Claude Opus 4.8 via the OpenAI dialect, blocked only by $0 balance. Now on M3 — tokenization.)

---

## 5. Open Questions / Things I Don't Understand Yet

> (I'll keep adding to this as we go. Honesty here is what makes the mentorship work.)

- 

---

## 6. Session Log

| Date | Focus | Outcome |
|------|-------|---------|
| 2026-06-17 | Assessment + Concept 01 + Milestone 1 | Workspace created; first task assigned |
| 2026-06-18 | Ran Milestone 1 (live Groq call) | ✅ First live LLM call. 170 tokens (61 prompt + 109 completion). Model round-trip ~0.1–0.6 s. M1 complete; M2 unlocked. |
| 2026-06-24 | M2 abstraction (multi-provider) | ✅ Built `llm.py` (Strategy/Adapter: `ChatResult` + `LLMProvider` + Groq/OpenAI/Anthropic + `get_provider` factory) and `m2_multi_provider.py`. `config.py` grew `openai_api_key()`, `anthropic_api_key()`, `available_providers()`. Installed `openai` 2.43.0 + `anthropic` 0.111.0. Ran it: Groq path verified (147 tokens, ~1.6 s). OpenAI/Anthropic adapters coded but key-gated. |
| 2026-06-25 | M2 close-out + debugging | ✅ Pushed code (repo made public). Added `NovaRelayProvider` (novarelay.io OpenAI-compatible relay → Claude Opus 4.8) + custom User-Agent to pass its Cloudflare filter; UTF-8 console fix. Debugged 4 distinct failure modes: wrong key, OpenAI `429 insufficient_quota`, novarelay `403 insufficient_user_quota` ($0 balance), Cloudflare UA block. Decision: **stay Groq-only (free); M2 done.** Starting M3 (tokenization). |
