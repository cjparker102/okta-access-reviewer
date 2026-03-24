# okta-access-reviewer

An AI-powered IAM auditing tool that connects to an Okta org, pulls user access data, and uses Claude AI to generate a security-focused access review report — flagging inactive accounts, over-provisioned users, and suspicious admin privileges.

## What It Does

1. Connects to your Okta org via API and pulls every active user's:
   - Last login timestamp
   - Assigned applications
   - Group memberships
   - Admin roles
2. Sends that data to Claude AI, which analyzes it like a senior IAM analyst
3. Outputs a timestamped Markdown report with specific findings and recommended actions

## Sample Output

See [`examples/sample_report.md`](examples/sample_report.md) for a real report generated from fake test data.

Findings are organized into four categories:
- **Inactive Accounts** — no login in 90+ days
- **Over-Provisioned Accounts** — unusually broad app/group access
- **Admin Privilege Concerns** — SUPER_ADMIN, ORG_ADMIN, APP_ADMIN assignments
- **Never-Logged-In Accounts** — created but never activated

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/cjparker102/okta-access-reviewer.git
cd okta-access-reviewer
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
OKTA_DOMAIN=yourorg.okta.com
OKTA_API_TOKEN=your-okta-api-token
ANTHROPIC_API_KEY=your-anthropic-api-key
```

**Okta API Token:** Admin Console → Security → API → Tokens → Create Token
(Requires Read-Only Administrator role or higher)

**Anthropic API Key:** [console.anthropic.com](https://console.anthropic.com)

### 3. Run

**Against your real Okta org:**
```bash
python main.py
```

**Using fake test data (no Okta needed):**
```bash
python examples/test_run.py
```

Reports are saved to `reports/access_review_TIMESTAMP.md`.

## Project Structure

```
├── src/
│   ├── okta_client.py    # Okta API connection and data collection
│   ├── ai_analyzer.py    # Claude AI integration and prompt engineering
│   └── report.py         # Report formatting and file output
├── examples/
│   ├── fake_users.json   # 10 fake users with realistic IAM issues for testing
│   ├── test_run.py       # Run the full pipeline without Okta
│   └── sample_report.md  # Example report output
├── main.py               # Entry point — orchestrates the full pipeline
├── .env.example          # Environment variable template
└── requirements.txt      # Python dependencies
```

## Tech Stack

- Python 3
- [Okta Python SDK](https://github.com/okta/okta-sdk-python)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) (Claude AI)
- python-dotenv
