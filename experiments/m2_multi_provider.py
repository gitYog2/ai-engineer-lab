"""
m2_multi_provider.py — Milestone 2: call MANY providers through ONE pattern.

What this demonstrates
----------------------
We ask the SAME question to every provider you currently have a key for, using
the SAME `chat()` call, then print a side-by-side comparison (tokens + latency +
answer). Adding or swapping a provider needs ZERO changes in this file — only a
key in `.env`. That is the entire payoff of the M2 abstraction (see llm.py).

How to run (Windows PowerShell, from the project root)
------------------------------------------------------
  .venv\\Scripts\\activate
  python experiments\\m2_multi_provider.py

Today you have only a GROQ key, so only Groq runs. Add OPENAI_API_KEY and/or
ANTHROPIC_API_KEY to `.env` and re-run — the others light up automatically,
and this file never changes. THAT is the lesson.

Java analogy for the overall shape
----------------------------------
A console app with a `main` that returns an exit code, looping over a list of
strategy implementations and collecting their results into rows for a report.
"""
from __future__ import annotations

import sys
import time

from config import available_providers
from llm import ChatResult, get_provider

# Windows consoles default to a legacy code page (cp1252) that can't print
# non-ASCII text — e.g. an upstream provider error in another language — and
# would crash the whole script with UnicodeEncodeError. Force UTF-8 so any
# provider's output (or error) prints safely. (No-op on systems already UTF-8.)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Same prompt for everyone, so the comparison is apples-to-apples.
SYSTEM_PROMPT = "You are a clear, friendly teacher. Answer in exactly 2 sentences."
USER_PROMPT = "What is a Large Language Model?"


def run_one(provider_name: str) -> tuple[ChatResult, float] | None:
    """Call one provider and time it. Returns (result, seconds), or None on error.

    We deliberately catch broadly here: one provider failing (bad key, missing
    SDK, rate limit) must NOT stop the others from running. Each row is best-effort.
    """
    try:
        provider = get_provider(provider_name)
    except Exception as exc:  # missing SDK / key construction failure
        print(f"[{provider_name}] skipped — could not initialize: {exc}", file=sys.stderr)
        return None

    start = time.perf_counter()
    try:
        result = provider.chat(SYSTEM_PROMPT, USER_PROMPT)
    except Exception as exc:  # network / API rejection
        print(f"[{provider_name}] call failed: {exc}", file=sys.stderr)
        return None
    elapsed = time.perf_counter() - start
    return result, elapsed


def main() -> int:
    """Entry point. Returns a process exit code (0 = success)."""
    providers = available_providers()
    if not providers:
        print("No provider keys found in .env. Add at least GROQ_API_KEY.", file=sys.stderr)
        return 1

    print(f"Providers with a key today: {', '.join(providers)}")
    print(f"\nQUESTION\n  {USER_PROMPT}\n")

    rows: list[tuple[ChatResult, float]] = []
    for name in providers:
        outcome = run_one(name)
        if outcome is None:
            continue
        result, elapsed = outcome
        rows.append(outcome)
        print("-" * 72)
        print(f"PROVIDER : {result.provider}")
        print(f"MODEL    : {result.model}")
        print(f"LATENCY  : {elapsed:.2f} s")
        print(f"TOKENS   : prompt={result.prompt_tokens}  "
              f"completion={result.completion_tokens}  total={result.total_tokens}")
        print(f"ANSWER   : {result.text.strip()}")

    # Compact comparison table at the end — the part you actually study.
    if rows:
        print("\n" + "=" * 72)
        print("COMPARISON")
        print(f"{'provider':<12}{'model':<30}{'latency':<10}{'tokens':<8}")
        for result, elapsed in rows:
            print(f"{result.provider:<12}{result.model:<30}{elapsed:<10.2f}{result.total_tokens:<8}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
