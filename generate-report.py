#!/usr/bin/env python3
"""Generate validation report for PR comment"""

import json
import sys
from pathlib import Path

def generate_report():
    """Generate markdown report from validation results"""
    
    try:
        with open('validation-results.json') as f:
            results = json.load(f)
    except FileNotFoundError:
        return "## ⚠️ FHIR Validation Report\n\nNo validation results found."
    
    passed = results.get('passed', [])
    failed = results.get('failed', [])
    skipped = results.get('skipped', [])
    errors = results.get('errors', [])
    
    total = len(passed) + len(failed) + len(skipped) + len(errors)
    
    # Determine overall status
    if failed or errors:
        status_emoji = "❌"
        status_text = "FAILED"
    elif total == 0:
        status_emoji = "⚠️"
        status_text = "NO EXAMPLES"
    else:
        status_emoji = "✅"
        status_text = "PASSED"
    
    # Build report
    lines = [
        f"## {status_emoji} FHIR Validation Report - {status_text}",
        "",
        "### Summary",
        "",
        f"- ✅ **Passed:** {len(passed)}",
        f"- ❌ **Failed:** {len(failed)}",
        f"- ⊘ **Skipped:** {len(skipped)}",
        f"- ⚠️ **Errors:** {len(errors)}",
        "",
    ]
    
    # Failed validations
    if failed:
        lines.extend([
            "### ❌ Failed Validations",
            "",
        ])
        
        for item in failed:
            file_path = item['file']
            resource_type = item['resourceType']
            resource_id = item['id']
            profile = item['profile']
            outcome = item.get('outcome', {})
            
            lines.append(f"#### `{file_path}`")
            lines.append(f"- **Resource:** {resource_type}/{resource_id}")
            lines.append(f"- **Profile:** {profile}")
            lines.append("")
            
            # Extract error messages
            issues = outcome.get('issue', [])
            errors_list = [i for i in issues if i.get('severity') in ['error', 'fatal']]
            
            if errors_list:
                lines.append("**Errors:**")
                for error in errors_list[:5]:  # Limit to first 5 errors
                    severity = error.get('severity', 'error')
                    diagnostics = error.get('diagnostics', 'No details')
                    location = error.get('expression', [''])[0] if error.get('expression') else ''
                    
                    if location:
                        lines.append(f"- **{severity.upper()}** at `{location}`: {diagnostics}")
                    else:
                        lines.append(f"- **{severity.upper()}**: {diagnostics}")
                
                if len(errors_list) > 5:
                    lines.append(f"- *(... and {len(errors_list) - 5} more errors)*")
            
            lines.append("")
    
    # Errors
    if errors:
        lines.extend([
            "### ⚠️ Processing Errors",
            "",
        ])
        
        for item in errors:
            file_path = item.get('file', 'unknown')
            error = item.get('error', 'Unknown error')
            
            lines.append(f"- `{file_path}`: {error}")
        
        lines.append("")
    
    # Skipped
    if skipped:
        lines.extend([
            "<details>",
            "<summary>⊘ Skipped Examples (click to expand)</summary>",
            "",
        ])
        
        for item in skipped:
            file_path = item['file']
            reason = item.get('reason', 'Unknown')
            lines.append(f"- `{file_path}`: {reason}")
        
        lines.extend([
            "",
            "</details>",
            "",
        ])
    
    # Passed (collapsed)
    if passed:
        lines.extend([
            "<details>",
            "<summary>✅ Passed Examples (click to expand)</summary>",
            "",
        ])
        
        for item in passed:
            file_path = item['file']
            profile = item['profile']
            lines.append(f"- `{file_path}` → `{profile}`")
        
        lines.extend([
            "",
            "</details>",
            "",
        ])
    
    # Footer
    lines.extend([
        "---",
        f"*Validated {total} example(s) against profiles defined in CapabilityStatement*"
    ])
    
    return "\n".join(lines)

def main():
    report = generate_report()
    
    # Write to file for GitHub Actions
    with open('validation-report.md', 'w') as f:
        f.write(report)
    
    # Also print to stdout
    print(report)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
