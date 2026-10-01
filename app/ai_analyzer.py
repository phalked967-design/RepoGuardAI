import json
from pathlib import Path

import requests


MODEL = "qwen2.5-coder:1.5b"
OLLAMA_URL = "http://localhost:11434/api/chat"


def analyze_report():
    report_path = Path("reports/scan_report.json")

    if not report_path.exists():
        raise FileNotFoundError("Scan report not found.")

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    prompt = f"""
You are RepoGuard AI, a software engineering code-review agent.

Analyze the following repository scan results.

Repository:
{report["repository"]}

Total files:
{report["total_files"]}

Python files:
{report["python_files"]}

JavaScript/TypeScript files:
{report["javascript_typescript_files"]}

Findings:
{json.dumps(report["findings"], indent=2)}

Produce a concise engineering report with exactly these sections:

1. Risk Summary
2. Findings Explained
3. Recommended Actions
4. Priority Order

Do not invent problems that are not supported by the scan results.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        },
        timeout=300
    )

    response.raise_for_status()

    data = response.json()
    return data["message"]["content"]


if __name__ == "__main__":
    result = analyze_report()

    output = Path("reports/ai_analysis.md")

    output.write_text(
        "# RepoGuard AI — AI Analysis\n\n" + result,
        encoding="utf-8"
    )

    print("AI analysis completed.")
    print(f"Report saved to: {output}")