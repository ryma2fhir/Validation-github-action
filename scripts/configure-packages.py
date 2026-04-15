#!/usr/bin/env python3
"""Install FHIR package dependencies from package.json"""

import json
import requests
import sys
import time
import os
import base64


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

with open(config_path,"r") as f:
    config = json.load(f)

ROOT = '.'
SERVER_URL = config["fhir-validator"]["base_url"]
PACKAGE_PATH = config["paths"]["package"]



def check_package_locally(package_id, version, root):
    name = f"{package_id}#{version}.tgz"
    for _, _, files in os.walk(f"{root}/packages"):
        if name in files:
            return True
    return False

    
def download_package(package_id, version, root, failed):
    url = f"https://packages.simplifier.net/{package_id}/{version}"
    response = requests.get(url)
    
    if response.status_code == 404:
        print(f"Package {package_id}#{version} not found on registry")
        new_entry=f'''{{"resourceType": "OperationOutcome","issue": ["severity": "Failure","diagnostics": "failed to find {package_id}: {version} on FHIR package Registry"]}}'''

        # If "package.json" doesn't exist, it creates it as an empty list then appends the new_entry regardless.
        failed.setdefault("package.json", []).append(new_entry)
        return False
    
    with open(f"{root}/packages/{package_id}-{version}.tgz", "wb") as f:
        f.write(response.content)
        return True
    
def install_package(package_id, version, root, server_url):
    package_path = f"{root}/packages/{package_id}-{version}.tgz"
    
    with open(package_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    params = {
        "resourceType": "Parameters",
        "parameter": [
            {
                "name": "npmContent",
                "valueBase64Binary": encoded
            }
        ]
    }
    
    response = requests.post(
        f"{server_url}/ImplementationGuide/$install",
        json=params,
        headers={"Content-Type": "application/fhir+json"}
    )
    return response


def main():

    failed = {}

    try:       
        with open(PACKAGE_PATH) as f:
            package = json.load(f)
    except FileNotFoundError:
        print("No package.json found - skipping package installation")
        return 0
    
    dependencies = package.get('dependencies', {})
    num_packages = len(dependencies)
    
    if not dependencies:
        print("No dependencies found in package.json")
        return 0
    
    print(f"Installing FHIR packages...")
    

    for package_id, version in dependencies.items():
        # Give server time between installations
        if package_id == "hl7.fhir.r4.core":
            num_packages -= 1
            continue  # Skip core package since it's already on the server
        time.sleep(2)
        print(f"\tInstalling {package_id}:{version}")
        if not check_package_locally(package_id, version, ROOT):
            download_package(package_id, version, ROOT)


        if not install_package(package_id, version, ROOT, SERVER_URL):
            new_entry=f'''{{"resourceType": "OperationOutcome","issue": ["severity": "Failure","diagnostics": "failed to $insert {package_id}: {version}"]}}'''

            # If "package.json" doesn't exist, it creates it as an empty list then appends the new_entry regardless.
            failed.setdefault("package.json", []).append(new_entry)

            
        
    
    if failed:
        print(f"\nFailed to install {len(failed)} packages:")
        for pkg, _ in failed.items():
            print(f"  - {pkg}")

        with open(f"'failed'.json",'w') as f:
            json.dump(failed,f)

        return 1
    
    print(f"\nSuccessfully installed {num_packages} packages")
    return 0

if __name__ == "__main__":
    sys.exit(main())
