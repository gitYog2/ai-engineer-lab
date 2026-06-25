"""
llm.py — ONE uniform way to call ANY chat LLM provider (the M2 abstraction).

The problem M2 solves
---------------------
In M1 we called Groq directly. But real AI systems swap models constantly —
for cost, quality, outages, or new releases. If every script hard-codes one
SDK, swapping a provider means rewriting the script. So we hide each provider
behind ONE common interface and let the rest of the code stay provider-agnostic.

Java analogy (this is the Strategy / Adapter pattern you already know)
----------------------------------------------------------------------
    interface LLMProvider {                    ->  class LLMProvider (base)
        ChatResult chat(system, user);         ->      def chat(self, system, user)
    }
    class GroqProvider      implements ...      ->  class GroqProvider(...)
    class OpenAIProvider    implements ...      ->  class OpenAIProvider(...)
    class AnthropicProvider implements ...      ->  class AnthropicProvider(...)

    LLMProvider p = LLMProviderFactory.get("groq");  ->  p = get_provider("groq")
    ChatResult  r = p.chat(system, user);            ->  r = p.chat(system, user)

The big lesson of M2
--------------------
Groq and OpenAI speak the SAME dialect ("OpenAI-compatible"), so they share ALL
their calling code here (see _OpenAICompatibleProvider). Anthropic speaks a
DIFFERENT dialect: a different method, the system prompt is a separate argument
(not a message), `max_tokens` is REQUIRED, the reply is a LIST of content blocks,
and even the token-count fields are named differently. That mismatch is exactly
why this abstraction earns its keep — callers don't care, they just call chat().
"""
from __future__ import annotations

from dataclasses import dataclass

from config import (
    ConfigError,
    anthropic_api_key,
    groq_api_key,
    openai_api_key,
)


@dataclass
class ChatResult:
    """A provider-agnostic answer. Every adapter normalizes its own SDK's
    response down to THIS one type, so the caller sees a consistent shape no
    matter which provider answered.

    Java analogy: a `record` / DTO returned by every adapter.
    """
    provider: str
    model: str
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMProvider:
    """Base 'interface'. Python has no `interface` keyword; the idiomatic
    equivalent is a base class whose method raises NotImplementedError.
    """
    name: str = "base"
    default_model: str = ""

    def chat(self, system: str, user: str) -> ChatResult:
        raise NotImplementedError


class _OpenAICompatibleProvider(LLMProvider):
    """Shared logic for ANY provider that speaks the OpenAI Chat Completions
    dialect. Groq and OpenAI both do, so they inherit everything here and differ
    ONLY in how their client is built (different SDK + different key).
    """

    def __init__(self, model: str | None = None):
        self.model = model or self.default_model
        self._client = self._make_client()

    def _make_client(self):
        raise NotImplementedError  # each subclass plugs in its own SDK client

    def chat(self, system: str, user: str) -> ChatResult:
        # In this dialect the system prompt is just the first message in the list.
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        usage = response.usage
        return ChatResult(
            provider=self.name,
            model=self.model,
            text=response.choices[0].message.content,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )


class GroqProvider(_OpenAICompatibleProvider):
    name = "groq"
    default_model = "llama-3.3-70b-versatile"

    def _make_client(self):
        # Lazy import: only load the SDK when this provider is actually used, so
        # someone with only a Groq key doesn't need OpenAI/Anthropic installed.
        from groq import Groq
        return Groq(api_key=groq_api_key())


class OpenAIProvider(_OpenAICompatibleProvider):
    name = "openai"
    default_model = "gpt-4o-mini"  # small + cheap; plenty for these experiments

    def _make_client(self):
        from openai import OpenAI
        return OpenAI(api_key=openai_api_key())


class AnthropicProvider(LLMProvider):
    """Anthropic does NOT use the OpenAI dialect — every line marked DIFFERENT
    is where its API diverges. This is the whole reason the abstraction exists.
    """
    name = "anthropic"
    default_model = "claude-haiku-4-5-20251001"  # fast + cheap current Claude

    def __init__(self, model: str | None = None):
        self.model = model or self.default_model
        from anthropic import Anthropic
        self._client = Anthropic(api_key=anthropic_api_key())

    def chat(self, system: str, user: str) -> ChatResult:
        response = self._client.messages.create(
            model=self.model,
            system=system,                  # DIFFERENT: top-level arg, NOT a message
            messages=[{"role": "user", "content": user}],
            max_tokens=1024,                # DIFFERENT: REQUIRED by Anthropic
            temperature=0.7,
        )
        usage = response.usage
        return ChatResult(
            provider=self.name,
            model=self.model,
            text=response.content[0].text,          # DIFFERENT: content is a list of blocks
            prompt_tokens=usage.input_tokens,       # DIFFERENT field name (vs prompt_tokens)
            completion_tokens=usage.output_tokens,  # DIFFERENT field name (vs completion_tokens)
            total_tokens=usage.input_tokens + usage.output_tokens,  # no 'total' is provided
        )


# --- Factory: short name -> ready-to-use provider instance --------------------
_REGISTRY: dict[str, type[LLMProvider]] = {
    "groq": GroqProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}


def get_provider(name: str, model: str | None = None) -> LLMProvider:
    """Return a ready-to-use provider by short name (e.g. "groq").

    Java analogy: a factory method backed by a registry Map<String, Class>.
    """
    try:
        provider_cls = _REGISTRY[name]
    except KeyError:
        known = ", ".join(_REGISTRY)
        raise ConfigError(f"Unknown provider '{name}'. Known providers: {known}")
    return provider_cls(model)
