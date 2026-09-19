"""
core/parser.py - Universal document and URL parser.
Extracts text from PDF, DOCX, Markdown, Plain Text, and Web URLs.
"""

from pathlib import Path
from typing import Optional, List, Dict
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document


class DocumentParser:
    """Extracts raw text from diverse file types and URLs."""

    @staticmethod
    def read_pdf(file_path: Path) -> str:
        """Extracts text from a PDF file."""
        text_parts = []
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())
        return "\n\n".join(text_parts)

    @staticmethod
    def read_docx(file_path: Path) -> str:
        """Extracts text from a DOCX file."""
        doc = Document(file_path)
        text_parts = []
        for p in doc.paragraphs:
            if p.text.strip():
                text_parts.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_parts.append(" | ".join(row_text))
        return "\n".join(text_parts)

    @staticmethod
    def read_text_file(file_path: Path) -> str:
        """Reads plain text or markdown file with utf-8 fallback."""
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="cp1251", errors="replace")

    @classmethod
    def parse_file(cls, file_path: Path) -> str:
        """Parses a file based on its extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return cls.read_pdf(file_path)
        elif suffix in [".docx", ".doc"]:
            return cls.read_docx(file_path)
        elif suffix in [".txt", ".md", ".json", ".yaml", ".yml"]:
            return cls.read_text_file(file_path)
        else:
            # Fallback to plain text read
            return cls.read_text_file(file_path)

    @staticmethod
    def fetch_url_text(url: str, timeout: float = 12.0) -> str:
        """Fetches a vacancy webpage and extracts clean article text."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
        with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        # Remove noisy elements
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "button", "form"]):
            tag.decompose()

        # Target job content containers common across HH, LinkedIn, Habr, lever, greenhouse
        target_tags = soup.find_all(
            ["div", "section", "main", "article"],
            class_=lambda c: c and any(k in c.lower() for k in ["vacancy", "job", "description", "content", "posting"])
        )
        if target_tags:
            text = "\n".join(t.get_text(separator="\n", strip=True) for t in target_tags)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Collapse excess empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    @classmethod
    def scan_directory(cls, dir_path: Path) -> List[Dict[str, str]]:
        """Scans a directory for supported document files."""
        if not dir_path.exists():
            return []
        supported_exts = {".pdf", ".docx", ".doc", ".txt", ".md"}
        results = []
        for item in sorted(dir_path.iterdir()):
            if item.is_file() and item.suffix.lower() in supported_exts and not item.name.startswith("."):
                try:
                    content = cls.parse_file(item)
                    results.append({
                        "name": item.name,
                        "path": str(item),
                        "content": content,
                        "size": item.stat().st_size
                    })
                except Exception as e:
                    results.append({
                        "name": item.name,
                        "path": str(item),
                        "content": f"[Ошибка чтения файла: {e}]",
                        "size": item.stat().st_size
                    })
        return results
