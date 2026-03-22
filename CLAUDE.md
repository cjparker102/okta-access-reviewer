# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**okta-access-reviewer** — an AI-powered IAM auditing tool that connects to an Okta org via API, pulls user and access data, sends it to Claude AI for analysis, and generates a report flagging security anomalies.

Built by Christopher Parker, an IT Support Analyst with Okta Certified Professional and Security+ certifications, transitioning into an IAM Engineer role. **Explain code clearly — Christopher wants to understand every file and function, not just copy-paste.**

## Tech Stack

- Python 3
- Okta Python SDK (`okta`)
- Anthropic Python SDK (`anthropic`) for Claude API
- `python-dotenv` for environment variable management

## Project Structure

```
okta-access-reviewer/
├── src/
│   ├── okta_client.py   # Okta API connection — fetches users, app assignments, groups, admin roles
│   ├── ai_analyzer.py   # Sends Okta data to Claude API, returns analysis
│   └── report.py        # Formats Claude's analysis into a readable output report
├── examples/
│   └── sample_report.md # Example report output using fake/sanitized data
├── .env.example         # Template showing required environment variables
├── requirements.txt     # Python dependencies
└── main.py              # Entry point — orchestrates the full pipeline
```

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in env vars before running
cp .env.example .env

# Run the tool
python main.py
```

## Environment Variables

Required in `.env` (see `.env.example`):
- `OKTA_DOMAIN` — your Okta org domain (e.g. `yourorg.okta.com`)
- `OKTA_API_TOKEN` — Okta API token with read access
- `ANTHROPIC_API_KEY` — Claude API key

## Architecture / Data Flow

1. `main.py` calls `okta_client.py` to pull user data from Okta
2. The collected data is passed to `ai_analyzer.py`, which formats a prompt and sends it to Claude
3. Claude's response is passed to `report.py`, which formats and writes the final report
4. Flagged anomalies include: inactive users, over-provisioned accounts, unusual admin access

## Code Style Conventions

- Add docstrings to every function explaining what it does, its parameters, and what it returns
- Use type hints on function signatures
- Keep functions small and single-purpose — one function, one job
