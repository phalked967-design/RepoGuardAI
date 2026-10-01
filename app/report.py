from pathlib import Path
import json


def save_report(result, output_dir="reports"):
    output = Path(output_dir)
    output.mkdir(exist_ok=True)

    json_file = output / "scan_report.json"
    md_file = output / "scan_report.md"

    json_file.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )

    lines = [
        f"# RepoGuard AI Report",
        "",
        f"**Repository:** {result['repository']}",
        f"**Total files:** {result['total_files']}",
        f"**Python files:** {result['python_files']}",
        f"**JavaScript/TypeScript files:** {result['javascript_typescript_files']}",
        "",
        "## Findings",
        ""
    ]

    if not result["findings"]:
        lines.append("No issues detected by the current scanner.")
    else:
        for i, finding in enumerate(result["findings"], start=1):
            lines.append(
                f"### {i}. {finding['severity'].upper()}"
            )
            lines.append(f"- {finding['issue']}")

            if "files" in finding:
                lines.append("- Files:")
                for file in finding["files"]:
                    lines.append(f"  - `{file}`")

            lines.append("")

    md_file.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return json_file, md_file