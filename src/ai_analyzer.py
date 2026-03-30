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

    prompt = f"""You are a senior IAM (Identity and Access Management) security analyst performing a comprehensive access review of an Okta organization.

Below is a JSON dataset of users and their current access. Each user record contains:

**Identity fields:**
- login: username/email
- first_name, last_name: user's name
- status: account status (ACTIVE, STAGED, SUSPENDED, DEPROVISIONED)
- department: their department (may be null)
- title: job title (may be null)
- user_type: employee classification — "full_time", "contractor", or "service_account" (may be null)
- manager: their manager's login (null = no manager assigned)
- employee_number: employee ID (may be null)

**Access fields:**
- apps: list of applications assigned to them
- groups: list of Okta groups they belong to
- admin_roles: list of Okta admin roles assigned directly (empty = no admin privileges)

**Timeline fields:**
- created: ISO timestamp when the account was created
- last_login: ISO timestamp of last login (null = never logged in)
- password_changed: ISO timestamp of last password change (null = never changed)

**Profile completeness:**
- mobile_phone, city, state, cost_center: profile fields (null = missing)

**Pre-computed risk signals** (in risk_signals object):
- is_contractor: boolean — user_type indicates contractor
- is_service_account: boolean — login starts with "svc." or user_type is service_account
- has_no_manager: boolean — no manager assigned
- profile_incomplete: boolean — 2+ key profile fields are missing
- missing_profile_fields: list of which fields are empty
- app_count: total number of app assignments
- group_count: total number of group memberships
- department_groups: list of dept-* groups this user is in
- cross_dept_count: number of department groups outside their own department
- possible_duplicates: logins of other active accounts with the same first+last name

Today's date: use last_login to identify accounts inactive for more than {INACTIVE_THRESHOLD_DAYS} days.

USER DATA:
{user_data_json}

Analyze this data and produce a security-focused access review report. Flag ALL of the following categories:

1. **Inactive & Dormant Accounts** — Users inactive for {INACTIVE_THRESHOLD_DAYS}+ days. Pay special attention to inactive accounts that ALSO hold admin roles or sensitive group memberships (dormant admins are critical risks).

2. **Never-Logged-In Accounts (Ghost Accounts)** — Accounts created but never used. Flag how long ago they were created — older ghost accounts are higher risk. Distinguish between STAGED (never activated) and ACTIVE (activated but unused).

3. **Admin Privilege Concerns** — Every user with admin_roles. Flag: admins who have never logged in, admins with no manager (orphaned admins), service accounts with admin roles, contractors with admin roles, admins inactive for 90+ days (sleeping admins). SUPER_ADMIN is the highest privilege — any SUPER_ADMIN issue is critical.

4. **Contractor & Vendor Access Violations** — Users where is_contractor is true OR user_type is "contractor". Flag: contractors with admin roles, contractors with access to crown jewel apps (AWS prod, Okta Admin, HR Admin, Finance Admin), contractors in permanent employee groups (dept-engineering, role-managers, etc.), contractors whose accounts are old (potential overstay — contracts are typically 6-18 months).

5. **Service Account Anomalies** — Users where is_service_account is true OR login starts with "svc.". Flag: service accounts in human-facing groups (dept-*, role-executives, role-managers), service accounts with interactive app access (Zoom, Salesforce, etc.), service accounts with admin roles.

6. **Privilege Creep & Over-Provisioning** — Users with cross_dept_count >= 2 (in multiple department groups they don't belong to). Users with app_count significantly above the median. Users whose groups don't match their department.

7. **Duplicate Identities** — Users where possible_duplicates is non-empty. Two active accounts for the same person is an offboarding/rehire failure. Flag both accounts.

8. **Orphaned Accounts** — Users with has_no_manager = true AND missing department or cost center. Especially dangerous if they also have admin roles. These users are invisible in the org chart.

9. **Departed Employee Risk** — Accounts that are very old (created 2+ years ago) AND have been inactive for 12+ months. These look like employees who left but were never offboarded.

10. **Password & Credential Hygiene** — Accounts where password_changed is null (password never rotated) especially if the account is 1+ year old. Stale credentials are easy targets for credential stuffing.

11. **Incomplete Profiles** — Users where profile_incomplete is true. Missing phone, city, state, or cost center suggests rushed provisioning or legacy account import.

For each finding, assign a severity: CRITICAL, HIGH, MEDIUM, or LOW.
For each flagged user, explain specifically WHY they are flagged and the recommended remediation action.

End with an executive summary: overall risk posture, total findings by severity, and top 3 recommended actions.

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
        max_tokens=16000,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    # The response comes back as a list of content blocks.
    # For a standard text response there will be exactly one block — we grab its text.
    analysis_text = message.content[0].text

    print("Analysis complete.")
    return analysis_text
