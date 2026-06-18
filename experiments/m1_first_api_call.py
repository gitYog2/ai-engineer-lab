"""
m1_first_api_call.py — Milestone 1: my first live LLM API call.

The whole AI application stack, in miniature
--------------------------------------------
  Application layer  -> this CLI script (the thing you run)
  Orchestration      -> we build the `messages` list (system + user)
  Model layer        -> Groq running llama-3.3-70b-versatile
  Retrieval layer    -> NOT used yet (arrives in M7)

How to run (Windows PowerShell, from the project root)
------------------------------------------------------
  .venv\\Scripts\\activate
  python experiments\\m1_first_api_call.py

Java analogy for the overall shape
----------------------------------
This is a console app with a `main` method that returns an exit code. It builds
a request object, calls a remote service via an SDK (like an HTTP client),
handles failures, and prints the result.
"""
from __future__ import annotations

import sys
import time

# The Groq SDK. `Groq` is the client (like a configured HttpClient/RestTemplate).
# The error classes let us catch specific failure types. If your installed SDK
# version names them differently, the Groq docs list the current names; as a
# fallback you can catch the base `Exception`.
from groq import Groq, APIError, APIConnectionError

from config import groq_api_key, ConfigError

# --- Configuration constants (grouped at top so they're easy to find/change) --
MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "You are a clear, friendly teacher."
USER_PROMPT = "Explain what an API is to a 10-year-old, in 3 sentences."
MAX_RETRIES = 1          # retry once on a transient network error, then give up
RETRY_BACKOFF_SECONDS = 1


def ask_model(client: Groq, system_prompt: str, user_prompt: str) -> tuple[str, object]:
    """Send one prompt to the model; return (answer_text, usage_metadata).

    The `messages` list is the heart of EVERY chat API. Each message has a role:
      - "system": standing instructions that shape the model's behavior/persona
      - "user":   the actual question from the human
      - ("assistant" would be the model's own past replies — used for memory)

    Java analogy: building a request DTO (a list of Message records) before
    handing it to a REST client.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,  # randomness/creativity dial — we experiment with this in M4
    )

    # `response.choices` is a list because the API can return several candidate
    # answers; we ask for one, so we read index 0.
    answer = response.choices[0].message.content
    return answer, response.usage


def main() -> int:
    """Entry point. Returns a process exit code (0 = success).

    Java analogy: `public static void main` — except in Python we return an int
    and pass it to `sys.exit()` so the OS sees the real exit code.
    """
    # 1) Build the client. If the key is missing, fail fast with a clear message
    #    instead of a confusing error deep inside the SDK.
    try:
        client = Groq(api_key=groq_api_key())
    except ConfigError as exc:
        print(f"[config error] {exc}", file=sys.stderr)
        return 1

    # 2) Call the model, retrying once on a transient connection error.
    #    `answer`/`usage` are initialized so the type checker knows they're set.
    answer: str = ""
    usage: object = None
    for attempt in range(1, MAX_RETRIES + 2):  # attempts: 1 (initial) .. +retries
        try:
            answer, usage = ask_model(client, SYSTEM_PROMPT, USER_PROMPT)
            break  # success — leave the retry loop
        except APIConnectionError as exc:
            # Network blip / DNS / timeout — worth one retry.
            if attempt <= MAX_RETRIES:
                print(f"[network] attempt {attempt} failed, retrying...", file=sys.stderr)
                time.sleep(RETRY_BACKOFF_SECONDS)
                continue
            print(f"[network error] could not reach Groq after retries: {exc}", file=sys.stderr)
            return 2
        except APIError as exc:
            # Bad key, rate limit, invalid model, etc. Retrying blindly won't help.
            print(f"[api error] Groq rejected the request: {exc}", file=sys.stderr)
            return 3

    # 3) Show the result and the token usage (your first peek at Concept 04).
    print("PROMPT")
    print(f"  {USER_PROMPT}\n")
    print("MODEL REPLY")
    print(f"  {answer}\n")
    print("TOKEN USAGE  (what you'll actually be billed on later)")
    print(f"  prompt_tokens     = {usage.prompt_tokens}")
    print(f"  completion_tokens = {usage.completion_tokens}")
    print(f"  total_tokens      = {usage.total_tokens}")
    return 0


# Java analogy: this guard is like checking we're the program's entry point.
# Code under it runs only when this file is executed directly (not imported).
if __name__ == "__main__":
    sys.exit(main())


# --- Observations (fill in after you run it) ---------------------------------
# 1.
# 2.
