#!/usr/bin/env python3
"""Validate FHIR examples against profiles defined in CapabilityStatement"""

import json
import requests
import sys
from pathlib import Path
from collections import defaultdict

FHIR_BASE = "http://localhost:8080/fhir"
EXAMPLES_DIR = "examples"  # Adjust to your directory structure

def load_capability_statement():
    """Load CapabilityStatement to get profile mappings"""
    try:
        with open('capability-statement.json') as f:
            capability = json.load(f)
    except FileNotFoundError:
        print("✗ CapabilityStatement not found - run upload-capability.py first")
        sys.exit(1)
    
    # Build mapping of resourceType -> profile URL
    profile_map = {}
    
    for rest in capability.get('rest', []):
        if rest.get('mode') == 'server':
            for resource in rest.get('resource', []):
                resource_type = resource.get('type')
                profile = resource.get('profile')
                
                if resource_type and profile:
                    profile_map[resource_type] = profile
    
    print(f"Loaded profile mappings for {len(profile_map)} resource types")
    return profile_map

def validate_resource(resource, profile_url):
    """Validate a resource against a profile using $validate"""
    params = {
        "resourceType": "Parameters",
        "parameter": [
            {
                "name": "resource",
                "resource": resource
            },
            {
                "name": "profile",
                "valueString": profile_url
            }
        ]
    }
    
    response = requests.post(
        f"{FHIR_BASE}/{resource['resourceType']}/$validate",
        json=params,
        headers={"Content-Type": "application/fhir+json"}
    )
    
    return response

def main():
    profile_map = load_capability_statement()
    
    examples_path = Path(EXAMPLES_DIR)
    
    if not examples_path.exists():
        print(f"Examples directory '{EXAMPLES_DIR}' not found")
        return 0
    
    # Find all JSON example files
    example_files = list(examples_path.rglob("*.json"))
    
    if not example_files:
        print(f"No example files found in {EXAMPLES_DIR}")
        return 0
    
    print(f"\nValidating {len(example_files)} examples...")
    
    results = {
        'passed': [],
        'failed': [],
        'skipped': [],
        'errors': []
    }
    
    for file_path in sorted(example_files):
        try:
            with open(file_path) as f:
                resource = json.load(f)
            
            resource_type = resource.get('resourceType')
            resource_id = resource.get('id', file_path.name)
            
            # Look up required profile
            profile_url = profile_map.get(resource_type)
            
            if not profile_url:
                print(f"⊘ Skipped {resource_type}/{resource_id} - no profile in CapabilityStatement")
                results['skipped'].append({
                    'file': str(file_path),
                    'resourceType': resource_type,
                    'id': resource_id,
                    'reason': 'No profile defined in CapabilityStatement'
                })
                continue
            
            # Validate
            response = validate_resource(resource, profile_url)
            
            if response.status_code == 200:
                outcome = response.json()
                
                # Check if validation passed
                issues = outcome.get('issue', [])
                errors = [i for i in issues if i.get('severity') in ['error', 'fatal']]
                
                if errors:
                    print(f"✗ Failed {resource_type}/{resource_id}")
                    for error in errors:
                        print(f"  - {error.get('severity')}: {error.get('diagnostics', 'No details')}")
                    
                    results['failed'].append({
                        'file': str(file_path),
                        'resourceType': resource_type,
                        'id': resource_id,
                        'profile': profile_url,
                        'outcome': outcome
                    })
                else:
                    print(f"✓ Passed {resource_type}/{resource_id}")
                    results['passed'].append({
                        'file': str(file_path),
                        'resourceType': resource_type,
                        'id': resource_id,
                        'profile': profile_url
                    })
            else:
                print(f"✗ Validation error for {resource_type}/{resource_id}: {response.status_code}")
                results['errors'].append({
                    'file': str(file_path),
                    'resourceType': resource_type,
                    'id': resource_id,
                    'error': response.text[:200]
                })
        
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            results['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
    
    # Save detailed results
    with open('validation-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"✓ Passed:  {len(results['passed'])}")
    print(f"✗ Failed:  {len(results['failed'])}")
    print(f"⊘ Skipped: {len(results['skipped'])}")
    print(f"⚠ Errors:  {len(results['errors'])}")
    print("="*60)
    
    # Exit with error if any failures
    if results['failed'] or results['errors']:
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
