"""
ai_analyzer.py

Responsible for sending collected Okta user data to Claude and getting back
a structured security analysis. Think of this as the "brain" layer —
it takes raw facts from okta_client.py and turns them into actionable findings.
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

# How many days without a login before we consider an account "inactive".
# This is a common IAM policy threshold — adjust to match your org's policy.
INACTIVE_THRESHOLD_DAYS = 90


def build_prompt(users: list[dict]) -> str:
    """
    Converts the list of user dicts into a structured text prompt for Claude.

    The quality of AI output is heavily driven by prompt quality. We give Claude:
      1. A clear role and task description
      2. The raw data, formatted as JSON so it's unambiguous
      3. Specific instructions on what to flag and how to structure the response

    Args:
        users: The enriched user list returned by collect_all_user_data().

    Returns:
        A formatted string prompt ready to send to Claude.
    """
    # json.dumps turns our Python list into a clean JSON string.
    # indent=2 makes it human-readable (and easier for the model to parse too).
    user_data_json = json.dumps(users, indent=2)

    prompt = f"""You are a senior IAM (Identity and Access Management) security analyst performing an access review of an Okta organization.

Below is a JSON dataset of users and their current access. Each user record contains:
- login: their username/email
- status: their account status
- last_login: ISO timestamp of last login (null means they have never logged in)
- created: ISO timestamp of when the account was created
- apps: list of applications assigned to them
- groups: list of Okta groups they belong to
- admin_roles: list of Okta admin roles assigned directly to them (empty list means no admin privileges)

Today's date context: use the last_login field to identify accounts inactive for more than {INACTIVE_THRESHOLD_DAYS} days.

USER DATA:
{user_data_json}

Please analyze this data and produce a security-focused access review report. Flag the following categories of concern:

1. **Inactive Accounts** — Users who have not logged in for more than {INACTIVE_THRESHOLD_DAYS} days, or have never logged in.
2. **Over-Provisioned Accounts** — Users with an unusually large number of app assignments or group memberships compared to peers, especially if their role doesn't seem to justify broad access.
3. **Admin Privilege Concerns** — Any user with admin_roles assigned. Note whether the scope seems appropriate or excessive (e.g. SUPER_ADMIN is the highest privilege level).
4. **Never-Logged-In Accounts** — Accounts that were created but never used. These could be orphaned or onboarding failures.

For each flagged user, explain specifically *why* they are flagged and what the recommended action is (e.g. disable account, review and reduce app assignments, verify admin role is still needed).

End the report with a brief executive summary of overall risk posture (1-3 sentences).

Format your response in clean Markdown."""

    return prompt


def analyze(users: list[dict]) -> str:
    """
    Sends user data to Claude and returns the full analysis as a string.

    This function is the bridge between our Okta data and Claude's intelligence.
    It creates the Anthropic client, builds the prompt, makes the API call,
    and extracts the text response.

    Args:
        users: The enriched user list returned by collect_all_user_data().

    Returns:
        A Markdown-formatted string containing Claude's access review analysis.
    """
    # The Anthropic client automatically reads ANTHROPIC_API_KEY from the environment
    client = Anthropic()

    print("Sending data to Claude for analysis...")

    prompt = build_prompt(users)

    # messages is a list because the Claude API supports multi-turn conversations.
    # For our use case we only need one turn: we send the full prompt, Claude responds.
    # "role": "user" means this message is from us (the caller).
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    # The response comes back as a list of content blocks.
    # For a standard text response there will be exactly one block — we grab its text.
    analysis_text = message.content[0].text

    print("Analysis complete.")
    return analysis_text
