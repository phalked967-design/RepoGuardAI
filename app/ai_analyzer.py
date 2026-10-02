import json
from pathlib import Path

import requests


MODEL = "qwen2.5-coder:1.5b"
OLLAMA_URL = "http://localhost:11434/api/chat"


def get_risk_level(findings):
    severities = {finding.get("severity") for finding in findings}

    if "high" in severities:
        return "HIGH"

    if "medium" in severities:
        return "MEDIUM"

    return "LOW"


def get_ai_explanation(finding):
    prompt = f"""
Explain this repository finding in ONE sentence only.

Finding:
{json.dumps(finding, indent=2)}

Rules:
- Return only one sentence.
- Maximum 25 words.
- Explain the practical impact of this exact finding.
- Do not mention security unless the finding is security-related.
- Do not mention Docker unless the finding is about Docker.
- Do not mention CI/CD unless the finding is about CI/CD.
- Do not suggest tools or frameworks.
- Do not change the severity.
- Do not add recommendations.
- Do not add headings.
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

    text = response.json()["message"]["content"].strip()

    # Remove accidental markdown/code formatting.
    text = text.replace("```", "").strip()

    # Keep only the first paragraph.
    text = text.split("\n\n")[0].strip()

    return text


def get_recommendation(finding):
    category = finding.get("category")

    recommendations = {
        "testing": "Add automated tests for the application's main functionality.",
        "ci_cd": "Add a GitHub Actions workflow to automate repository checks.",
        "deployment": "Add deployment configuration if containerized deployment is required.",
        "security": "Review and remediate the identified security issue.",
        "technical_debt": "Review and resolve the identified technical debt."
    }

    return recommendations.get(
        category,
        "Review the finding and apply an appropriate corrective action."
    )


def analyze_report():
    report_path = Path("reports/scan_report.json")

    if not report_path.exists():
        raise FileNotFoundError("Scan report not found.")

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    findings = report["findings"]

    risk_level = get_risk_level(findings)

    severity_order = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    sorted_findings = sorted(
        findings,
        key=lambda finding: severity_order.get(
            finding.get("severity", "low"),
            2
        )
    )

    lines = [
        "# RepoGuard AI - AI Analysis",
        "",
        "## Risk Summary",
        "",
        f"**Overall Risk Level: {risk_level}**",
        "",
        f"- High findings: {sum(f.get('severity') == 'high' for f in findings)}",
        f"- Medium findings: {sum(f.get('severity') == 'medium' for f in findings)}",
        f"- Low findings: {sum(f.get('severity') == 'low' for f in findings)}",
        ""
    ]

    if not findings:
        lines.extend([
            "## Findings Explained",
            "",
            "No issues were detected by the current scanner.",
            "",
            "## Priority Order",
            "",
            "No remediation is currently required.",
            ""
        ])

    else:
        lines.extend([
            "## Findings Explained",
            ""
        ])

        for number, finding in enumerate(sorted_findings, start=1):

            lines.extend([
                f"### {number}. {finding['issue']}",
                "",
                f"**Severity:** {finding['severity'].upper()}",
                f"**Category:** {finding.get('category', 'general')}",
            ])

            if "file" in finding:
                lines.append(f"**File:** `{finding['file']}`")

            if "line" in finding:
                lines.append(f"**Line:** {finding['line']}")

            lines.extend([
                "",
                "**Impact:**",
                get_ai_explanation(finding),
                "",
                "**Recommended fix:**",
                get_recommendation(finding),
                ""
            ])

        lines.extend([
            "## Priority Order",
            ""
        ])

        for number, finding in enumerate(sorted_findings, start=1):
            lines.append(
                f"{number}. {finding['severity'].upper()} - "
                f"{finding['issue']}"
            )

        lines.append("")

    output = Path("reports/ai_analysis.md")

    output.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return output


if __name__ == "__main__":
    output = analyze_report()

    print("AI analysis completed.")
    print(f"Report saved to: {output}")