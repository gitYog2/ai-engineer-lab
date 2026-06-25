# 04 — Tokens, Context Windows, Temperature & Cost

> **Concept #4 of Phase 1.** This note backs three milestones:
> **M3 (tokenization)** — done now · **M4 (temperature/sampling)** · **M5 (context + cost)**.
> The tokenization section is complete; the last two sections are stubs we fill
> as we reach M4 and M5.

---

## PART 1 — Tokenization (M3)

### 1. The Concept

A model **never sees your characters or words.** Before anything happens, your
text is split into **tokens** — sub-word chunks from a fixed vocabulary — and
the model only ever reads, reasons over, and predicts *tokens*.

```
"Tokenization"  ->  ["Token", "ization"]      (2 tokens)
"Explain ..."   ->  [id, id, id, ...]          (a list of integers)
```

A token is **~¾ of a word / ~4 characters of English**, on average. It is the
atomic unit of everything that follows: billing, context limits, and latency.

### 2. Why It Exists

Why not feed raw characters or whole words?
- **Whole words** → the vocabulary would be millions of entries and still miss
  new/rare words ("antidisestablishmentarianism", typos, code, emoji).
- **Single characters** → sequences become very long and the model wastes
  capacity relearning that "t-h-e" = "the".
- **Sub-word tokens (BPE)** are the sweet spot: common words are one token,
  rare words split into reusable pieces, and *nothing is ever out-of-vocabulary*
  because the fallback is bytes. Fixed vocab, full coverage.

### 3. How It Works Internally (BPE, briefly)

Byte-Pair Encoding builds the vocab by repeatedly merging the most frequent
adjacent pairs, starting from bytes. Result: frequent strings (" the", "ization")
become single tokens; rare strings stay split. At runtime it greedily matches the
longest known pieces.

**What I saw in the experiment** (`experiments/m3_tokenization.py`):
```
text: "Tokenization isn't magic - it's sub-words!"
pieces: ['Token','ization',' isn',"'t",' magic',' -',' it',"'s",' sub','-','words','!']
```
Two things to burn in:
- **A leading space is part of the token** (`' magic'`, `' it'`). That's why
  prompt formatting/whitespace affects token counts.
- A capitalized/long word splits into sub-words (`'Token'`+`'ization'`).

### 4. What the Numbers Taught Me (observed)

| text | chars | tokens | chars/token | lesson |
|------|------:|-------:|------------:|--------|
| `"Hello, world!"` | 13 | 4 | 3.25 | punctuation = its own tokens |
| `"tokenization"` | 12 | 2 | 6.00 | common word = few tokens |
| `"antidisestablishmentarianism"` | 28 | 6 | 4.67 | rare long word = many pieces |
| `"       "` (spaces) | 7 | 1 | 7.00 | runs of whitespace compress well |
| `"1234567890"` | 10 | 4 | 2.50 | digits chunk in small groups |
| code snippet | 31 | 11 | 2.82 | code is token-dense (symbols, indents) |
| `"नमस्ते दुनिया"` (Hindi) | 13 | 13 | **1.00** | **non-English ≈ 4× the tokens** |

> **Biggest practical takeaway:** the same *meaning* costs wildly different token
> counts depending on language and formatting. Non-English and code are
> token-expensive; plain English is cheap.

### 5. Why Tokens Matter — the "three taxes"

Every token you send or receive is taxed three ways:
1. **Cost** — APIs bill **per token** (input + output, often priced differently).
2. **Context window** — the model can only "see" a fixed number of tokens at once
   (e.g. 8k / 128k / 1M). Your whole prompt + history + answer must fit. (→ M5)
3. **Latency** — more tokens = more compute = slower, especially output tokens,
   which are generated one at a time.

### 6. Estimating Tokens in Practice

- **Rule of thumb:** ~4 chars/token, ~0.75 words/token for English. Halve that
  intuition for non-English or code.
- **Local estimate:** `tiktoken` (OpenAI's tokenizer) — fast, no API call, lets
  you SEE pieces. Great for *budgeting* a prompt before you send it.
- **The billable truth is the API's `usage`.** In the experiment, tiktoken said
  *9 tokens* for the user text, but Groq/Llama reported **`prompt_tokens=48`** —
  because (a) **tokenizers are model-specific** (Llama's vocab ≠ OpenAI's) and
  (b) the API counts the **whole request**: system prompt + chat-template role
  markers, not just your text. Estimate locally; trust `usage` for money.

### 7. Engineering Implications (things I'll actually do)

- Trim system prompts and history — every token is paid for on **every** call.
- Prefer English for instructions where possible; it's cheaper per idea.
- Watch output length (`max_tokens`) — output is generated serially (latency) and
  often costs more per token than input.
- When something is "too long for the model," that's a **token** limit, not a
  character limit (→ retrieval, M7, exists largely to manage this).

---

## PART 2 — Temperature & Sampling (M4)

### 1. The Concept

At each step the model outputs a probability distribution over the next token.
**Temperature decides how we sample from it:**
- `temperature = 0` → always pick the single most-likely token → **deterministic**
  (greedy). Same input → same output.
- higher temperature → flattens the distribution → lower-probability tokens get
  a real chance → **more random / creative / varied**.

(`top_p` / nucleus sampling is a sibling knob: instead of flattening, it samples
only from the smallest set of tokens whose probabilities sum to *p*. Tune one or
the other, not both.)

### 2. What I Observed (`experiments/m4_temperature.py`)

Same prompt ("invent a coffee-shop name") ×4:
- **temp 0.0** → identical every time (Groq: "Brewed Awakening Co." ×4;
  Ollama/MedGemma: "The Daily Grindstone" ×4).
- **temp 1.3** → answers vary run to run.
- **Cross-model bonus:** BOTH providers are deterministic at 0 and varied at 1.3
  — temperature behaves the same regardless of model/vendor.

### 3. When to Use Which (the practical rule)

| Want | Temperature | Examples |
|------|-------------|----------|
| Consistency / correctness | **~0** | extraction, classification, JSON, code, tool-calling, evals |
| Creativity / variety | **~0.7–1.3** | brainstorming, naming, marketing copy, ideas |

> Default instinct: **start at 0 for anything you'll parse or must reproduce**;
> raise it only when you *want* surprise. A flaky pipeline is often just a
> too-high temperature.

### 4. Caveats

- temp 0 is "as deterministic as possible," not a 100% guarantee — batching,
  floating-point, and MoE routing can still cause rare differences.
- Very high temperature (→2) eventually produces incoherent text.

---

## PART 3 — Context Windows & Cost Math (M5)  *(stub — fill in M5)*

> The fixed token budget per request; what happens when you exceed it; how to
> compute the $ cost of a call from `usage` and a price sheet; input vs output
> pricing; why retrieval beats "paste everything".

---

## 8. Self-Test Questions (answer before M4)

1. Why does `"नमस्ते दुनिया"` cost ~4× the tokens of equivalent English?
2. `tiktoken` said 9 tokens but the API said 48 for the "same" prompt. Give the
   **two** independent reasons.
3. You're about to send a 50-page document to an 8k-token model. Why might it
   fail, and which layer of the stack (Concept 01) exists to fix this?
4. Which is usually more expensive and slower to produce: 100 input tokens or
   100 output tokens? Why?
5. True/false: trimming whitespace and a verbose system prompt saves money on
   *every single call*. Explain.

---

## 9. My Notes & Observations

> (Your space — what clicked, what's still fuzzy.)

-
