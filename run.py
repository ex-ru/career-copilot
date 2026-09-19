#!/usr/bin/env python3
"""
Career Copilot - Entry Point.
Run interactively:
    python run.py

Or use CLI flags:
    python run.py --test-ai
    python run.py --docx -i document.md -o document.docx
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.config import config
from core.llm import llm
from core.docx_builder import DocxBuilder
from interfaces.cli.app import CareerCopilotCLI
from interfaces.cli.views import console, notify_success, notify_error


def main():
    parser = argparse.ArgumentParser(
        description="Career Copilot: AI-Powered Career Profiling & CV Tailoring Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--test-ai", action="store_true", help="Test AI provider connection and exit")
    parser.add_argument("--docx", action="store_true", help="Standalone Markdown to DOCX converter mode")
    parser.add_argument("-i", "--input", type=str, help="Input Markdown file for DOCX converter")
    parser.add_argument("-o", "--output", type=str, help="Output DOCX file destination")

    args = parser.parse_args()

    if args.test_ai:
        console.print("[bold cyan]Тестирование AI подключения...[/bold cyan]")
        ok, msg = llm.test_connection()
        if ok:
            notify_success(msg)
            sys.exit(0)
        else:
            notify_error(msg)
            sys.exit(1)

    if args.docx:
        if not args.input:
            notify_error("Укажите входной файл с помощью -i / --input")
            sys.exit(1)
        in_path = Path(args.input)
        out_path = Path(args.output) if args.output else in_path.with_suffix(".docx")
        if not in_path.exists():
            notify_error(f"Файл {in_path} не найден!")
            sys.exit(1)
        md_text = in_path.read_text(encoding="utf-8")
        DocxBuilder.render_markdown_to_docx(md_text, out_path)
        notify_success(f"DOCX успешно сохранен: {out_path}")
        sys.exit(0)

    # Default: Interactive rich CLI
    try:
        app = CareerCopilotCLI()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[dim]Сессия прервана пользователем. До свидания![/dim]")
        sys.exit(0)


if __name__ == "__main__":
    main()
