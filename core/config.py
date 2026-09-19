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
        if "deepseek" in url:
            return "DeepSeek API"
        if "127.0.0.1:1234" in url or "lmstudio" in url:
            return "LM Studio (Local Offline)"
        return f"Custom API ({self.base_url})"

    @property
    def is_configured(self) -> bool:
        """Returns True if minimum required settings to call AI are present."""
        # For Ollama / local, api_key can be anything (even dummy)
        if self.base_url and ("localhost" in self.base_url or "127.0.0.1" in self.base_url):
            return True
        return bool(self.api_key and self.api_key.strip())

    def ensure_directories(self) -> None:
        """Creates necessary working directories if missing."""
        for d in [self.inputs_dir, self.vacancies_dir, self.output_dir, self.templates_dir]:
            d.mkdir(parents=True, exist_ok=True)


config = AppConfig()
config.ensure_directories()
