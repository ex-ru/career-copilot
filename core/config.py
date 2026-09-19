"""
core/config.py - Centralized configuration loader for Career Copilot.
Handles environment variables, API endpoints, paths, and provider detection.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUTS_DIR = DATA_DIR / "inputs"
VACANCIES_DIR = DATA_DIR / "vacancies"
OUTPUT_DIR = DATA_DIR / "output"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Auto-load .env
load_dotenv(PROJECT_ROOT / ".env")


class AppConfig(BaseModel):
    # LLM Settings
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    base_url: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL") or None)
    model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.3")))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "4000")))
    default_language: str = Field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "both"))

    # Project directories
    project_root: Path = PROJECT_ROOT
    inputs_dir: Path = INPUTS_DIR
    vacancies_dir: Path = VACANCIES_DIR
    output_dir: Path = OUTPUT_DIR
    templates_dir: Path = TEMPLATES_DIR

    @property
    def normalized_base_url(self) -> Optional[str]:
        """Ensures base_url ends with /v1 if missing for local servers."""
        if not self.base_url:
            return None
        url = self.base_url.rstrip("/")
        if not url.endswith("/v1"):
            return f"{url}/v1"
        return url

    @property
    def provider_name(self) -> str:
        """Determines the friendly provider name based on URL and model."""
        if not self.base_url:
            return "OpenAI (Direct)"
        url = self.base_url.lower()
        if "openrouter" in url:
            return "OpenRouter Gateway"
        if "generativelanguage.googleapis.com" in url or "google" in url:
            return "Google Gemini (OpenAI Compat)"
        if "localhost:11434" in url or "ollama" in url:
            return "Ollama (Local Offline)"
        if "8080" in url or "llama" in url:
            return "llama.cpp (Local Server)"
        if "deepseek" in url:
            return "DeepSeek API"
        if "127.0.0.1:1234" in url or "lmstudio" in url:
            return "LM Studio (Local Offline)"
        if any(ip in url for ip in ["192.168.", "10.", "172.", "localhost", "127.0.0.1"]):
            return f"Local / LAN Server ({self.base_url})"
        return f"Custom API ({self.base_url})"

    @property
    def is_configured(self) -> bool:
        """Returns True if minimum required settings to call AI are present."""
        # For Ollama / llama.cpp / local LAN servers, api_key can be dummy
        if self.base_url and any(x in self.base_url for x in ["localhost", "127.0.0.1", "192.168.", "10.", "172.", "8080", "11434"]):
            return True
        return bool(self.api_key and self.api_key.strip())

    def ensure_directories(self) -> None:
        """Creates necessary working directories if missing."""
        for d in [self.inputs_dir, self.vacancies_dir, self.output_dir, self.templates_dir]:
            d.mkdir(parents=True, exist_ok=True)


config = AppConfig()
config.ensure_directories()
