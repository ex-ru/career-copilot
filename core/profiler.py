"""
core/profiler.py - Candidate Profile and Skills Matrix manager.
Performs CV audits, identifies missing metrics, and synthesizes skills_matrix.md.
"""

from pathlib import Path
from typing import Dict, List, Optional
from core.config import config
from core.llm import llm
from core.parser import DocumentParser


class CandidateProfiler:
    """Manages the candidate's master profile and skills matrix."""

    PROFILE_FILE = config.data_dir_profile if hasattr(config, 'data_dir_profile') else config.project_root / "data" / "skills_matrix.md"

    @classmethod
    def get_profile_path(cls) -> Path:
        return config.project_root / "data" / "skills_matrix.md"

    @classmethod
    def has_profile(cls) -> bool:
        path = cls.get_profile_path()
        return path.exists() and path.stat().st_size > 100

    @classmethod
    def load_profile(cls) -> str:
        path = cls.get_profile_path()
        if path.exists():
            return DocumentParser.read_text_file(path)
        return ""

    @classmethod
    def save_profile(cls, content: str) -> Path:
        path = cls.get_profile_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    @classmethod
    def audit_existing_documents(cls, raw_texts: List[Dict[str, str]]) -> str:
        """
        Analyzes provided raw CV/certificate texts and produces a constructive audit:
        identifies strengths, missing metrics, vague responsibilities, and key questions to ask.
        """
        combined = "\n\n--- ДОКУМЕНТ КАНДИДАТА ---\n\n".join(
            f"Файл: {doc['name']}\n\n{doc['content']}" for doc in raw_texts
        )

        system_prompt = (
            "Ты — опытный IT-рекрутер. "
            "Твоя цель — провести краткий аудит предоставленных документов соискателя (резюме, сертификаты, портфолио). "
            "Сделай конструктивный лаконичный разбор:\n"
            "1. Сильные стороны и очевидный сеньорити/стек (2-3 буллета).\n"
            "2. Белые пятна (где не хватает оцифрованных результатов/метрик).\n"
            "3. Список из 3-4 коротких точечных вопросов кандидату (строго по 1 предложению на вопрос) для выявления метрик."
        )

        user_prompt = f"Вот исходные материалы кандидата:\n\n{combined[:14000]}\n\nПроведи аудит и сформируй вопросы."
        return llm.complete(system_prompt, user_prompt, temperature=0.3)

    @classmethod
    def synthesize_skills_matrix(cls, raw_context: str, interview_notes: str = "") -> str:
        """
        Synthesizes a structured master skills_matrix.md based on raw documents and interview notes.
        """
        system_prompt = (
            "Ты — эксперт по карьерному позиционированию в IT. "
            "На основе предоставленных документов и ответов на интервью создай исчерпывающий мастер-профиль кандидата "
            "в формате 'Матрица компетенций и единый источник истины' (skills_matrix.md).\n\n"
            "Структура документа:\n"
            "# Мастер-профиль и матрица компетенций\n"
            "## 1. Сводное позиционирование (Summary, грейд, ключевые роли, локация/формат, языки)\n"
            "## 2. Карьерные треки и специализации (3-4 ключевых фокуса со списком технологий)\n"
            "## 3. Хронология опыта с оцифрованными результатами (Компания, Период, Роль, Проекты, Метрики/Достижения, Стек)\n"
            "## 4. Карта ключевых навыков и технологий (Hard Skills, Архитектура, Инструменты, Soft Skills)\n"
            "## 5. Сертификаты, курсы и образование\n"
            "## 6. Портфолио / Публичные проекты\n\n"
            "ПРАВИЛА:\n"
            "- Никакой «воды», только факты, технологии и измеримые результаты.\n"
            "- Используй чистый структурированный Markdown."
        )

        user_prompt = (
            f"--- ИСХОДНЫЕ МАТЕРИАЛЫ КАНДИДАТА ---\n{raw_context[:12000]}\n\n"
            f"--- ЗАМЕТКИ / ОТВЕТЫ ИЗ ИНТЕРВЬЮ ---\n{interview_notes}\n\n"
            "Сформируй полную профессиональную skills_matrix.md на русском языке."
        )

        return llm.complete(system_prompt, user_prompt, temperature=0.2, max_tokens=4000)
