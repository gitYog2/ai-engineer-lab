# 01 — The AI Application Stack

> **Concept #1 of Phase 1.** This is the mental map everything else hangs on.
> When you understand these four layers and how data flows through them, every
> AI product you'll ever look at becomes "oh, it's just *this* arrangement of the stack."

---

## 1. The Concept

Almost every real AI product is built from **four layers** stacked on top of each other.
Data (a user's request) flows **down** the stack and a result flows **back up**.

```
┌─────────────────────────────────────────────────────────┐
│  4. APPLICATION LAYER   (what the user touches)          │
│     Frontend · Backend · APIs · Auth · Product logic     │
├─────────────────────────────────────────────────────────┤
│  3. ORCHESTRATION LAYER (the "brain wiring")             │
│     Prompt assembly · Chains · Agents · Tools · Memory   │
├─────────────────────────────────────────────────────────┤
│  2. RETRIEVAL LAYER     (giving the model knowledge)     │
│     Embeddings · Vector DB · Search · Re-ranking         │
├─────────────────────────────────────────────────────────┤
│  1. MODEL LAYER         (the raw intelligence)           │
│     OpenAI · Anthropic · Gemini · Groq · Open-source     │
└─────────────────────────────────────────────────────────┘
```

**One-line definition of each layer:**

1. **Model Layer** — the raw reasoning/generation engine (the LLM itself). It takes text in, produces text out. It knows *nothing* about your user or your data unless you put it in the prompt.
2. **Retrieval Layer** — finds the *right knowledge* (your docs, a user's history, the web) and feeds it into the prompt so the model can answer about things it was never trained on.
3. **Orchestration Layer** — the wiring that decides *what to send the model, in what order, with which tools, and what to do with the answer.* This is where "an LLM call" becomes "an AI feature."
4. **Application Layer** — everything the user actually sees and the infrastructure around it: UI, backend server, your own API, authentication, billing, rate limiting, logging.

---

## 2. Why It Exists (why split into layers at all?)

Because each layer solves a **different, independent problem**, and separating them lets you swap any one without rewriting the others:

- The model is a **commodity you rent** — you don't train it, you call it. Swapping GPT for Claude shouldn't force a UI rewrite.
- Models have **frozen knowledge and no memory** — the retrieval layer exists purely to fix that (give them fresh/private facts).
- A single model call is **stateless and dumb about your goals** — orchestration exists to turn one call into a multi-step, tool-using, stateful workflow.
- Users need **a product, not a model** — the application layer exists because nobody pays for "raw API access" except other developers.

The separation is the whole point: **loose coupling.** Real teams change models monthly, swap vector DBs, and rewrite UIs — the layered design is what makes that survivable.

---

## 3. How It Works Internally (follow one request through the stack)

User asks a product: *"What's our refund policy for orders over 30 days?"*

1. **Application Layer** receives the HTTP request (user is authenticated, request is logged, rate-limit checked).
2. **Orchestration Layer** takes the question and decides a plan: "this needs company-specific knowledge → do retrieval first."
3. **Retrieval Layer** converts the question into an **embedding** (a vector), searches a **vector database** of the company's policy documents, and returns the 3 most relevant chunks.
4. **Orchestration Layer** assembles a final prompt: `system instructions + retrieved policy chunks + the user's question`.
5. **Model Layer** receives that prompt and generates an answer grounded in the chunks.
6. The answer flows **back up**: orchestration may post-process it (format, add citations) → application layer returns it to the UI → user sees it.

> **Key insight:** the model never "looked up" anything. The *retrieval layer* did the lookup and the *orchestration layer* pasted the result into the prompt. The model just reasoned over text it was handed. This single insight demystifies 80% of AI products.

---

## 4. Trade-offs (the decisions real engineers argue about)

- **Buy vs build the model:** Proprietary APIs (OpenAI/Anthropic) = best quality, zero ops, but cost + vendor lock-in + data leaves your walls. Open-source (Llama, etc.) = control + privacy, but you run the infra.
- **Retrieval vs bigger context window:** You *could* paste more text into a huge context window instead of retrieving — but it's slower, costlier, and quality degrades. Retrieval is the scalable answer. (More in Concept 04 & 05.)
- **Use a framework vs roll your own orchestration:** LangChain/LlamaIndex give you speed early but add abstraction you must debug later. Many production teams start with a framework and rip it out. (Concept 06.)
- **Thin app vs thick app:** Putting logic in prompts is fast to change but fragile; putting it in code is robust but slower to iterate. Production systems balance both.

---

## 5. Real-World Usage (where the famous products sit)

- **ChatGPT / Claude.ai** — Model + Orchestration + App. (Retrieval only when you attach files or browse.)
- **Perplexity** — *Retrieval-first*: it searches the web, then feeds results to a model. The retrieval layer is the star.
- **GitHub Copilot / Cursor** — Application layer is the editor; orchestration assembles your code context; retrieval pulls relevant files; model completes.
- **Notion AI** — App layer is the doc editor; retrieval pulls your workspace content; model writes/edits.

We'll do full teardowns of all of these in **Concept 07**. For now, just notice: *they're all the same four layers in different proportions.*

---

## 6. Practical Exercise (do this in your head / a notebook)

For each product below, sketch which layers it leans on most and draw the request flow:

1. A customer-support bot that answers from a company's help docs.
2. A "chat with your PDF" app.
3. A coding autocomplete tool.
4. A plain chatbot with no external knowledge.

> Goal: be able to say *"layer X does Y here"* for each. Bring your sketches and I'll review them.

---

## 7. Mini-Project (later, after M1–M2)

Build a one-file Python script that is a **minimal vertical slice of the whole stack**:
- App layer: a CLI that takes a question.
- Orchestration: assembles a system prompt + the question.
- Model: calls a provider.
- (Retrieval comes in M7.)

You'll basically build a tiny ChatGPT with no retrieval — and *feel* where the retrieval layer is missing.

---

## 8. Self-Test Questions (answer before we move on)

1. A model is said to be "stateless." What does that mean, and which layer compensates for it?
2. If a model was trained in 2024 and you ask it about something from last week, which layer makes a correct answer possible, and how?
3. Why is it valuable that the model layer is "swappable"? Give a concrete business reason.
4. Perplexity and a basic chatbot both call an LLM. What's the architectural difference between them?
5. In the refund-policy example, the model "answered a company-specific question" — but it was never trained on that company. Explain, in one sentence, how that's possible.

---

## 9. My Notes & Observations

> (Your space. Write what clicked, what's still fuzzy, and any "wait, but what about…" questions.)

- 
