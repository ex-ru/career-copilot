"""
core/llm.py - Universal LLM Client supporting OpenAI, Gemini, Claude, OpenRouter, and Ollama.
Provides synchronous and streaming interfaces for real-time interactive experiences.
"""

from typing import Generator, List, Dict, Tuple, Optional
from openai import OpenAI
from core.config import config, AppConfig


class LLMClient:
    """Wrapper around OpenAI-compatible APIs."""

    def __init__(self, cfg: Optional[AppConfig] = None):
        self.cfg = cfg or config
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            kwargs = {}
            if self.cfg.api_key:
                kwargs["api_key"] = self.cfg.api_key
            else:
                # Local models like Ollama might not require a real key
                kwargs["api_key"] = "local-dummy-key"

            base_url = self.cfg.normalized_base_url
            if base_url:
                kwargs["base_url"] = base_url

            self._client = OpenAI(**kwargs)
        return self._client

    def reload(self) -> None:
        """Forces client reinitialization after config change."""
        self._client = None

    def test_connection(self) -> Tuple[bool, str]:
        """Tests connection with a lightweight prompt."""
        if not self.cfg.is_configured:
            return False, "API ключ или адрес локального сервера не настроен. Проверьте файл .env."
        try:
            response = self.client.chat.completions.create(
                model=self.cfg.model,
                messages=[{"role": "user", "content": "Привет, подтверди готовность в одном коротком предложении."}],
                max_tokens=150,
                temperature=0.0
            )
            raw_msg = response.choices[0].message.content
            if not raw_msg and hasattr(response.choices[0].message, 'reasoning_content'):
                raw_msg = response.choices[0].message.reasoning_content
            msg = (raw_msg or "Готовность подтверждена (OK)").strip()
            return True, f"Соединение успешно ({self.cfg.provider_name}, модель: {self.cfg.model}): {msg}"
        except Exception as e:
            return False, f"Ошибка подключения к AI: {str(e)}"

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Single non-streaming completion."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.cfg.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.cfg.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.cfg.max_tokens
        )
        choice = response.choices[0]
        content = choice.message.content or ""
        if not content.strip():
            reasoning = getattr(choice.message, 'reasoning_content', '') or ""
            if reasoning.strip():
                content = reasoning.strip()
        return content

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Generator[str, None, None]:
        """Streaming chat completions for interactive CLI conversations."""
        stream = self.client.chat.completions.create(
            model=self.cfg.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.cfg.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.cfg.max_tokens,
            stream=True
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Generator[str, None, None]:
        """Streaming completion with system and user prompts."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        yield from self.stream_chat(messages, temperature, max_tokens)


llm = LLMClient()
