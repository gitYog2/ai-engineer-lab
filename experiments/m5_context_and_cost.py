"""
m5_context_and_cost.py — Milestone 5: context windows + cost math.

Two ideas, both measured in TOKENS (back to Concept 04):

1) CONTEXT WINDOW — the fixed number of tokens a model can "see" in ONE request.
   Your system prompt + chat history + the new question + the answer it generates
   must ALL fit inside it. Exceed it and the API errors out (or silently drops
   the oldest text).

2) COST — you pay per token, with input (prompt) and output (completion) priced
   separately. For the SAME work, model choice can swing the bill ~100x.

This makes ONE real Groq call, then uses its token `usage` to:
  - show how much of the context window the call used, and
  - compute the $ cost on Groq AND what the SAME call would cost on other models.

Run (from project root):
  python experiments\\m5_context_and_cost.py
"""
from __future__ import annotations

import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from llm import get_provider

# Context window sizes in TOKENS. Approximate — check each provider's docs.
CONTEXT_WINDOW = {
    "llama-3.3-70b-versatile": 128_000,
}

# Price per 1,000,000 tokens as (input, output) in USD.
# !!! ILLUSTRATIVE / APPROXIMATE (as of 2026) — verify on each provider's pricing
# page before trusting for real budgeting. The MATH is the lesson, not the exact $.
PRICES = {
    "Groq Llama-3.3-70B":   (0.59, 0.79),
    "GPT-4o-mini":          (0.15, 0.60),
    "GPT-4o":               (2.50, 10.00),
    "Claude Sonnet":        (3.00, 15.00),
    "Claude Opus":          (15.00, 75.00),
    "Self-hosted (Ollama)": (0.00, 0.00),
}


def usd(prompt_tokens: int, completion_tokens: int, price_in: float, price_out: float) -> float:
    """Cost of one call: (tokens / 1M) * price-per-1M, summed for input + output."""
    return prompt_tokens / 1_000_000 * price_in + completion_tokens / 1_000_000 * price_out


def main() -> int:
    provider = get_provider("groq")
    model = provider.model
    window = CONTEXT_WINDOW.get(model, 128_000)

    # One real call so we reason about HONEST token numbers, not guesses.
    result = provider.chat(
        "You are concise.",
        "In two sentences, what is a context window?",
        temperature=0.0,
    )
    pt, ct, total = result.prompt_tokens, result.completion_tokens, result.total_tokens

    print("=" * 72)
    print("PART A — CONTEXT WINDOW (the token budget per request)")
    print("=" * 72)
    print(f"model               : {model}")
    print(f"context window      : {window:,} tokens")
    print(f"this call used      : {total:,} tokens (prompt {pt} + completion {ct})")
    print(f"% of window used    : {total / window * 100:.4f}%")
    print(f"room left in window : {window - total:,} tokens")
    print(f"rough capacity      : ~{window / 650:,.0f} pages of English (~650 tok/page)")
    print("  -> Exceed the window and the API rejects the call (context_length_exceeded)")
    print("     or silently drops the oldest messages. THIS is why retrieval (M7) exists.")

    print("\n" + "=" * 72)
    print("PART B — COST MATH (the SAME call, priced on every model)")
    print("=" * 72)
    print(f"Billing this one call: prompt={pt} tokens, completion={ct} tokens")
    print("Prices are ILLUSTRATIVE $/1M tokens (input, output) — verify before trusting.\n")
    print(f"{'model':22}{'in/1M':>8}{'out/1M':>8}{'this call':>14}{'1M calls/mo':>14}")
    print("-" * 72)
    for name, (pin, pout) in PRICES.items():
        c = usd(pt, ct, pin, pout)
        print(f"{name:22}{pin:>8.2f}{pout:>8.2f}{'$' + format(c, '.6f'):>14}"
              f"{'$' + format(c * 1_000_000, ',.0f'):>14}")

    print("\nTakeaways:")
    print("  - Same work, ~100x cost spread across models -> model choice IS a cost decision.")
    print("  - Output tokens usually cost MORE than input -> watch max_tokens / verbosity.")
    print("  - Self-hosted (Ollama) is $0 per token (you pay for hardware + electricity).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
