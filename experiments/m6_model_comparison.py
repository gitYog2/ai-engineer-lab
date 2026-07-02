"""
m6_model_comparison.py — Milestone 6: compare models head-to-head.

The point
---------
"Which model should I use?" is THE recurring AI-engineering question. The honest
answer is "it depends on the task" — so you compare. This harness runs the SAME
set of prompts (different task TYPES) across every model you list, at temperature
0 (fair, deterministic), and reports speed + output size so you can eyeball
QUALITY yourself.

This is the human-judged version. Auto-scoring with an "LLM-as-judge" comes later.

What you'll likely see
----------------------
A big general model (Groq's Llama-3.3-70B) vs a smaller specialized one
(Ollama's MedGemma-27B): close on easy facts, diverging on code / instruction-
following / reasoning. That gap IS the lesson — capability vs size/speed/cost.

Run (from project root):
  python experiments\\m6_model_comparison.py
"""
from __future__ import annotations

import sys
import time

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from config import available_providers
from llm import get_provider

# Which providers to put head-to-head. Edit to add any you have keys for.
PROVIDERS_TO_COMPARE = ["groq", "ollama"]

SYSTEM = "Be helpful and concise."
# (category, prompt) — chosen to stress DIFFERENT capabilities.
PROMPTS = [
    ("factual",   "What is the capital of Australia? One word."),
    ("reasoning", "A train goes 60 km in 1.5 hours. Average speed in km/h? Give the number and a one-line why."),
    ("creative",  "Write a two-line poem about the sea."),
    ("code",      "Write a Python one-liner that reverses a string s."),
    ("following", "Reply with exactly three primary colors, comma-separated, nothing else."),
]
TEMPERATURE = 0.0  # deterministic => a fair, repeatable comparison


def main() -> int:
    providers = [p for p in PROVIDERS_TO_COMPARE if p in available_providers()]
    missing = [p for p in PROVIDERS_TO_COMPARE if p not in available_providers()]
    for p in missing:
        print(f"(skipping '{p}' — no key/base URL in .env)", file=sys.stderr)
    if not providers:
        print("No comparable providers available. Check .env.", file=sys.stderr)
        return 1

    clients = {name: get_provider(name) for name in providers}
    print("Comparing:", ", ".join(f"{n} ({c.model})" for n, c in clients.items()))

    # stats[name] = [total_latency, total_completion_tokens, n_ok]
    stats = {name: [0.0, 0, 0] for name in providers}

    for category, prompt in PROMPTS:
        print("\n" + "=" * 72)
        print(f"[{category}]  {prompt}")
        print("-" * 72)
        for name in providers:
            start = time.perf_counter()
            try:
                result = clients[name].chat(SYSTEM, prompt, temperature=TEMPERATURE)
            except Exception as exc:
                print(f"  {name:8} ERROR: {exc}")
                continue
            elapsed = time.perf_counter() - start
            stats[name][0] += elapsed
            stats[name][1] += result.completion_tokens
            stats[name][2] += 1
            answer = " ".join(result.text.strip().split())  # collapse to one line
            print(f"  {name:8} ({elapsed:4.1f}s, {result.completion_tokens:>3} tok): {answer}")

    print("\n" + "=" * 72)
    print("SUMMARY")
    print(f"{'provider':10}{'prompts':>8}{'avg latency':>13}{'total out tok':>15}")
    for name in providers:
        total_lat, total_tok, n = stats[name]
        avg = total_lat / n if n else 0.0
        print(f"{name:10}{n:>8}{avg:>11.1f}s{total_tok:>15}")
    print("\nQuality is YOURS to judge — read the answers above. Speed/size is measured;")
    print("'best' = the cheapest/fastest model that still passes your quality bar per task.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
