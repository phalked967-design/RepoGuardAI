import sys

from scanner import scan_repository
from report import save_report


if len(sys.argv) != 2:
    print("Usage: python app\\run_scan.py <repository_path>")
    raise SystemExit(1)


repo_path = sys.argv[1]

result = scan_repository(repo_path)

json_file, md_file = save_report(result)

print("Scan completed.")
print(f"JSON report: {json_file}")
print(f"Markdown report: {md_file}")
