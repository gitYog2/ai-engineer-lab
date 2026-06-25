"""
config.py — Centralized configuration loader for ALL roadmap experiments.

Java analogy
------------
Think of this as a small `ConfigUtil` class that reads `application.properties`
once at startup and exposes typed getters. Every experiment imports from here
instead of re-reading environment variables itself (DRY — Don't Repeat Yourself).

Why a separate file?
--------------------
In M2 we add OpenAI and Anthropic. Rather than copy-pasting "load the key" logic
into every script, we centralize it here once. Future scripts just call, e.g.,
`groq_api_key()` and get a validated value or a clear error.
"""
from __future__ import annotations  # lets us write modern type hints on older Pythons

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Locate and load the .env file.
#
# `__file__` is this file's path. We go up one directory (from /experiments to
# the project root) and look for ".env" there. `load_dotenv` reads KEY=VALUE
# lines and injects them into the process environment — exactly like exporting
# env vars in a shell before launching a Java app.
# ---------------------------------------------------------------------------
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


class ConfigError(RuntimeError):
    """Raised when a required configuration value is missing.

    Java analogy: a custom unchecked exception (extends RuntimeException) that
    carries a clear, actionable message.
    """


def require_env(name: str) -> str:
    """Return the value of an environment variable, or raise a clear error.

    Java analogy: like `Objects.requireNonNull(System.getenv(name), msg)` —
    but the message tells you *exactly* how to fix it instead of throwing a
    bare NullPointerException.
    """
    value = os.getenv(name)
    if not value:
        raise ConfigError(
            f"Missing required environment variable '{name}'.\n"
            f"  Fix: create a file named '.env' at {_ENV_PATH}\n"
            f"  containing the line:  {name}=your_key_here"
        )
    return value


# --- Convenience accessors (one per provider we'll use across the roadmap) ----
# Each provider stores its key under a differently-named env var. We map a short,
# friendly provider name -> the env var that holds its key, so the rest of the
# codebase never has to remember the exact variable spelling.
#
# Java analogy: a small Map<String, String> of provider -> property key.
_PROVIDER_ENV = {
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


def groq_api_key() -> str:
    return require_env("GROQ_API_KEY")


def openai_api_key() -> str:
    return require_env("OPENAI_API_KEY")


def anthropic_api_key() -> str:
    return require_env("ANTHROPIC_API_KEY")


def available_providers() -> list[str]:
    """Return the provider names whose API key is actually present in .env.

    This lets an experiment run with WHATEVER keys you have today and simply
    skip the rest — no crashes, no commented-out code. Add an OpenAI key later
    and that provider "lights up" on the next run with zero code changes.

    Java analogy: feature flags driven by which config values are populated.
    """
    return [name for name, env in _PROVIDER_ENV.items() if os.getenv(env)]
