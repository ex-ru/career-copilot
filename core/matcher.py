"""
core/matcher.py - In-depth Job Requirements and Candidate Stack Matching Engine.
Performs gap analysis, calculates fit score, and creates targeted positioning strategy.
"""

from typing import Dict, Any
import re
from core.llm import llm


class JobMatcher:
    """Matches candidate profile against job vacancy descriptions."""

    @staticmethod
    def detect_language(vacancy_text: str) -> str:
        """Detects whether vacancy is predominantly English, Russian or mixed."""
        cyrillic_chars = len(re.findall(r'[\u0400-\u04FF]', vacancy_text))
        latin_chars = len(re.findall(r'[a-zA-Z]', vacancy_text))
        if cyrillic_chars > latin_chars * 0.4:
            return "ru"
        return "en"

    @classmethod
    def analyze_match(cls, profile_markdown: str, vacancy_text: str, vacancy_title: str = "Target Job") -> str:
        """
        Produces a comprehensive matching analysis markdown document.
        """
        system_prompt = (
            "Ты — ведущий эксперт по карьерному трекингу и техническому отбору кандидатов. "
            "Твоя задача — сопоставить профиль кандидата с требованиями конкретной вакансии и составить "
            "детальный аналитический отчет matching_analysis.md.\n\n"
            "Структура отчета:\n"
            "# Анализ соответствия (Matching Analysis): [Название роли / Компании]\n\n"
            "## 1. Сводная оценка (Fit Score)\n"
            "- Общий процент соответствия (0-100%)\n"
            "- Вердикт (Strong Fit / Moderate Fit / Stretch)\n"
            "- Язык вакансии и специфика локации/формата\n\n"
            "## 2. Карта совпадения стека и требований\n"
            "| Требование вакансии | Опыт кандидата | Статус (Полное / Частичное / Пробел) |\n"
            "| ... | ... | ... |\n\n"
            "## 3. Сильные стороны для выделения (Ключевые козыри)\n"
            "- Топ-3-5 аргументов, почему кандидат идеально справится с задачами роли\n\n"
            "## 4. Пробелы и стратегия их нивелирования\n"
            "- Чего не хватает и как честно компенсировать это смежным опытом\n\n"
            "## 5. Стратегия адаптации резюме и Cover Letter\n"
            "- На каких проектах сделать акцент\n"
            "- Какие формулировки и ключевые слова использовать для прохождения ATS\n\n"
            "ВАЖНО: Пиши сразу итоговый структурированный Markdown без тегов <think> и без долгих рассуждений."
        )

        user_prompt = (
            f"--- ВАКАНСИЯ: {vacancy_title} ---\n{vacancy_text[:3500]}\n\n"
            f"--- МАСТЕР-ПРОФИЛЬ КАНДИДАТА ---\n{profile_markdown[:4500]}\n\n"
            "Проведи глубокий аудит и сформируй полный matching_analysis.md."
        )

        return llm.complete(system_prompt, user_prompt, temperature=0.2, max_tokens=2500)
