#!/usr/bin/env python3
"""Upload FHIR conformance resources (StructureDefinitions, ValueSets, CodeSystems, etc.)"""

import json
import requests
import sys
from pathlib import Path

FHIR_BASE = "http://localhost:8080/fhir"
ASSETS_DIR = "fhir"  # Adjust to your directory structure

def upload_resource(file_path):
    """Upload a single FHIR resource"""
    try:
        with open(file_path) as f:
            resource = json.load(f)
        
        resource_type = resource.get('resourceType')
        resource_id = resource.get('id', 'unknown')
        
        # Use PUT with id for idempotency
        if resource.get('id'):
            url = f"{FHIR_BASE}/{resource_type}/{resource_id}"
            response = requests.put(
                url,
                json=resource,
                headers={"Content-Type": "application/fhir+json"}
            )
        else:
            url = f"{FHIR_BASE}/{resource_type}"
            response = requests.post(
                url,
                json=resource,
                headers={"Content-Type": "application/fhir+json"}
            )
        
        if response.status_code in [200, 201]:
            print(f"✓ Uploaded {resource_type}/{resource_id}")
            return True
        else:
            print(f"✗ Failed to upload {resource_type}/{resource_id}: {response.status_code}")
            print(f"  File: {file_path}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Error uploading {file_path}: {e}")
        return False

def main():
    assets_path = Path(ASSETS_DIR)
    
    if not assets_path.exists():
        print(f"Assets directory '{ASSETS_DIR}' not found - skipping")
        return 0
    
    # Find all JSON files (conformance resources)
    json_files = list(assets_path.rglob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {ASSETS_DIR}")
        return 0
    
    print(f"Uploading {len(json_files)} FHIR assets...")
    
    failed = []
    for file_path in sorted(json_files):
        if not upload_resource(file_path):
            failed.append(str(file_path))
    
    if failed:
        print(f"\n✗ Failed to upload {len(failed)} assets:")
        for f in failed:
            print(f"  - {f}")
        return 1
    
    print(f"\n✓ Successfully uploaded all {len(json_files)} assets")
    return 0

if __name__ == "__main__":
    sys.exit(main())
