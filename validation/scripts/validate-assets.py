#!/usr/bin/env python3
"""Validate FHIR conformance assets (StructureDefinitions, ValueSets, etc.) are valid FHIR"""

import json
import requests
import sys
from pathlib import Path

FHIR_BASE = "http://localhost:8080/fhir"
ASSETS_DIR = "fhir"

def validate_asset(file_path):
    """Validate a conformance resource"""
    try:
        with open(file_path) as f:
            resource = json.load(f)
        
        resource_type = resource.get('resourceType')
        resource_id = resource.get('id', file_path.name)
        
        # Simple validation using $validate
        params = {
            "resourceType": "Parameters",
            "parameter": [
                {
                    "name": "resource",
                    "resource": resource
                }
            ]
        }
        
        response = requests.post(
            f"{FHIR_BASE}/{resource_type}/$validate",
            json=params,
            headers={"Content-Type": "application/fhir+json"}
        )
        
        if response.status_code == 200:
            outcome = response.json()
            issues = outcome.get('issue', [])
            errors = [i for i in issues if i.get('severity') in ['error', 'fatal']]
            
            if errors:
                print(f"✗ Invalid {resource_type}/{resource_id}")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"  - {error.get('diagnostics', 'No details')}")
                return False
            else:
                print(f"✓ Valid {resource_type}/{resource_id}")
                return True
        else:
            print(f"✗ Validation failed for {resource_type}/{resource_id}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error validating {file_path}: {e}")
        return False

def main():
    assets_path = Path(ASSETS_DIR)
    
    if not assets_path.exists():
        print(f"Assets directory '{ASSETS_DIR}' not found - skipping asset validation")
        return 0
    
    json_files = list(assets_path.rglob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {ASSETS_DIR}")
        return 0
    
    print(f"Validating {len(json_files)} conformance assets...")
    
    failed = []
    for file_path in sorted(json_files):
        if not validate_asset(file_path):
            failed.append(str(file_path))
    
    if failed:
        print(f"\n✗ {len(failed)} assets failed validation:")
        for f in failed:
            print(f"  - {f}")
        return 1
    
    print(f"\n✓ All {len(json_files)} assets are valid FHIR")
    return 0

if __name__ == "__main__":
    sys.exit(main())
