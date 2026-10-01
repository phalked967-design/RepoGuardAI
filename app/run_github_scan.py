import sys

from github_scanner import scan_github_repository
from report import save_report
from ai_analyzer import analyze_report


if len(sys.argv) != 2:
    print("Usage: python app\\run_github_scan.py <github_repo_url>")
    raise SystemExit(1)


repo_url = sys.argv[1]

result = scan_github_repository(repo_url)

json_file, md_file = save_report(result)

print("GitHub scan completed.")
print(f"JSON report: {json_file}")
print(f"Markdown report: {md_file}")

analysis = analyze_report()

from pathlib import Path

ai_file = Path("reports/ai_analysis.md")

ai_file.write_text(
    "# RepoGuard AI — AI Analysis\n\n" + analysis,
    encoding="utf-8"
)

print("AI analysis completed.")
print(f"AI report: {ai_file}")