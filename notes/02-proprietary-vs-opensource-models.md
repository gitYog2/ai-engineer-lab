# 02 — Proprietary vs Open-Source Models (hosted vs self-hosted)

> **Concept #2 of Phase 1.** Grounded in the M6 experiment
> (`experiments/m6_model_comparison.py`): Groq's Llama-3.3-70B vs a self-hosted
> Ollama MedGemma-27B, head-to-head.

---

## 1. It's really TWO decisions, not one

People say "proprietary vs open-source," but two independent axes are hiding in there:

1. **The weights:** closed (GPT, Claude — you can only rent them) vs open (Llama,
   Qwen, Gemma, DeepSeek — you can download and run them).
2. **Where it runs:** a **managed API** (someone else's servers) vs **self-hosted**
   (your own box).

Most combinations exist:
- **closed + hosted** → OpenAI, Anthropic
- **open + hosted** → Groq serving Llama (open weights, *their* fast infra)
- **open + self-hosted** → Ollama on your server

> Key correction to a common myth: "open-source model" ≠ "self-hosted." Groq runs
> an **open** model (Llama) as a **hosted** API. Open weights, someone else's box.

---

## 2. What I Observed (M6)

Same 5 prompts, temperature 0, Groq Llama-70B vs self-hosted Ollama MedGemma-27B:

- **Quality:** near-tie — both got all 5 right (a *medical* 27B model held its own
  on general tasks).
- **Speed:** Groq ~0.3–0.5 s per call. The self-hosted box swung wildly — 1 s up to
  **726 s (12 minutes!)** for a single request, averaging ~179 s.
- **Why:** that server is shared/loaded and I don't control it. The slowness wasn't
  the model's "fault" — it was the *infrastructure*.

**Lesson:** who runs the box determines *reliability*, not just privacy. Managed
APIs give predictable latency + scaling; self-hosting gives control but you own
every ops problem (load, hardware, uptime).

---

## 3. The Trade-off Table

| | Proprietary, hosted (OpenAI/Anthropic) | Open, self-hosted (Ollama) |
|---|---|---|
| Frontier quality | highest | catching up; model-dependent |
| Setup / ops | zero | you run, scale, patch it |
| Latency / reliability | predictable, SLA | your hardware's problem (saw 726 s) |
| Cost model | per token (adds up at scale) | fixed hardware + electricity ($0/token) |
| Data privacy | data leaves your walls | data never leaves ✅ |
| Vendor lock-in | yes | none — swap models freely ✅ |
| Offline / air-gapped | no | yes |
| Rate limits | the provider's | none, but capped by your own capacity |

*(Open + hosted, like Groq, is the middle ground: open weights on fast managed
infra, no ops — but data still leaves and you depend on the vendor.)*

---

## 4. How to Choose (rule of thumb)

- **Default to a hosted API** to move fast — don't run infra you don't need.
- **Self-host when:** data legally can't leave (health/finance/legal — note our test
  model was literally *MedGemma*!), you need offline/air-gapped operation, you're at
  a scale where per-token cost dominates hardware cost, or you must avoid vendor
  lock-in.
- My M6 answer captured two of these: **privacy** and **lock-in freedom**. The run
  itself added a third consideration in the other direction: **reliability/ops cost**.

---

## 5. Self-Test

1. Name a concrete scenario where you'd self-host even though a hosted API is
   faster and cheaper to start with.
2. "Open-source model" and "self-hosted" are not the same thing — explain using Groq.
3. Your self-hosted box answered in 726 s once. What did that reveal about the *real*
   cost of self-hosting?

---

## 6. My Notes & Observations

> (Your space — what clicked, what's still fuzzy.)

-
