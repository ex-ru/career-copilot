"""
core/docx_builder.py - Converts structured Markdown documents into professionally formatted DOCX files.
Features executive styling (Calibri, Navy accent headers, subtle borders, clean bullet lists).
"""

import re
from pathlib import Path
from typing import Optional, Union
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class DocxBuilder:
    """Renders Markdown into high-quality corporate DOCX documents."""

    PRIMARY_COLOR = RGBColor(46, 64, 83)     # Navy slate
    SECONDARY_COLOR = RGBColor(100, 116, 139) # Cool grey
    TEXT_COLOR = RGBColor(33, 33, 33)         # Dark charcoal
    BORDER_HEX = "2E4053"

    @classmethod
    def set_cell_margins(cls, cell, top=60, bottom=60, left=100, right=100):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    @classmethod
    def add_bottom_border(cls, paragraph, color_hex=None, size="8"):
        pPr = paragraph._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), size)
        bottom.set(qn('w:space'), '4')
        bottom.set(qn('w:color'), color_hex or cls.BORDER_HEX)
        pBdr.append(bottom)
        pPr.append(pBdr)

    @classmethod
    def add_formatted_runs(cls, paragraph, text: str, base_font_size=10, is_bold_base=False, is_italic_base=False, text_color=None):
        tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
        for token in tokens:
            if not token:
                continue
            run = paragraph.add_run()
            run.font.name = 'Calibri'
            run.font.size = Pt(base_font_size)
            if text_color:
                run.font.color.rgb = text_color
            else:
                run.font.color.rgb = cls.TEXT_COLOR

            if token.startswith('**') and token.endswith('**') and len(token) >= 4:
                run.text = token[2:-2]
                run.bold = True
                run.italic = is_italic_base
            elif token.startswith('*') and token.endswith('*') and len(token) >= 2:
                run.text = token[1:-1]
                run.bold = is_bold_base
                run.italic = True
            else:
                run.text = token
                run.bold = is_bold_base
                run.italic = is_italic_base

    @classmethod
    def render_markdown_to_docx(cls, md_text: str, output_path: Union[str, Path]) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = Document()
        # Set margins to 0.75 inches
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.7)
            section.bottom_margin = Inches(0.7)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        lines = md_text.splitlines()
        i = 0
        in_code_block = False
        table_buffer = []

        def flush_table():
            nonlocal table_buffer
            if not table_buffer:
                return
            # Parse table rows
            rows_data = []
            for row_line in table_buffer:
                if re.match(r'^\s*\|[-:\s|]+\|\s*$', row_line):
                    continue  # Separator line
                cells = [c.strip() for c in row_line.strip().strip('|').split('|')]
                if cells:
                    rows_data.append(cells)
            table_buffer = []
            if not rows_data:
                return

            num_cols = max(len(r) for r in rows_data)
            table = doc.add_table(rows=len(rows_data), cols=num_cols)
            table.autofit = True

            for r_idx, row in enumerate(rows_data):
                for c_idx in range(num_cols):
                    cell = table.cell(r_idx, c_idx)
                    cell_text = row[c_idx] if c_idx < len(row) else ""
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.05
                    is_header = (r_idx == 0)
                    cls.add_formatted_runs(p, cell_text, base_font_size=9.5, is_bold_base=is_header)
                    cls.set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

            # Spacing after table
            spacer = doc.add_paragraph()
            spacer.paragraph_format.space_before = Pt(0)
            spacer.paragraph_format.space_after = Pt(4)

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Handle Markdown Tables
            if stripped.startswith('|') and stripped.endswith('|'):
                table_buffer.append(stripped)
                i += 1
                continue
            else:
                if table_buffer:
                    flush_table()

            # Handle Code blocks
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                i += 1
                continue

            if in_code_block:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.left_indent = Inches(0.2)
                run = p.add_run(line)
                run.font.name = 'Consolas'
                run.font.size = Pt(9)
                run.font.color.rgb = cls.SECONDARY_COLOR
                i += 1
                continue

            # Empty lines
            if not stripped:
                i += 1
                continue

            # Horizontal rules
            if stripped in ['---', '***', '___']:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                cls.add_bottom_border(p, color_hex="BDC3C7", size="4")
                i += 1
                continue

            # Heading 1 (# ...)
            if stripped.startswith('# '):
                title = stripped[2:].strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                cls.add_formatted_runs(p, title, base_font_size=17, is_bold_base=True, text_color=cls.PRIMARY_COLOR)
                cls.add_bottom_border(p, color_hex=cls.BORDER_HEX, size="10")
                i += 1
                continue

            # Heading 2 (## ...)
            if stripped.startswith('## '):
                title = stripped[3:].strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.keep_with_next = True
                cls.add_formatted_runs(p, title, base_font_size=13, is_bold_base=True, text_color=cls.PRIMARY_COLOR)
                cls.add_bottom_border(p, color_hex="7F8C8D", size="6")
                i += 1
                continue

            # Heading 3 (### ...)
            if stripped.startswith('### '):
                title = stripped[4:].strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.keep_with_next = True
                cls.add_formatted_runs(p, title, base_font_size=11, is_bold_base=True, text_color=cls.PRIMARY_COLOR)
                i += 1
                continue

            # Bullet points
            bullet_match = re.match(r'^(\s*)[-*+]\s+(.*)$', line)
            if bullet_match:
                indent_level = len(bullet_match.group(1)) // 2
                bullet_text = bullet_match.group(2)
                p = doc.add_paragraph(style='List Bullet')
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.15
                if indent_level > 0:
                    p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
                cls.add_formatted_runs(p, bullet_text, base_font_size=10)
                i += 1
                continue

            # Numbered lists
            num_match = re.match(r'^(\s*)\d+\.\s+(.*)$', line)
            if num_match:
                item_text = num_match.group(2)
                p = doc.add_paragraph(style='List Number')
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.15
                cls.add_formatted_runs(p, item_text, base_font_size=10)
                i += 1
                continue

            # Blockquotes (> ...)
            if stripped.startswith('>'):
                quote_text = stripped.lstrip('> ').strip()
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.left_indent = Inches(0.3)
                cls.add_formatted_runs(p, quote_text, base_font_size=9.5, is_italic_base=True, text_color=cls.SECONDARY_COLOR)
                i += 1
                continue

            # Standard paragraph
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            cls.add_formatted_runs(p, stripped, base_font_size=10)
            i += 1

        if table_buffer:
            flush_table()

        doc.save(output_path)
        return output_path
