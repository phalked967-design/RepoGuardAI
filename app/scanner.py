from pathlib import Path
import json
import re
import sys


IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}


SECRET_PATTERNS = [
    r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
    r"secret\s*=\s*['\"][^'\"]+['\"]",
    r"password\s*=\s*['\"][^'\"]+['\"]",
    r"token\s*=\s*['\"][^'\"]+['\"]",
]

SECURITY_PATTERNS = [
    (
        r"\beval\s*\(",
        "high",
        "Use of eval() detected. This can execute untrusted code."
    ),
    (
        r"\bexec\s*\(",
        "high",
        "Use of exec() detected. This can execute dynamically supplied code."
    ),
    (
        r"subprocess\.(run|call|Popen)\([^)]*shell\s*=\s*True",
        "high",
        "subprocess is used with shell=True, which can create command injection risk."
    ),
    (
        r"requests\.(get|post|put|delete)\(\s*['\"]http://",
        "medium",
        "HTTP URL detected in a requests call. HTTPS should be preferred for sensitive communication."
    ),
    (
        r"\bexcept\s*:\s*$",
        "medium",
        "Bare except detected. This can hide unexpected errors."
    ),
    (
        r"\bexcept\s+Exception\s*:",
        "low",
        "Broad Exception handling detected. Consider handling specific exceptions."
    ),
]

TECH_DEBT_PATTERNS = [
    (
        r"\bTODO\b",
        "low",
        "TODO comment detected. This may represent unfinished technical work."
    ),
    (
        r"\bFIXME\b",
        "medium",
        "FIXME comment detected. This indicates known code that may require correction."
    ),
]


def scan_repository(repo_path: str):
    root = Path(repo_path)

    if not root.exists():
        raise FileNotFoundError(f"Repository not found: {repo_path}")

    files = [
        p
        for p in root.rglob("*")
        if p.is_file()
        and not any(part in IGNORE_DIRS for part in p.parts)
    ]

    extensions = {}

    for file in files:
        ext = file.suffix.lower() or "[no extension]"
        extensions[ext] = extensions.get(ext, 0) + 1

    findings = []

    has_readme = any(
        file.name.lower() in {"readme.md", "readme.txt"}
        for file in files
    )

    has_tests = any(
        "test" in part.lower()
        for file in files
        for part in file.parts
    )

    has_docker = any(
        file.name.lower()
        in {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}
        for file in files
    )

    has_ci = any(
        ".github" in file.parts and "workflows" in file.parts
        for file in files
    )

    has_requirements = any(
        file.name.lower()
        in {
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "pom.xml",
            "build.gradle",
        }
        for file in files
    )

    if not has_readme:
        findings.append({
            "severity": "medium",
            "category": "documentation",
            "issue": "README documentation is missing."
        })

    if not has_tests:
        findings.append({
            "severity": "medium",
            "category": "testing",
            "issue": "No obvious test files or test directories were detected."
        })

    if not has_requirements:
        findings.append({
            "severity": "low",
            "category": "dependencies",
            "issue": "No common dependency manifest was detected."
        })

    if not has_ci:
        findings.append({
            "severity": "low",
            "category": "ci_cd",
            "issue": "No GitHub Actions workflow was detected."
        })

    if not has_docker:
        findings.append({
            "severity": "low",
            "category": "deployment",
            "issue": "No Docker configuration was detected."
        })

    for file in files:
        try:
            text = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except Exception:
            continue

        relative_path = str(file.relative_to(root))
        lines = text.splitlines()

        for line_number, line in enumerate(lines, start=1):

            for pattern in SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "severity": "high",
                        "category": "security",
                        "issue": "Possible hard-coded secret detected.",
                        "file": relative_path,
                        "line": line_number
                    })
                    break

            for pattern, severity, issue in SECURITY_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "severity": severity,
                        "category": "security",
                        "issue": issue,
                        "file": relative_path,
                        "line": line_number
                    })

            for pattern, severity, issue in TECH_DEBT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "severity": severity,
                        "category": "technical_debt",
                        "issue": issue,
                        "file": relative_path,
                        "line": line_number
                    })

    python_files = extensions.get(".py", 0)

    javascript_files = (
        extensions.get(".js", 0)
        + extensions.get(".jsx", 0)
        + extensions.get(".ts", 0)
        + extensions.get(".tsx", 0)
    )

    return {
        "repository": root.name,
        "total_files": len(files),
        "python_files": python_files,
        "javascript_typescript_files": javascript_files,
        "extensions": extensions,
        "findings": findings,
    }


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python app\\scanner.py <repository_path>")
        raise SystemExit(1)

    result = scan_repository(sys.argv[1])

    print(json.dumps(result, indent=2))