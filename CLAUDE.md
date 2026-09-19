# CLAUDE.md — Instructions for Claude Code

This repository is **Career Copilot**: an AI-driven career positioning, candidate interviewing, and resume tailoring engine.

When opened in **Claude Code**, no external API keys are needed. Claude serves directly as the AI Career Consultant and Execution Agent.

## Key CLI Commands
- Test suite: `python -m pytest -v tests`
- Standalone Markdown to Word (DOCX) compiler: `python run.py --docx -i <file.md> -o <file.docx>`
- Interactive terminal UI: `python run.py`

## Project Structure
- `templates/`: Reference templates (`skills_matrix_template.md`, SWE, DevOps, PM).
- `data/inputs/`: User's raw resumes, certificates, and portfolio notes.
- `data/skills_matrix.md`: Canonical source of truth for the candidate's experience.
- `data/vacancies/`: Target job postings (.txt, .md, .pdf).
- `data/output/<vacancy>/`: Generated package (matching analysis, tailored CVs, cover letters, DOCX).

## Operating Workflows
1. **Candidate Profiling**:
   - If user asks for an interview or profile creation: review `data/inputs/`, conduct structured STAR/XYZ interview in chat, and write `data/skills_matrix.md`.
2. **Job Tailoring**:
   - When a job vacancy is provided: match requirements, generate `matching_analysis.md`, tailored CVs (`CV_Tailored_RU.md`, `CV_Tailored_EN.md`), and `Cover_Letter.md`.
   - Always run `python run.py --docx` on each generated markdown file to compile styled DOCX documents.
