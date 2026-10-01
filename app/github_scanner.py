import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from scanner import scan_repository


def scan_github_repository(repo_url: str):
    repo_name = Path(urlparse(repo_url).path).stem

    if not repo_name:
        raise ValueError("Invalid GitHub repository URL.")

    temp_dir = Path(tempfile.mkdtemp(prefix="repoguard_"))

    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(temp_dir)],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        result = scan_repository(str(temp_dir))
        result["repository"] = repo_name

        return result

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("Usage: python app\\github_scanner.py <github_repo_url>")
        raise SystemExit(1)

    result = scan_github_repository(sys.argv[1])

    print(json.dumps(result, indent=2))