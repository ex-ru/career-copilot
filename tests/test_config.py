"""
tests/test_config.py - Unit tests for configuration and provider detection.
"""

from core.config import AppConfig


def test_provider_detection():
    # OpenAI default
    cfg1 = AppConfig(api_key="sk-123", base_url=None)
    assert cfg1.provider_name == "OpenAI (Direct)"

    # Gemini
    cfg2 = AppConfig(api_key="AIzaSy", base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    assert "Gemini" in cfg2.provider_name

    # Ollama
    cfg3 = AppConfig(api_key="", base_url="http://localhost:11434/v1")
    assert "Ollama" in cfg3.provider_name
    assert cfg3.is_configured is True  # Ollama is usable without real API key

    # OpenRouter
    cfg4 = AppConfig(api_key="sk-or", base_url="https://openrouter.ai/api/v1")
    assert "OpenRouter" in cfg4.provider_name
