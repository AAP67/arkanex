# ArkaneX

**Interview intelligence for Chief of Staff, BizOps, and Strategy roles — generates company-specific questions with evaluation rubrics, powered by Claude.**

Paste a company URL and job description, upload a candidate resume, and get 5–10 tailored interview questions with detailed scoring rubrics, red flags, and follow-ups. Export as a professional PDF to hand directly to your hiring panel.

![Demo Screenshot](assets/demo-screenshot.png)
<!-- Replace with actual screenshot -->

**[Try the Live Demo →](your-streamlit-url)**

---

## How It Works

```
Company URL → auto-scrape context
JD URL      → auto-scrape job description     → Claude Sonnet → Structured questions
Resume      → extract candidate background       (JSON output)    with rubrics
                                                       ↓
                                              PDF / Markdown / JSON export
```

You can choose between two question styles: **conversational behavioral** (past experiences, leadership, cultural fit) or **scenario-based case studies** (real-time problem solving with specific constraints and stakeholders).

Each question includes a title, scenario/context, the question itself, an evaluation rubric with "excellent" indicators and red flags, and three follow-up questions to go deeper.

## Features

- **Auto-scrape** — paste a company URL or job posting link and extract context automatically via BeautifulSoup
- **Resume parsing** — upload PDF or DOCX resumes, text extracted and fed into prompt
- **Two question modes** — conversational behavioral or scenario-based case studies
- **Evaluation rubrics** — 5–6 "excellent" indicators + 4–5 red flags per question
- **Follow-up questions** — three probing follow-ups per question for deeper assessment
- **PDF export** — professional formatted PDF with cover page and branding
- **Session save/load** — export session as JSON, reload later to continue

## Project Structure

```
├── app.py             # Full application (UI, scraping, generation, export)
├── SETUP.md           # Detailed setup and feature documentation
└── requirements.txt
```

## Quickstart

```bash
git clone https://github.com/your-repo/arkanex.git
cd arkanex
pip install -r requirements.txt
```

Add your API key to `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

```bash
streamlit run app.py
```

**Stack:** Streamlit · Claude Sonnet (Anthropic) · BeautifulSoup · ReportLab (PDF) · PyPDF2

## Built By

**[Karan Rajpal](https://www.linkedin.com/in/krajpal/)** — UC Berkeley Haas MBA '25 · LLM Validation @ Handshake AI (OpenAI/Perplexity) · Former 5th hire at Borderless Capital
