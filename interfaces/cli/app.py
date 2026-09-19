"""
interfaces/cli/app.py - Main interactive CLI loop and controllers.
"""

import sys
from pathlib import Path
from typing import List
from rich.prompt import Prompt, Confirm
from rich.table import Table

from core.config import config
from core.llm import llm
from core.parser import DocumentParser
from core.profiler import CandidateProfiler
from core.interviewer import CareerInterviewer
from core.matcher import JobMatcher
from core.generator import PackageGenerator
from core.report_builder import ReportBuilder
from interfaces.cli.views import (
    console, print_banner, print_status_bar, print_menu,
    render_md, notify_success, notify_error, notify_info, notify_warning
)


class CareerCopilotCLI:
    """Coordinates user interaction in the terminal."""

    def __init__(self):
        config.ensure_directories()

    def run(self):
        """Main event loop."""
        while True:
            console.clear()
            print_banner()

            # Inspect state
            has_profile = CandidateProfiler.has_profile()
            inputs = DocumentParser.scan_directory(config.inputs_dir)
            vacancies = DocumentParser.scan_directory(config.vacancies_dir)
            packages = [p for p in config.output_dir.iterdir() if p.is_dir() and not p.name.startswith(".")] if config.output_dir.exists() else []

            print_status_bar(
                has_profile=has_profile,
                is_configured=config.is_configured,
                provider_name=config.provider_name,
                model_name=config.model,
                inputs_count=len(inputs),
                vacancies_count=len(vacancies),
                packages_count=len(packages)
            )

            print_menu()
            choice = Prompt.ask("\n[bold cyan]Выберите действие[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "0"], default="1")

            if choice == "1":
                self.handle_profile_menu()
            elif choice == "2":
                self.handle_vacancies_menu()
            elif choice == "3":
                self.handle_single_tailoring()
            elif choice == "4":
                self.handle_batch_tailoring()
            elif choice == "5":
                self.handle_aggregate_report()
            elif choice == "6":
                self.handle_ai_settings()
            elif choice == "0":
                notify_info("До новых встреч и успешных офферов!")
                sys.exit(0)

    # --------------------------------------------------------------------------
    # 1. Profile Management
    # --------------------------------------------------------------------------
    def handle_profile_menu(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]=== УПРАВЛЕНИЕ ПРОФИЛЕМ КАНДИДАТА ===[/bold cyan]\n")

        has_profile = CandidateProfiler.has_profile()
        if has_profile:
            console.print("[green]✓ Мастер-профиль найден:[/green] data/skills_matrix.md\n")
        else:
            console.print("[yellow]! Мастер-профиль еще не сформирован.[/yellow]\n")

        console.print("1. [bold]Экспресс-режим (Fast Track):[/bold] Сканировать data/inputs/ (резюме, сертификаты) + точечные вопросы AI")
        console.print("2. [bold]Глубокое карьерное интервью:[/bold] Интерактивный диалог с AI-консультантом «с нуля»")
        console.print("3. [bold]Просмотреть текущий профиль[/bold] (skills_matrix.md)")
        console.print("4. [bold]Инициализировать из эталонного шаблона[/bold] (Software Engineer / DevOps / PM)")
        console.print("0. Вернуться в главное меню\n")

        sub = Prompt.ask("Ваш выбор", choices=["1", "2", "3", "4", "0"], default="1")

        if sub == "1":
            self.run_fast_track_profiling()
        elif sub == "2":
            self.run_deep_interview()
        elif sub == "3":
            if has_profile:
                content = CandidateProfiler.load_profile()
                console.clear()
                render_md(content)
                Prompt.ask("\n[dim]Нажмите Enter для возврата...[/dim]")
            else:
                notify_warning("Профиль еще не создан. Выберите пункт 1 или 2.")
                Prompt.ask("[dim]Enter для продолжения...[/dim]")
        elif sub == "4":
            self.handle_template_import()

    def run_fast_track_profiling(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]--- ЭКСПРЕСС-РЕЖИМ: АУДИТ ФАЙЛОВ И ТОЧЕЧНЫЕ ВОПРОСЫ ---[/bold cyan]\n")

        docs = DocumentParser.scan_directory(config.inputs_dir)
        if not docs:
            notify_warning(f"В папке '{config.inputs_dir}' не найдено файлов (PDF, DOCX, TXT, MD).")
            console.print("Положите туда ваше текущее резюме, список сертификатов или диплом и повторите запуск.\n")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        console.print(f"Найдено файлов для анализа: [bold green]{len(docs)}[/bold green]")
        for d in docs:
            console.print(f"  • {d['name']} ({d['size']} байт)")

        with console.status("[bold green]AI анализирует ваши документы и ищет зоны роста...[/bold green]"):
            audit = CandidateProfiler.audit_existing_documents(docs)

        console.print("\n[bold]Результаты аудита и ключевые вопросы:[/bold]\n")
        render_md(audit)

        if not Confirm.ask("\nХотите ответить на эти вопросы прямо сейчас для включения в профиль?", default=True):
            if Confirm.ask("Сформировать skills_matrix.md на основе текущих файлов без уточнений?", default=True):
                with console.status("[bold green]Синтезирую skills_matrix.md...[/bold green]"):
                    combined_text = "\n\n".join(d['content'] for d in docs)
                    matrix = CandidateProfiler.synthesize_skills_matrix(combined_text, "")
                    CandidateProfiler.save_profile(matrix)
                notify_success("Мастер-профиль сохранен в data/skills_matrix.md!")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        # Start targeted interviewer
        combined_text = "\n\n".join(d['content'] for d in docs)
        interviewer = CareerInterviewer(mode="fast", initial_context=combined_text)

        console.print("\n[bold cyan]Начинаем уточняющий диалог. Введите 'готово' в любой момент для завершения.[/bold cyan]\n")
        console.print("[bold blue]Интервьюер (AI):[/bold blue] ", end="")
        for chunk in interviewer.start_message():
            console.print(chunk, end="", style="white")
        console.print("\n")

        turn = 0
        while turn < 4:
            user_input = Prompt.ask("\n[bold green]Ваш ответ[/bold green]")
            if user_input.strip().lower() in ["готово", "stop", "exit", "все", "сохранить"]:
                break
            console.print("\n[bold blue]Интервьюер (AI):[/bold blue] ", end="")
            for chunk in interviewer.send_user_response(user_input):
                console.print(chunk, end="", style="white")
            console.print("\n")
            turn += 1

        with console.status("[bold green]Синтезирую обновленный профиль skills_matrix.md...[/bold green]"):
            transcript = interviewer.get_full_transcript()
            matrix = CandidateProfiler.synthesize_skills_matrix(combined_text, transcript)
            CandidateProfiler.save_profile(matrix)

        notify_success("Отлично! Мастер-профиль успешно обновлен в data/skills_matrix.md!")
        Prompt.ask("[dim]Enter для продолжения...[/dim]")

    def run_deep_interview(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]--- ГЛУБОКОЕ КАРЬЕРНОЕ ИНТЕРВЬЮ «С НУЛЯ» ---[/bold cyan]\n")
        console.print("AI-интервьюер проведет вас по ключевым вехам карьеры, чтобы извлечь оцифрованные метрики,")
        console.print("архитектурные кейсы и сформировать идеальную базу компетенций.\n")
        console.print("[dim]Подсказка: чтобы закончить в любой момент и сгенерировать профиль, напишите 'готово'.[/dim]\n")

        interviewer = CareerInterviewer(mode="deep")
        console.print("[bold blue]Интервьюер (AI):[/bold blue] ", end="")
        for chunk in interviewer.start_message():
            console.print(chunk, end="", style="white")
        console.print("\n")

        while True:
            user_input = Prompt.ask("\n[bold green]Ваш ответ[/bold green]")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in ["готово", "сохранить", "закончить", "exit", "стоп"]:
                break

            console.print("\n[bold blue]Интервьюер (AI):[/bold blue] ", end="")
            for chunk in interviewer.send_user_response(user_input):
                console.print(chunk, end="", style="white")
            console.print("\n")

        with console.status("[bold green]Синтезирую полноценную матрицу компетенций skills_matrix.md...[/bold green]"):
            transcript = interviewer.get_full_transcript()
            matrix = CandidateProfiler.synthesize_skills_matrix("", transcript)
            saved_path = CandidateProfiler.save_profile(matrix)

        notify_success(f"Интервью завершено! Мастер-профиль создан: {saved_path}")
        Prompt.ask("[dim]Enter для продолжения...[/dim]")

    def handle_template_import(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]=== ВЫБОР ЭТАЛОННОГО ШАБЛОНА ===[/bold cyan]\n")
        templates = list(config.templates_dir.glob("*.md"))
        if not templates:
            notify_warning("Шаблоны не найдены в templates/")
            Prompt.ask("[dim]Enter для продолжения...[/dim]")
            return

        for i, t in enumerate(templates, 1):
            console.print(f"{i}. [bold]{t.stem}[/bold] ({t.name})")

        choice = Prompt.ask("\nВыберите номер шаблона для копирования в профиль", default="1")
        try:
            selected = templates[int(choice) - 1]
            content = selected.read_text(encoding="utf-8")
            CandidateProfiler.save_profile(content)
            notify_success(f"Шаблон '{selected.name}' успешно скопирован в data/skills_matrix.md!")
        except Exception as e:
            notify_error(f"Ошибка выбора: {e}")
        Prompt.ask("[dim]Enter для продолжения...[/dim]")

    # --------------------------------------------------------------------------
    # 2. Vacancies Management
    # --------------------------------------------------------------------------
    def handle_vacancies_menu(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]=== УПРАВЛЕНИЕ ВАКАНСИЯМИ ===[/bold cyan]\n")

        vacancies = DocumentParser.scan_directory(config.vacancies_dir)
        if vacancies:
            table = Table(title="Текущие вакансии в data/vacancies/")
            table.add_column("№", style="dim", width=4)
            table.add_column("Название файла", style="bold cyan")
            table.add_column("Размер", justify="right")
            for idx, v in enumerate(vacancies, 1):
                table.add_row(str(idx), v["name"], f"{v['size']} б")
            console.print(table)
            console.print()
        else:
            notify_info("В папке data/vacancies/ пока нет вакансий.")

        console.print("1. [bold]Добавить вакансию по URL-ссылке[/bold] (HH, LinkedIn, Habr, корпоративный сайт)")
        console.print("2. [bold]Вставить текст вакансии вручную[/bold]")
        console.print("3. [bold]Открыть директорию data/vacancies/[/bold]")
        console.print("0. Вернуться в главное меню\n")

        sub = Prompt.ask("Ваш выбор", choices=["1", "2", "3", "0"], default="1")
        if sub == "1":
            url = Prompt.ask("Введите URL вакансии")
            if url:
                try:
                    with console.status("[bold green]Скачиваю и очищаю текст вакансии...[/bold green]"):
                        text = DocumentParser.fetch_url_text(url)
                    # Create safe filename
                    name = Prompt.ask("Короткое название для файла вакансии (например, Senior_DevOps_Fintech)", default="Job_Posting")
                    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name).strip("_") + ".txt"
                    file_path = config.vacancies_dir / safe_name
                    file_path.write_text(f"URL: {url}\n\n{text}", encoding="utf-8")
                    notify_success(f"Вакансия сохранена в data/vacancies/{safe_name} ({len(text)} символов)!")
                except Exception as e:
                    notify_error(f"Не удалось загрузить вакансию по ссылке: {e}")
            Prompt.ask("[dim]Enter для продолжения...[/dim]")

        elif sub == "2":
            name = Prompt.ask("Название для файла вакансии (например, Python_Lead_Startup)")
            safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name).strip("_") + ".txt"
            console.print("\n[bold]Вставьте текст вакансии (для завершения введите строку с одной точкой '.'):[/bold]")
            lines = []
            while True:
                line = input()
                if line.strip() == ".":
                    break
                lines.append(line)
            full_text = "\n".join(lines)
            if full_text.strip():
                file_path = config.vacancies_dir / safe_name
                file_path.write_text(full_text, encoding="utf-8")
                notify_success(f"Вакансия сохранена в data/vacancies/{safe_name}!")
            Prompt.ask("[dim]Enter для продолжения...[/dim]")

    # --------------------------------------------------------------------------
    # 3. Single Vacancy Tailoring
    # --------------------------------------------------------------------------
    def handle_single_tailoring(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]=== АДАПТАЦИЯ РЕЗЮМЕ ПОД ВАКАНСИЮ ===[/bold cyan]\n")

        if not CandidateProfiler.has_profile():
            notify_error("Сначала создайте мастер-профиль кандидата (пункт 1 меню)!")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        profile_md = CandidateProfiler.load_profile().strip()
        if len(profile_md) < 50:
            notify_error("Мастер-профиль кандидата (data/skills_matrix.md) пуст! Сначала заполните информацию о кандидате в пункте 1 меню.")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        vacancies = DocumentParser.scan_directory(config.vacancies_dir)

        if not vacancies:
            notify_warning("Нет вакансий в data/vacancies/. Добавьте вакансию через пункт 2 меню.")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        for idx, v in enumerate(vacancies, 1):
            console.print(f"{idx}. [bold]{v['name']}[/bold]")

        choice = Prompt.ask("\nВыберите номер вакансии для адаптации", default="1")
        try:
            selected = vacancies[int(choice) - 1]
        except (ValueError, IndexError):
            notify_error("Неверный номер.")
            Prompt.ask("[dim]Enter...[/dim]")
            return

        # Validate vacancy content
        if not selected["content"] or len(selected["content"].strip()) < 50:
            notify_error(f"Файл вакансии '{selected['name']}' пуст или содержит слишком мало текста (менее 50 символов)!")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        console.print("\n[bold]Языковой режим пакета:[/bold]")
        console.print("1. [bold]Both (RU + EN)[/bold] — сгенерировать резюме и Cover Letter на обоих языках")
        console.print("2. [bold]RU only[/bold] — только на русском языке")
        console.print("3. [bold]EN only[/bold] — только на английском языке")
        console.print("4. [bold]Auto[/bold] — автоматически по языку вакансии")
        lang_choice = Prompt.ask("Выбор языка", choices=["1", "2", "3", "4"], default="1")
        mode_map = {"1": "both", "2": "ru", "3": "en", "4": "auto"}
        lang_mode = mode_map[lang_choice]

        title = Path(selected["name"]).stem
        try:
            with console.status("[bold green]Генерирую полный пакет документов...[/bold green]") as status:
                def update_status(msg):
                    status.update(f"[bold green]{msg}[/bold green]")

                res = PackageGenerator.process_vacancy_package(
                    vacancy_title=title,
                    vacancy_text=selected["content"],
                    profile_md=profile_md,
                    language_mode=lang_mode,
                    progress_callback=update_status
                )

            console.print(f"\n[bold green][OK] Пакет успешно создан в каталоге:[/bold green] {res['directory']}")
            console.print("[bold]Созданные файлы:[/bold]")
            for f in res["files"]:
                console.print(f"  📄 {Path(f).name}")
        except Exception as e:
            notify_error(f"Ошибка при генерации пакета под '{title}':\n{e}")

        Prompt.ask("\n[dim]Нажмите Enter для возврата...[/dim]")

    # --------------------------------------------------------------------------
    # 4. Batch Process All Vacancies
    # --------------------------------------------------------------------------
    def handle_batch_tailoring(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]=== ПАКЕТНАЯ АДАПТАЦИЯ ПОД ВСЕ ВАКАНСИИ ===[/bold cyan]\n")

        if not CandidateProfiler.has_profile():
            notify_error("Сначала создайте мастер-профиль кандидата (пункт 1 меню)!")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        profile_md = CandidateProfiler.load_profile().strip()
        if len(profile_md) < 50:
            notify_error("Мастер-профиль кандидата (data/skills_matrix.md) пуст! Сначала заполните информацию о кандидате в пункте 1 меню.")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        vacancies = DocumentParser.scan_directory(config.vacancies_dir)

        if not vacancies:
            notify_warning("В каталоге data/vacancies/ нет вакансий для обработки.")
            Prompt.ask("[dim]Enter для возврата...[/dim]")
            return

        console.print(f"Будет обработано вакансий: [bold green]{len(vacancies)}[/bold green]")
        if not Confirm.ask("Запустить генерацию пакетов под все вакансии?", default=True):
            return

        success_count = 0
        for idx, vac in enumerate(vacancies, 1):
            title = Path(vac["name"]).stem
            console.print(f"\n[bold cyan][{idx}/{len(vacancies)}] Обработка: {title}...[/bold cyan]")
            try:
                with console.status(f"[bold green]Генерация {title}...[/bold green]") as status:
                    PackageGenerator.process_vacancy_package(
                        vacancy_title=title,
                        vacancy_text=vac["content"],
                        profile_md=profile_md,
                        progress_callback=lambda m: status.update(f"[bold green]{m}[/bold green]")
                    )
                notify_success(f"Завершена: {title}")
                success_count += 1
            except Exception as e:
                notify_error(f"Ошибка при обработке {title}: {e}")

        # Build aggregate report if at least one succeeded
        if success_count > 0:
            console.print("\n[bold cyan]Сборка сводного отчета по всем вакансиям...[/bold cyan]")
            with console.status("[bold green]Формирую vacancy_analysis_report.md...[/bold green]"):
                ReportBuilder.generate_aggregate_report()
            notify_success("Пакетная обработка завершена! Сводный отчет сохранен в data/output/vacancy_analysis_report.md")
        else:
            notify_warning("Ни одна вакансия не была успешно обработана.")
        Prompt.ask("[dim]Enter для продолжения...[/dim]")

    # --------------------------------------------------------------------------
    # 5. Aggregate Report
    # --------------------------------------------------------------------------
    def handle_aggregate_report(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]=== СВОДНЫЙ СРАВНИТЕЛЬНЫЙ ОТЧЕТ ПО ВАКАНСИЯМ ===[/bold cyan]\n")

        report_file = config.output_dir / "vacancy_analysis_report.md"
        if not report_file.exists():
            notify_info("Отчет еще не сгенерирован. Генерирую на основе имеющихся пакетов в data/output/...")
            with console.status("[bold green]Анализирую данные всех вакансий...[/bold green]"):
                content = ReportBuilder.generate_aggregate_report()
        else:
            if Confirm.ask("Обновить сводный отчет по актуальным данным?", default=False):
                with console.status("[bold green]Обновляю vacancy_analysis_report.md...[/bold green]"):
                    content = ReportBuilder.generate_aggregate_report()
            else:
                content = report_file.read_text(encoding="utf-8")

        console.clear()
        render_md(content)
        Prompt.ask("\n[dim]Нажмите Enter для возврата...[/dim]")

    # --------------------------------------------------------------------------
    # 6. AI Settings & Diagnostic
    # --------------------------------------------------------------------------
    def handle_ai_settings(self):
        console.clear()
        print_banner()
        console.print("[bold cyan]=== НАСТРОЙКИ AI И ДИАГНОСТИКА СОЕДИНЕНИЯ ===[/bold cyan]\n")

        console.print(f"• Провайдер:     [bold]{config.provider_name}[/bold]")
        console.print(f"• Модель:        [bold]{config.model}[/bold]")
        console.print(f"• Base URL:      [bold]{config.base_url or 'По умолчанию (OpenAI)'}[/bold]")
        console.print(f"• API Ключ:      [bold]{'Указан (' + config.api_key[:6] + '...)' if config.api_key else 'Отсутствует'}[/bold]\n")

        with console.status("[bold green]Тестирую соединение с AI-сервером...[/bold green]"):
            ok, message = llm.test_connection()

        if ok:
            notify_success(message)
        else:
            notify_error(message)
            console.print("\n[yellow]Подсказка:[/yellow] Отредактируйте файл [bold].env[/bold] в корне проекта для изменения ключа или провайдера.")

        Prompt.ask("\n[dim]Нажмите Enter для возврата...[/dim]")
