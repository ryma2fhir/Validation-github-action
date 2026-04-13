#!/usr/bin/env python3
"""Install FHIR package dependencies from package.json"""

import json
import requests
import sys
import time
import os
import base64
from dotenv import load_dotenv


load_dotenv()  # does nothing if no .env file exists, so safe to leave in

def check_package_locally(package_id, version, root):
    name = f"{package_id}#{version}.tgz"
    for _, _, files in os.walk(f"{root}/packages"):
        if name in files:
            return True
    return False

    
def download_package(package_id, version, root):
    url = f"https://packages.simplifier.net/{package_id}/{version}"
    response = requests.get(url)
    
    if response.status_code == 404:
        print(f"Package {package_id}#{version} not found on registry")
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
    print(os.getcwd())
    ROOT = f"{os.getcwd()}/Validation-github-action"
    PACKAGE_PATH = f"{ROOT}/test/package.json"
    SERVER_URL = "http://localhost:8080/fhir"

    print(PACKAGE_PATH)
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
    
    failed = []
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
            failed.append(f"{package_id}#{version}")
    
    if failed:
        print(f"\nFailed to install {len(failed)} packages:")
        for pkg in failed:
            print(f"  - {pkg}")
        return 1
    
    print(f"\nSuccessfully installed {num_packages} packages")
    return 0

if __name__ == "__main__":
    sys.exit(main())
