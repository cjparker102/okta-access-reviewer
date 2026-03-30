"""
report.py

Responsible for writing the AI analysis to a file and printing a
summary to the terminal. Think of this as the "output" layer —
it takes the finished analysis and delivers it in a useful format.
"""

import os
from datetime import datetime


def save_report(analysis: str, output_dir: str = "reports") -> str:
    """
    Writes the analysis to a timestamped Markdown file.

    We timestamp the filename so that running the tool multiple times
    doesn't overwrite previous reports — you get a history of reviews.
    That's useful for showing an auditor that reviews happen regularly.

    Args:
        analysis:   The Markdown string returned by ai_analyzer.analyze().
        output_dir: The folder to write reports into. Defaults to "reports/".

    Returns:
        The full file path of the saved report (so main.py can tell the user where it is).
    """
    # Create the output directory if it doesn't exist yet.
    # exist_ok=True means "don't raise an error if the folder is already there".
    os.makedirs(output_dir, exist_ok=True)

    # Build a timestamp string like "2026-03-22_14-05-30" for the filename.
    # We replace colons with dashes because colons are not valid in filenames on Windows.
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"access_review_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    # Add a header block at the top of the file with metadata.
    # This makes the report self-contained — anyone reading it knows
    # when it was generated and what tool produced it.
    header = f"""# Okta Access Review Report

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
**Tool:** okta-access-reviewer
**Engine:** AI-powered analysis

---

"""

    with open(filepath, "w") as f:
        f.write(header + analysis)

    return filepath


def print_summary(analysis: str) -> None:
    """
    Prints a brief terminal summary so the user gets immediate feedback
    without having to open the report file.

    We scan the analysis for lines that start with "##" — those are the
    section headers Claude was instructed to use. Printing them gives a
    quick table of contents of what was found.

    Args:
        analysis: The Markdown string returned by ai_analyzer.analyze().
    """
    print("\n" + "=" * 60)
    print("ACCESS REVIEW COMPLETE — FINDINGS OVERVIEW")
    print("=" * 60)

    # Walk through every line and print the section headers (## lines).
    # This gives a quick overview without dumping the whole report to the terminal.
    for line in analysis.splitlines():
        if line.startswith("## "):
            print(f"  • {line[3:].strip()}")

    print("=" * 60 + "\n")
