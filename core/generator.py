"""
core/generator.py - Generates tailored CVs, Cover Letters, and DOCX packages for target vacancies.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from core.config import config
from core.llm import llm
from core.matcher import JobMatcher
from core.docx_builder import DocxBuilder


class PackageGenerator:
    """Orchestrates generation of matching analysis, tailored CVs, Cover Letters, and DOCX files."""

    @classmethod
    def generate_tailored_cv(
        cls,
        profile_md: str,
        vacancy_text: str,
        matching_analysis: str,
        lang: str = "ru"
    ) -> str:
        """Generates role-tailored CV in specified language (RU or EN)."""
        lang_instruction = (
            "Пиши на чистом русском языке с международной IT-терминологией."
            if lang == "ru"
            else "Write in fluent, professional English (international tech resume standard, action-oriented verbs)."
        )

        system_prompt = (
            "Ты — главный специалист по подготовке топ-уровневых резюме для IT-индустрии. "
            "Твоя цель — адаптировать резюме кандидата под конкретную вакансию на основе проведенного анализа совпадения.\n\n"
            f"ЯЗЫК ДОКУМЕНТА: {lang_instruction}\n\n"
            "ЖЕСТКИЕ ПРАВИЛА:\n"
            "1. НЕ придумывай опыт и не искажай факты. Используй только реальный бэкграунд из мастер-профиля.\n"
            "2. Перефразируй и структурируй формулировки так, чтобы релевантный вакансии опыт стоял на первом месте.\n"
            "3. Используй формат STAR/XYZ: 'Глагол действия + контекст + оцифрованный результат/метрика'.\n"
            "4. Включи ключевые слова из вакансии для успешного прохождения ATS-систем.\n"
            "5. Структура резюме:\n"
            "   # [Имя Фамилия Кандидата]\n"
            "   [Целевая позиция] | [Контакты / Локация / Формат]\n"
            "   ## Профессиональное резюме (Summary)\n"
            "   ## Ключевые компетенции и стек (Core Competencies & Tech Stack)\n"
            "   ## Опыт работы (Work Experience: Компания, Роль, Период, Достижения, Стек)\n"
            "   ## Сертификаты и образование (Certifications & Education)\n"
        )

        user_prompt = (
            f"--- АНАЛИЗ СООТВЕТСТВИЯ ВАКАНСИИ ---\n{matching_analysis[:6000]}\n\n"
            f"--- ВАКАНСИЯ ---\n{vacancy_text[:6000]}\n\n"
            f"--- МАСТЕР-ПРОФИЛЬ КАНДИДАТА ---\n{profile_md[:12000]}\n\n"
            f"Сформируй адаптированное резюме на языке: {lang.upper()}."
        )

        return llm.complete(system_prompt, user_prompt, temperature=0.25, max_tokens=3500)

    @classmethod
    def generate_cover_letter(
        cls,
        profile_md: str,
        vacancy_text: str,
        matching_analysis: str,
        lang: str = "ru"
    ) -> str:
        """Generates personalized, high-converting Cover Letter."""
        lang_instruction = (
            "Пиши на русском языке в профессиональном, доброжелательном и энергичном тоне."
            if lang == "ru"
            else "Write in professional, engaging, confident English."
        )

        system_prompt = (
            "Ты — карьерный стратег. Напиши лаконичное, персонализированное сопроводительное письмо (Cover Letter) "
            "под конкретную вакансию.\n\n"
            f"ЯЗЫК: {lang_instruction}\n\n"
            "СТРУКТУРА ПИСЬМА (3-4 коротких абзаца, не более 200-250 слов):\n"
            "1. Приветствие и четкое позиционирование (на какую роль откликаюсь и почему этот профиль идеален).\n"
            "2. Ключевая ценность: 2-3 конкретных факта/проекта из опыта, напрямую закрывающие боли вакансии.\n"
            "3. Релевантные детали (локация, готовность к формату, знание стека).\n"
            "4. Call to Action: вежливое приглашение на 15-минутный звонок для обсуждения задач команды."
        )

        user_prompt = (
            f"--- АНАЛИЗ СООТВЕТСТВИЯ ---\n{matching_analysis[:4000]}\n\n"
            f"--- ВАКАНСИЯ ---\n{vacancy_text[:4000]}\n\n"
            f"--- ПРОФИЛЬ КАНДИДАТА ---\n{profile_md[:6000]}\n\n"
            f"Сформируй идеальный Cover Letter на языке: {lang.upper()}."
        )

        return llm.complete(system_prompt, user_prompt, temperature=0.3, max_tokens=1500)

    @classmethod
    def process_vacancy_package(
        cls,
        vacancy_title: str,
        vacancy_text: str,
        profile_md: str,
        language_mode: Optional[str] = None,
        output_dir: Optional[Path] = None,
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Runs the full pipeline for a single vacancy:
        1. Matching Analysis -> MD
        2. Tailored CV -> MD & DOCX (RU and/or EN)
        3. Cover Letter -> MD & DOCX (RU and/or EN)
        """
        output_base = output_dir or config.output_dir
        # Sanitize folder name
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in vacancy_title).strip("_")
        pkg_dir = output_base / safe_name
        pkg_dir.mkdir(parents=True, exist_ok=True)

        mode = language_mode or config.default_language
        detected_lang = JobMatcher.detect_language(vacancy_text)

        languages_to_build = []
        if mode == "both":
            languages_to_build = ["ru", "en"]
        elif mode in ["ru", "en"]:
            languages_to_build = [mode]
        else:
            languages_to_build = [detected_lang]

        created_files = []

        # Step 1: Matching analysis
        if progress_callback:
            progress_callback(f"Анализирую требования вакансии '{vacancy_title}'...")
        matching_md = JobMatcher.analyze_match(profile_md, vacancy_text, vacancy_title)
        matching_file = pkg_dir / "matching_analysis.md"
        matching_file.write_text(matching_md, encoding="utf-8")
        created_files.append(str(matching_file))

        # Step 2: Documents per language
        for lang in languages_to_build:
            lang_suffix = f"_{lang.upper()}" if len(languages_to_build) > 1 else ""

            # Tailored CV
            if progress_callback:
                progress_callback(f"Генерирую адаптированное резюме ({lang.upper()})...")
            cv_md = cls.generate_tailored_cv(profile_md, vacancy_text, matching_md, lang=lang)
            cv_md_file = pkg_dir / f"CV_Tailored{lang_suffix}.md"
            cv_md_file.write_text(cv_md, encoding="utf-8")
            created_files.append(str(cv_md_file))

            # Compile CV DOCX
            if progress_callback:
                progress_callback(f"Компилирую DOCX резюме ({lang.upper()})...")
            cv_docx_file = pkg_dir / f"CV_Tailored{lang_suffix}.docx"
            DocxBuilder.render_markdown_to_docx(cv_md, cv_docx_file)
            created_files.append(str(cv_docx_file))

            # Cover letter
            if progress_callback:
                progress_callback(f"Формирую Cover Letter ({lang.upper()})...")
            cl_md = cls.generate_cover_letter(profile_md, vacancy_text, matching_md, lang=lang)
            cl_md_file = pkg_dir / f"Cover_Letter{lang_suffix}.md"
            cl_md_file.write_text(cl_md, encoding="utf-8")
            created_files.append(str(cl_md_file))

            # Compile Cover Letter DOCX
            cl_docx_file = pkg_dir / f"Cover_Letter{lang_suffix}.docx"
            DocxBuilder.render_markdown_to_docx(cl_md, cl_docx_file)
            created_files.append(str(cl_docx_file))

        return {
            "vacancy_title": vacancy_title,
            "directory": str(pkg_dir),
            "files": created_files,
            "detected_language": detected_lang
        }
