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
    novarelay_api_key,
    ollama_base_url,
    ollama_model,
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

    def chat(self, system: str, user: str, temperature: float = 0.7) -> ChatResult:
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

    def chat(self, system: str, user: str, temperature: float = 0.7) -> ChatResult:
        # In this dialect the system prompt is just the first message in the list.
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
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


class NovaRelayProvider(_OpenAICompatibleProvider):
    """Nova AI Relay (novarelay.io) — an OpenAI-COMPATIBLE gateway that fronts
    many model families (Claude, GPT, Gemini, ...) behind ONE key and ONE base
    URL. Because it speaks the OpenAI dialect, we reach it with the very same
    OpenAI SDK — we only point `base_url` at the relay. This is the cleanest
    proof of the M2 lesson: "OpenAI-compatible" means *same code, just swap
    base_url + key + model*. Here it lets us call a Claude model THROUGH the
    OpenAI dialect (no Anthropic SDK needed).
    """
    name = "novarelay"
    default_model = "claude-opus-4-8"      # a Claude model, served via the relay
    base_url = "https://ai.novarelay.io/v1"
    # novarelay sits behind Cloudflare, whose bot filter blocks the OpenAI SDK's
    # default User-Agent ("OpenAI/Python ...") with a 403 "Your request was
    # blocked." Sending a plain custom User-Agent gets through. (Found by
    # comparing raw httpx — which reached the app — against the SDK, which 403'd.)
    user_agent = "ai-engineer-roadmap/1.0"

    def _make_client(self):
        from openai import OpenAI
        # Same SDK as OpenAIProvider — the differences are base_url, key, and the
        # custom User-Agent required to pass novarelay's Cloudflare bot filter.
        return OpenAI(
            api_key=novarelay_api_key(),
            base_url=self.base_url,
            default_headers={"User-Agent": self.user_agent},
        )


class OllamaProvider(_OpenAICompatibleProvider):
    """A local or remote Ollama server, reached via its OpenAI-compatible /v1
    API. Same dialect as OpenAI/Groq/novarelay — only base_url + model change.
    Ollama ignores auth, so the api_key is a throwaway placeholder. WHICH model
    exists is server-specific (whatever was `ollama pull`-ed), so both the base
    URL and the model are read from .env (OLLAMA_BASE_URL / OLLAMA_MODEL).
    """
    name = "ollama"
    default_model = "puyangwang/medgemma-27b-it:q8"  # overridable via OLLAMA_MODEL

    def __init__(self, model: str | None = None):
        self.model = model or ollama_model()
        self._client = self._make_client()

    def _make_client(self):
        from openai import OpenAI
        # Ollama needs no real key; the SDK only requires a non-empty value.
        return OpenAI(api_key="ollama", base_url=ollama_base_url())


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

    def chat(self, system: str, user: str, temperature: float = 0.7) -> ChatResult:
        response = self._client.messages.create(
            model=self.model,
            system=system,                  # DIFFERENT: top-level arg, NOT a message
            messages=[{"role": "user", "content": user}],
            max_tokens=1024,                # DIFFERENT: REQUIRED by Anthropic
            temperature=temperature,
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
    "novarelay": NovaRelayProvider,
    "ollama": OllamaProvider,
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
