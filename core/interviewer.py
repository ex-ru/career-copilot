"""
core/interviewer.py - Interactive Career Interviewer and Gap-Filling Engine.
Supports both Fast Track (refining existing resume) and Deep Career Interview (from scratch).
"""

from typing import List, Dict, Generator
from core.llm import llm


class CareerInterviewer:
    """Manages dialog state and questions during candidate onboarding."""

    DEEP_INTERVIEW_SYSTEM_PROMPT = (
        "Ты — технический карьерный интервьюер. "
        "Твоя задача — провести быстрое, динамичное интервью с IT-специалистом для составления матрицы навыков.\n\n"
        "КРИТИЧЕСКИЕ ТРЕБОВАНИЯ К КРАТКОСТИ:\n"
        "1. Формулируй вопросы МАКСИМАЛЬНО КОРОТКО: строго 1–2 емких предложения (до 25–30 слов).\n"
        "2. Задавай строго ОДИН конкретный вопрос за шаг. Не перегружай кандидатов списками.\n"
        "3. НИКАКОЙ «воды», долгих вступлений, комплиментов ('Отличный ответ!'), лекций и описаний методологий.\n"
        "4. Краткий отклик на ответ кандидата (2–4 слова, например: 'Понял, зафиксировал.') + сразу следующий вопрос.\n"
        "5. План диалога:\n"
        "   - Вопрос 1: Текущая роль и 1–2 целевые позиции для поиска.\n"
        "   - Вопрос 2: Ключевой стек технологий и главная суперсила.\n"
        "   - Вопрос 3: Главный проект за последнее время: что именно сделал и какой измеримый результат в цифрах (SLA, RPS, экономия)?\n"
        "   - Вопрос 4: Был ли опыт руководства людьми (размер команды) или ответственность за архитектуру?\n"
        "   - Вопрос 5: Желаемый формат работы (удаленка/релокация/офис) и зарплатные ожидания.\n"
        "6. Если кандидат написал 'готово' или ответил на темы — кратко поблагодари в 1 предложение и заверши диалог."
    )

    FAST_TRACK_SYSTEM_PROMPT = (
        "Ты — технический рекрутер. Твоя задача — задать кандидату предельно короткие уточняющие вопросы по его резюме.\n\n"
        "ПРАВИЛА:\n"
        "1. Формулируй вопросы строго в 1 короткое предложение (до 15–20 слов).\n"
        "2. Задавай строго 1 конкретный вопрос за шаг.\n"
        "3. Спрашивай только недостающие цифры: размер инфраструктуры, RPS, метрики оптимизации или бюджет.\n"
        "4. Без вступлений, приветствий и вежливых расшаркиваний — сразу суть вопроса."
    )

    def __init__(self, mode: str = "deep", initial_context: str = ""):
        self.mode = mode
        self.initial_context = initial_context
        self.history: List[Dict[str, str]] = []

        system_msg = self.FAST_TRACK_SYSTEM_PROMPT if mode == "fast" else self.DEEP_INTERVIEW_SYSTEM_PROMPT
        if initial_context:
            system_msg += f"\n\nКонтекст уже имеющихся документов кандидата:\n{initial_context[:10000]}"

        self.history.append({"role": "system", "content": system_msg})

    def start_message(self) -> Generator[str, None, None]:
        """Generates the initial greeting and first question."""
        if self.mode == "fast":
            prompt = "Задай сразу первый предельно короткий вопрос (1 предложение) для уточнения оцифрованных результатов в резюме."
        else:
            prompt = "Поздоровайся в 3-4 словах и задай первый короткий вопрос (1 предложение): кем сейчас работаешь и на какие роли ориентируешься?"

        self.history.append({"role": "user", "content": prompt})
        accumulated = ""
        for chunk in llm.stream_chat(self.history, temperature=0.3, max_tokens=100):
            accumulated += chunk
            yield chunk

        # Replace prompt with response in history
        self.history.pop()  # remove instruction prompt
        self.history.append({"role": "assistant", "content": accumulated})

    def send_user_response(self, user_text: str) -> Generator[str, None, None]:
        """Sends candidate response and streams next interviewer question/comment."""
        self.history.append({"role": "user", "content": user_text})
        accumulated = ""
        for chunk in llm.stream_chat(self.history, temperature=0.3, max_tokens=120):
            accumulated += chunk
            yield chunk
        self.history.append({"role": "assistant", "content": accumulated})

    def get_full_transcript(self) -> str:
        """Returns readable interview dialogue for profile synthesis."""
        lines = []
        for msg in self.history:
            if msg["role"] == "user":
                lines.append(f"**Кандидат:** {msg['content']}")
            elif msg["role"] == "assistant":
                lines.append(f"**Интервьюер (AI):** {msg['content']}")
        return "\n\n".join(lines)
