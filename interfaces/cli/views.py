"""
interfaces/cli/views.py - Rich UI components, banners, tables, and renderers.
"""

from typing import List, Tuple, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.prompt import Prompt, Confirm

import sys

# Ensure UTF-8 on Windows console
if sys.platform == "win32":
    try:
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(legacy_windows=False)


def print_banner():
    """Renders the main stylish application banner."""
    banner_text = Text()
    banner_text.append("[*] CAREER COPILOT ", style="bold cyan")
    banner_text.append("v0.1.0\n", style="dim")
    banner_text.append("Автономный AI-ассистент карьерного позиционирования и адаптации резюме\n", style="italic white")
    banner_text.append("OpenAI • Google Gemini • Anthropic Claude • Ollama (Offline) • OpenRouter", style="dim green")

    console.print(Panel(banner_text, border_style="bright_blue", expand=False))


def print_status_bar(has_profile: bool, is_configured: bool, provider_name: str, model_name: str, inputs_count: int, vacancies_count: int, packages_count: int):
    """Renders quick status card."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold")
    table.add_column()
    table.add_column(style="bold")
    table.add_column()

    ai_status = f"[green][OK] {provider_name} ({model_name})[/green]" if is_configured else "[red][!] Не настроен (см. .env)[/red]"
    prof_status = "[green][OK] Заполнен (skills_matrix.md)[/green]" if has_profile else "[yellow][!] Требуется создание[/yellow]"

    table.add_row("AI Провайдер:", ai_status, "Исходные файлы:", f"{inputs_count} шт. в data/inputs/")
    table.add_row("Мастер-профиль:", prof_status, "Вакансии:", f"{vacancies_count} шт. в data/vacancies/")
    table.add_row("", "", "Готовые пакеты:", f"{packages_count} шт. в data/output/")

    console.print(Panel(table, title="[bold]Состояние системы[/bold]", border_style="cyan"))


def print_menu():
    """Prints the main interactive navigation menu."""
    menu_table = Table(show_header=False, box=None, padding=(0, 1))
    menu_table.add_column("Key", style="bold cyan", width=4)
    menu_table.add_column("Action", style="white")

    menu_table.add_row("1", "👤 Профиль соискателя (Онбординг / Аудит резюме / Карьерное интервью)")
    menu_table.add_row("2", "💼 Управление вакансиями (Файлы / Парсинг по URL / Вставка текста)")
    menu_table.add_row("3", "🎯 Адаптация резюме под вакансию (Matching + CV + Cover Letter + DOCX)")
    menu_table.add_row("4", "⚡ Пакетная адаптация под ВСЕ добавленные вакансии")
    menu_table.add_row("5", "📊 Сводный сравнительный отчет по всем вакансиям")
    menu_table.add_row("6", "⚙️ Проверить подключение к AI / Сменить модель")
    menu_table.add_row("0", "🚪 Выход")

    console.print(Panel(menu_table, title="[bold]Главное меню[/bold]", border_style="dim blue"))


def render_md(content: str):
    """Renders markdown content nicely in console."""
    console.print(Markdown(content))


def notify_success(msg: str):
    console.print(f"[bold green][OK] {msg}[/bold green]")


def notify_error(msg: str):
    console.print(f"[bold red][ERROR] {msg}[/bold red]")


def notify_info(msg: str):
    console.print(f"[bold cyan][INFO] {msg}[/bold cyan]")


def notify_warning(msg: str):
    console.print(f"[bold yellow][WARN] {msg}[/bold yellow]")

