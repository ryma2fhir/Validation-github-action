#!/usr/bin/env python3
"""Upload CapabilityStatement that defines profile requirements"""

import json
import requests
import sys
from pathlib import Path

FHIR_BASE = "http://localhost:8080/fhir"
CAPABILITY_FILE = "CapabilityStatement.json"  # Adjust to your file location

def upload_capability_statement():
    """Upload the CapabilityStatement"""
    capability_path = Path(CAPABILITY_FILE)
    
    # Try common locations
    search_paths = [
        Path(CAPABILITY_FILE),
        Path("fhir") / CAPABILITY_FILE,
        Path("conformance") / CAPABILITY_FILE,
    ]
    
    for path in search_paths:
        if path.exists():
            capability_path = path
            break
    else:
        print(f"✗ CapabilityStatement not found in: {[str(p) for p in search_paths]}")
        return False
    
    try:
        with open(capability_path) as f:
            resource = json.load(f)
        
        resource_id = resource.get('id')
        
        if not resource_id:
            print("✗ CapabilityStatement must have an 'id' element")
            return False
        
        url = f"{FHIR_BASE}/CapabilityStatement/{resource_id}"
        response = requests.put(
            url,
            json=resource,
            headers={"Content-Type": "application/fhir+json"}
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ Uploaded CapabilityStatement/{resource_id}")
            
            # Save for later use by validation script
            with open('capability-statement.json', 'w') as f:
                json.dump(resource, f)
            
            return True
        else:
            print(f"✗ Failed to upload CapabilityStatement: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Error uploading CapabilityStatement: {e}")
        return False

def main():
    if upload_capability_statement():
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
