import os
import json
import sys
from collections import defaultdict

def parse_validation_output(results_file):
    """Parse your FHIR validation JSON output - adjust to match your output format"""
    with open(results_file) as f:
        data = json.load(f)

    issues = {"error": [], "warning": [], "information": []}

    for entry in data:  # adjust depending on your JSON structure
        file_path = entry.get("file", "unknown")
        for issue in entry.get("issues", []):
            severity = issue.get("severity", "").lower()
            message = issue.get("message", "")
            location = issue.get("location", "")

            if severity in issues:
                issues[severity].append({
                    "file": file_path,
                    "message": message,
                    "location": location
                })

    return issues

def group_by_file(issue_list):
    grouped = defaultdict(list)
    for issue in issue_list:
        grouped[issue["file"]].append(issue)
    return grouped

def make_file_link(file_path):
    """Create a GitHub link to the file in the repo"""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    sha = os.environ.get("GITHUB_SHA", "")
    if repo and sha:
        url = f"https://github.com/{repo}/blob/{sha}/{file_path}"
        return f'<a href="{url}"><code>{file_path}</code></a>'
    return f"<code>{file_path}</code>"

def render_section(title, emoji, issues, colour):
    grouped = group_by_file(issues)
    total = len(issues)
    file_count = len(grouped)

    html = f"""
<details>
<summary><strong>{emoji} {title} &nbsp;|&nbsp; {total} total across {file_count} file(s)</strong></summary>
<br>
"""

    if not issues:
        html += f"<p>✅ No {title.lower()} found.</p>\n"
    else:
        for file_path, file_issues in sorted(grouped.items()):
            html += f"<details>\n<summary>{make_file_link(file_path)} &nbsp;— {len(file_issues)} {title.lower()}</summary>\n<br>\n"
            html += '<table><thead><tr><th>Location</th><th>Message</th></tr></thead><tbody>\n'
            for issue in file_issues:
                location = issue.get("location") or "—"
                message = issue["message"]
                html += f"<tr><td><code>{location}</code></td><td>{message}</td></tr>\n"
            html += "</tbody></table>\n</details>\n<br>\n"

    html += "</details>\n"
    return html

def main():
    results_file = sys.argv[1] if len(sys.argv) > 1 else "validation-results.json"

    issues = parse_validation_output(results_file)

    errors = issues["error"]
    warnings = issues["warning"]
    information = issues["information"]

    summary = f"""# 🏥 FHIR Validation Summary

| Severity | Count |
|----------|-------|
| 🔴 Errors | {len(errors)} |
| 🟡 Warnings | {len(warnings)} |
| 🔵 Information | {len(information)} |

---

{render_section("Errors", "🔴", errors, "red")}

{render_section("Warnings", "🟡", warnings, "yellow")}

{render_section("Information", "🔵", information, "blue")}
"""

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "w") as f:
            f.write(summary)
        print("✅ Summary written to GitHub Actions.")
    else:
        print(summary)

if __name__ == "__main__":
    main()