"""
m4_temperature.py — Milestone 4: temperature (how the model PICKS each token).

The idea
--------
At every step the model outputs a probability distribution over the next token.
`temperature` controls HOW we sample from that distribution:
  - temperature = 0   -> always take the single most likely token
                         => deterministic, repeatable (greedy decoding)
  - higher temperature -> flattens the distribution -> more random / "creative"

This script asks the SAME prompt several times at a LOW and a HIGH temperature
so you can SEE the difference: repetition vs variety.

Run (from project root):
  python experiments\\m4_temperature.py

Java analogy
------------
temperature is like a "randomness strength" on a generator: 0 = pure function
(same input -> same output); higher = stochastic.
"""
from __future__ import annotations

import sys

# UTF-8 console so any non-ASCII output prints instead of crashing (as in M2/M3).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from llm import get_provider

PROVIDER = "ollama"
SYSTEM = "You are a creative branding assistant."
USER = "Invent a name for a coffee shop. Reply with ONLY the name, nothing else."
RUNS = 4  # how many times to repeat the SAME prompt at each temperature


def run_at(provider, temperature: float) -> None:
    print(f"\n--- temperature = {temperature}  (same prompt x{RUNS}) ---")
    for i in range(1, RUNS + 1):
        answer = provider.chat(SYSTEM, USER, temperature=temperature).text.strip()
        print(f"  {i}. {answer}")


def main() -> int:
    provider = get_provider(PROVIDER)
    print(f"Provider: {PROVIDER}  ({provider.model})")
    print(f"Prompt  : {USER}")

    run_at(provider, 0.0)   # expect (near-)identical answers every time
    run_at(provider, 1.3)   # expect a different answer almost every time

    print("\nWhat to notice:")
    print("  temp 0.0 -> answers repeat  => deterministic; use for extraction,")
    print("              classification, code, anything needing consistency.")
    print("  temp 1.3 -> answers vary    => creative; use for brainstorming,")
    print("              naming, writing, generating options.")
    print("\nMental model: same probability distribution, different *sampling*.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
