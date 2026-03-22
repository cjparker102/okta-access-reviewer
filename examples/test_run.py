"""
test_run.py

A test script that runs the full analyzer → report pipeline using
fake_users.json instead of hitting the real Okta API.

Use this to:
  - Test that your ANTHROPIC_API_KEY is working
  - See what a real report looks like before connecting to Okta
  - Develop and tweak the prompt in ai_analyzer.py without API rate limits

Run with:
    python examples/test_run.py
"""

import json
import sys
import os

# Add the project root to Python's module search path so we can import
# from src/ even though we're running from the examples/ subfolder.
# __file__ is the path to this script; we go up one level to get the root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_analyzer import analyze
from src.report import save_report, print_summary


def load_fake_users(path: str) -> list[dict]:
    """
    Reads fake_users.json and returns it as a Python list.

    Args:
        path: Path to the JSON file containing fake user data.

    Returns:
        A list of user dicts matching the same shape as collect_all_user_data().
    """
    with open(path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    print("=" * 60)
    print("  Okta Access Reviewer — TEST MODE (fake data)")
    print("=" * 60 + "\n")

    # Build the path to fake_users.json relative to this script's location
    fake_data_path = os.path.join(os.path.dirname(__file__), "fake_users.json")

    print(f"Loading fake user data from: {fake_data_path}")
    users = load_fake_users(fake_data_path)
    print(f"Loaded {len(users)} fake users.\n")

    # Run through the exact same analyzer and report pipeline as main.py
    analysis = analyze(users)

    filepath = save_report(analysis)
    print_summary(analysis)

    print(f"Full report saved to: {filepath}\n")
