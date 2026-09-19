"""
core/interviewer.py - Interactive Career Interviewer and Gap-Filling Engine.
Supports both Fast Track (refining existing resume) and Deep Career Interview (from scratch).
"""

from typing import List, Dict, Generator
from core.llm import llm


class CareerInterviewer:
    """Manages dialog state and questions during candidate onboarding."""

    DEEP_INTERVIEW_SYSTEM_PROMPT = (
        "Ты — топовый карьерный коуч и технический интервьюер уровня VP of Engineering / CTO. "
        "Твоя задача — провести глубокое, доброжелательное, но дотошное интервью с IT-специалистом, "
        "чтобы составить его убойный мастер-профиль и матрицу компетенций.\n\n"
        "ПРАВИЛА ИНТЕРВЬЮ:\n"
        "1. Задавай вопросы последовательно, по 1-2 связанных вопроса за раз, не перегружай кандидата.\n"
        "2. Фокусируйся на конкретных метриках и действиях по формуле STAR/XYZ: "
        "'Что сделал (X) с помощью каких технологий (Y) и к какому бизнес-результату в цифрах это привело (Z)?'\n"
        "3. Реагируй на ответы кандидата: подмечай крутые достижения, проси раскрыть детали, если ответ слишком общий.\n"
        "4. Тематические блоки интервью:\n"
        "   - Блок 1: Текущая роль, целевые позиции, стек, ожидания по зарплате и формату (удаленка/релокация).\n"
        "   - Блок 2: Ключевой стек, сильные стороны (суперсила) и технологии, с которыми больше НЕ хочется работать.\n"
        "   - Блок 3: Топ-3 самых масштабных проекта/кейса в карьере с измеримыми результатами.\n"
        "   - Блок 4: Управленческий или архитектурный опыт, кризисные ситуации и преодоление факапов.\n"
        "   - Блок 5: Сертификаты, профильное образование, владение языками.\n"
        "5. Когда кандидат скажет 'Готово', 'Сгенерируй профиль' или вы пройдете все блоки, "
        "поблагодари кандидата и сообщи, что готов синтезировать полную матрицу навыков."
    )

    FAST_TRACK_SYSTEM_PROMPT = (
        "Ты — технический рекрутер и карьерный консультант. "
        "Ты уже изучил первичное резюме кандидата. Твоя задача — задать ему несколько точечных вопросов, "
        "чтобы закрыть пробелы: вытащить недостающие оцифрованные метрики, масштаб систем и уточнить целевой карьерный трек. "
        "Задавай вопросы кратко и по делу. Не задавай больше 2 вопросов за раз."
    )

    def __init__(self, mode: str = "deep", initial_context: str = ""):
        self.mode = mode
        self.initial_context = initial_context
        self.history: List[Dict[str, str]] = []

        system_msg = self.FAST_TRACK_SYSTEM_PROMPT if mode == "fast" else self.DEEP_INTERVIEW_SYSTEM_PROMPT
        if initial_context:
            system_msg += f"\n\nКонтекст уже имеющихся документов кандидата:\n{initial_context[:8000]}"

        self.history.append({"role": "system", "content": system_msg})

    def start_message(self) -> Generator[str, None, None]:
        """Generates the initial greeting and first question."""
        if self.mode == "fast":
            prompt = (
                "Поздоровайся с кандидатом, скажи в одном предложении, что ты ознакомился с его материалами, "
                "и задай первые 2 вопроса для уточнения метрик и желаемого позиционирования."
            )
        else:
            prompt = (
                "Поздоровайся с кандидатом, объясни формат нашего интервью (10-15 минут, чтобы вытащить ключевые достижения) "
                "и задай первый блок вопросов: кем он сейчас работает и на какие целевые роли хочет позиционироваться."
            )

        self.history.append({"role": "user", "content": prompt})
        accumulated = ""
        for chunk in llm.stream_chat(self.history, temperature=0.3):
            accumulated += chunk
            yield chunk

        # Replace prompt with response in history
        self.history.pop()  # remove instruction prompt
        self.history.append({"role": "assistant", "content": accumulated})

    def send_user_response(self, user_text: str) -> Generator[str, None, None]:
        """Sends candidate response and streams next interviewer question/comment."""
        self.history.append({"role": "user", "content": user_text})
        accumulated = ""
        for chunk in llm.stream_chat(self.history, temperature=0.3):
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
