"""
core/report_builder.py - Synthesizes an aggregate comparison report across all analyzed vacancies.
"""

from pathlib import Path
from typing import List, Dict, Any
from core.config import config
from core.llm import llm
from core.parser import DocumentParser


class ReportBuilder:
    """Builds an aggregate cross-vacancy analysis and ranking report."""

    @classmethod
    def generate_aggregate_report(cls, output_dir: Path = config.output_dir) -> str:
        """
        Scans all processed vacancy packages in data/output/ and builds a unified
        comparative report: vacancy_analysis_report.md
        """
        packages = []
        for pkg_dir in sorted(output_dir.iterdir()):
            if pkg_dir.is_dir():
                matching_file = pkg_dir / "matching_analysis.md"
                if matching_file.exists():
                    analysis_text = DocumentParser.read_text_file(matching_file)
                    packages.append({
                        "name": pkg_dir.name,
                        "analysis": analysis_text[:3000]
                    })

        if not packages:
            return "# Сводный отчет по вакансиям\n\nПока нет обработанных вакансий в директории `data/output/`."

        combined_analyses = "\n\n====================\n\n".join(
            f"### ВАКАНСИЯ: {p['name']}\n{p['analysis']}" for p in packages
        )

        system_prompt = (
            "Ты — карьерный аналитик и стратегический советник. "
            "Перед тобой результаты анализа нескольких целевых вакансий для одного кандидата. "
            "Составь единый комплексный аналитический отчет 'vacancy_analysis_report.md'.\n\n"
            "СТРУКТУРА ОТЧЕТА:\n"
            "# Комплексный аналитический отчет по целевым вакансиям\n\n"
            "## 1. Сводная сравнительная таблица\n"
            "| Вакансия / Компания | Оценка Fit Score (%) | Ключевые козыри | Главные риски/пробелы | Приоритет отклика (Высокий/Средний/Низкий) |\n"
            "| ... | ... | ... | ... | ... |\n\n"
            "## 2. Анализ совокупного спроса на технологии и стек\n"
            "- Какие навыки встречаются чаще всего\n"
            "- Какие смежные навыки стоит подтянуть кандидату в первую очередь\n\n"
            "## 3. Топ-3 наиболее выигрышных позиций для первоочередного отклика\n"
            "- С подробным обоснованием стратегии\n\n"
            "## 4. Рекомендации по прохождению интервью\n"
        )

        user_prompt = f"Вот выжимки анализов по {len(packages)} вакансиям:\n\n{combined_analyses}\n\nСформируй полный сводный отчет."
        report_md = llm.complete(system_prompt, user_prompt, temperature=0.2, max_tokens=4000)

        # Save to output root
        report_file = output_dir / "vacancy_analysis_report.md"
        report_file.write_text(report_md, encoding="utf-8")
        return report_md
