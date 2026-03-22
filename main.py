"""
main.py

The entry point for okta-access-reviewer. This is the file you run to
kick off the full pipeline. Its only job is to orchestrate the three
modules in the correct order and handle any top-level errors gracefully.

Run with:
    python main.py
"""

import asyncio
import sys

from src.okta_client import build_okta_client, collect_all_user_data
from src.ai_analyzer import analyze
from src.report import save_report, print_summary


async def main():
    """
    Orchestrates the full access review pipeline:
        1. Connect to Okta and collect user data
        2. Send data to Claude for analysis
        3. Save the report and print a summary

    This function is async because okta_client.py uses async functions —
    anything that calls an async function must itself be async.
    """
    print("=" * 60)
    print("  Okta Access Reviewer")
    print("=" * 60 + "\n")

    # Step 1: Build the Okta client and pull all user data
    client = build_okta_client()
    users = await collect_all_user_data(client)

    if not users:
        print("No users found. Check your OKTA_DOMAIN and OKTA_API_TOKEN.")
        sys.exit(1)

    # Step 2: Send the collected data to Claude for analysis
    analysis = analyze(users)

    # Step 3: Save the report to a file and print a quick summary
    filepath = save_report(analysis)
    print_summary(analysis)

    print(f"Full report saved to: {filepath}\n")


# This is the standard Python idiom for running a script.
# The block below only runs when you execute this file directly
# (e.g. `python main.py`), NOT when it's imported by another module.
# asyncio.run() starts the async event loop and runs our main() function.
if __name__ == "__main__":
    asyncio.run(main())
