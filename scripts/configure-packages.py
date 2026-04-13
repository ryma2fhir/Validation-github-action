#!/usr/bin/env python3
"""Install FHIR package dependencies from package.json"""

import json
import requests
import sys
import time

FHIR_BASE = "http://localhost:8080/fhir"

def install_package(package_id, version):
    """Install a FHIR package using $install operation"""
    params = {
        "resourceType": "Parameters",
        "parameter": [
            {"name": "id", "valueString": f"{package_id}#{version}"}
        ]
    }
    
    try:
        response = requests.post(
            f"{FHIR_BASE}/$install",
            json=params,
            headers={"Content-Type": "application/fhir+json"},
            timeout=300  # Package installation can take time
        )
        
        if response.status_code in [200, 201]:
            print(f"Installed {package_id}#{version}")
            return True
        else:
            print(f"Failed to install {package_id}#{version}: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Error installing {package_id}#{version}: {e}")
        return False

def main():
    try:
        with open('../package.json') as f:
            package = json.load(f)
    except FileNotFoundError:
        print("No package.json found - skipping package installation")
        return 0
    
    dependencies = package.get('dependencies', {})
    
    if not dependencies:
        print("No dependencies found in package.json")
        return 0
    
    print(f"Installing {len(dependencies)} FHIR packages...")
    
    failed = []
    for package_id, version in dependencies.items():
        # Give server time between installations
        time.sleep(2)
        
        if not install_package(package_id, version):
            failed.append(f"{package_id}#{version}")
    
    if failed:
        print(f"\nFailed to install {len(failed)} packages:")
        for pkg in failed:
            print(f"  - {pkg}")
        return 1
    
    print(f"\nSuccessfully installed all {len(dependencies)} packages")
    return 0

if __name__ == "__main__":
    sys.exit(main())
