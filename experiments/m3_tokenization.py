"""
m3_tokenization.py — Milestone 3: make TOKENS visible.

Why this matters (the M3 thesis)
--------------------------------
An LLM never sees your characters or words. Your text is first chopped into
"tokens" — sub-word chunks — and the model only ever works with those. Tokens
are the unit you are BILLED in, the unit CONTEXT WINDOWS are measured in, and a
major driver of LATENCY. So "how many tokens is this?" is a question you'll ask
constantly as an AI engineer.

This script does two things:
  PART A — show tokenization locally with `tiktoken` (you SEE the sub-word
           pieces, not just a count).
  PART B — compare a local count against the REAL token count the model's API
           reports, to prove tokenizers are model-specific.

How to run (from the project root)
----------------------------------
  .venv\\Scripts\\activate
  python experiments\\m3_tokenization.py

Java analogy
------------
tiktoken's encoder is like a CharsetEncoder/Tokenizer: text in -> int[] out.
Each int is a token id; decoding one id gives back its text piece.
"""
from __future__ import annotations

import sys

from config import available_providers
from llm import get_provider

# Make non-ASCII (e.g. the Hindi sample, or an upstream error) printable on
# Windows' legacy console instead of crashing. (Same fix as the M2 runner.)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# tiktoken is OpenAI's tokenizer. It is NOT identical to Llama's (Groq) — that
# very difference is Part B's lesson — but it's perfect for SEEING how
# tokenization works. "cl100k_base" is the GPT-3.5/4 encoding.
ENCODING_NAME = "cl100k_base"

# Strings chosen to reveal different tokenization behaviours.
SAMPLES = [
    "Hello, world!",
    "tokenization",                       # 1 word -> 'token' + 'ization'
    "antidisestablishmentarianism",       # 1 long word -> many tokens
    "AI",                                 # tiny
    "       ",                            # pure whitespace
    "1234567890",                         # digits chunk oddly
    "def add(a, b):\n    return a + b",   # code
    "नमस्ते दुनिया",                        # non-English: far MORE tokens per char
]


def _label(s: str) -> str:
    """Display a sample on one line: keep real (incl. non-English) text, but make
    newlines visible, wrap in quotes, and truncate long ones."""
    shown = s.replace("\n", "\\n")
    shown = f'"{shown}"'
    return shown if len(shown) <= 32 else shown[:29] + '..."'


def show_local_tokenization(enc) -> None:
    print("=" * 72)
    print(f"PART A — local tokenization with tiktoken ({ENCODING_NAME})")
    print("=" * 72)
    print(f"{'text':34}{'chars':>6}{'words':>6}{'tokens':>7}{'chars/tok':>10}")
    print("-" * 72)
    for s in SAMPLES:
        ids = enc.encode(s)
        n_tokens = len(ids)
        n_chars = len(s)
        n_words = len(s.split())
        ratio = (n_chars / n_tokens) if n_tokens else 0.0
        print(f"{_label(s):34}{n_chars:>6}{n_words:>6}{n_tokens:>7}{ratio:>10.2f}")

    # Now SHOW the pieces for one sentence — the most illuminating part.
    demo = "Tokenization isn't magic - it's sub-words!"
    ids = enc.encode(demo)
    pieces = [enc.decode([i]) for i in ids]
    print("\nSeeing the pieces — how the model actually reads a sentence:")
    print(f"  text   : {demo}")
    print(f"  tokens : {len(ids)}")
    print(f"  pieces : {pieces}")
    print("  (Note: a leading space is part of the token, and 'Tokenization'")
    print("   splits into sub-words. The model predicts ONE of these at a time.)")


def compare_with_model(enc) -> None:
    print("\n" + "=" * 72)
    print("PART B — local count vs the model's OWN tokenizer (Groq / Llama)")
    print("=" * 72)
    if "groq" not in available_providers():
        print("Groq key not found in .env — skipping the live comparison.")
        return

    user_text = "Explain tokenization in one short sentence."
    provider = get_provider("groq")
    result = provider.chat("You are concise.", user_text)

    local_user_tokens = len(enc.encode(user_text))
    print(f"user text           : {user_text!r}")
    print(f"tiktoken (OpenAI)   : {local_user_tokens} tokens for that text alone")
    print(f"Groq/Llama reports  : prompt_tokens={result.prompt_tokens}, "
          f"completion_tokens={result.completion_tokens}")
    print("\nWhy the numbers differ — two reasons, both worth internalizing:")
    print("  1) Different tokenizer: Llama's vocabulary != OpenAI's, so the SAME")
    print("     text becomes a different token count on each model.")
    print("  2) Overhead: the API's prompt_tokens counts the WHOLE request —")
    print("     your system prompt + chat-template role markers — not just text.")
    print("\nTakeaway: estimate locally, but the API's usage is the BILLABLE truth.")


def main() -> int:
    try:
        import tiktoken
    except ImportError:
        print("tiktoken not installed. Run: pip install -r experiments/requirements.txt",
              file=sys.stderr)
        return 1
    enc = tiktoken.get_encoding(ENCODING_NAME)

    show_local_tokenization(enc)
    compare_with_model(enc)

    print("\nRule of thumb to memorize: ~4 chars/token for English (~0.75 words/token).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
