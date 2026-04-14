#!/usr/bin/env python3
"""Upload FHIR conformance resources (StructureDefinitions, ValueSets, CodeSystems, etc.)"""

import json
import requests
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import os



load_dotenv()  # does nothing if no .env file exists, so safe to leave in

ROOT = os.getenv("ROOT")
PACKAGE_PATH = os.getenv("PACKAGE_PATH")
SERVER_URL = os.getenv("SERVER_URL")

ASSETS_FOLDERS = [
    "CapabilityStatement",
    "StructureDefinition",
    "ImplementationGuide",
    "SearchParameter",
    "MessageDefinition",
    "OperationDefinition",
    "CompartmentDefinition",
    "StructureMap",
    "GraphDefinition",
    "ExampleScenario",
    "CodeSystem",
    "ValueSet",
    "ConceptMap",
    "NamingSystem",
    "TerminologyCapabilities",
    "Conformance-resources"
]
EXAMPLES_FOLDERS = "examples"

FHIR_BASE = "http://localhost:8080/fhir"
ASSETS_DIR = "fhir"  # Adjust to your directory structure

def get_json_info(file_path):
    try:
        with open(file_path) as f:
            resource = json.load(f)
        
        resource_type = resource.get('resourceType')
        resource_id = resource.get('id')

        return resource, resource_id, resource_type
    
    except Exception as e:
        print(f"Error getting resource id and resource type for {file_path}: {e}")
        return False

def get_xml_info(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    
        NS = "{http://hl7.org/fhir}"
        resource_type = root.tag.replace(NS, "")
        
        id_element = root.find(f"{NS}id")
        resource_id = id_element.get("value")

        with open(file_path) as f:
            resource = f.read()

        return resource, resource_id, resource_type
    
    except Exception as e:
        print(f"Error getting resource id and/or resource type for {file_path}: {e}")
        return False

def upload_resource(file_path,resource, resource_id, resource_type, format):
    """Upload a single FHIR resource"""
    try:
        # Use PUT with id for idempotency
        url = f"{FHIR_BASE}/{resource_type}/{resource_id}"
        if format == "xml":
            response = requests.put(
                url,
                data=resource,
                headers={"Content-Type": "application/fhir+xml"}
            )
        else:
            response = requests.put(
                url,
                json=resource,
                headers={"Content-Type": "application/fhir+json"}
            )

        
        if response.status_code in [200, 201]:
            print(f"Uploaded {resource_type}/{resource_id}")
            return True
        else:
            print(f"Failed to upload {resource_type}/{resource_id}: {response.status_code}")
            print(f"  File: {file_path}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")
        return False
    
def validate_resources(file_path, resource, resource_id, resource_type, format):
    # Simple validation using $validate
    try:
        params = {
            "resourceType": "Parameters",
            "parameter": [
                {
                    "name": "resource",
                    "resource": resource
                }
            ]
        }
        
        url = f"{FHIR_BASE}/{resource_type}/{resource_id}"
        if format == "xml":
            response = requests.put(
                url,
                data=resource,
                headers={"Content-Type": "application/fhir+xml"}
            )
        else:
            response = requests.put(
                url,
                json=resource,
                headers={"Content-Type": "application/fhir+json"}
            )
        
        if response.status_code == 200:
            outcome = response.json()
            issues = outcome.get('issue', [])
            errors = [i for i in issues if i.get('severity') in ['error', 'fatal']]
            
            if errors:
                print(f"Invalid {resource_type}/{resource_id}")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"  - {error.get('diagnostics', 'No details')}")
                return False
            else:
                print(f"Valid {resource_type}/{resource_id}")
                return True
        else:
            print(f"Validation failed for {resource_type}/{resource_id}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error validating {file_path}: {e}")
        return False

def main():
    failed = []
    total = 0

    for folder in ASSETS_FOLDERS:
        assets_path = Path(ROOT) / folder
    
        if not assets_path.exists():
            continue
        
        # Find all JSON files (conformance resources)
        json_files = list(assets_path.rglob("*.json"))
        xml_files = list(assets_path.rglob("*.xml"))

        total += len(json_files) + len(xml_files)
        
        if not json_files or not xml_files:
            continue
        
        print(f"Uploading {len(json_files)} FHIR assets...")
                
        all_files = [(f, "json") for f in sorted(json_files)] + [(f, "xml") for f in sorted(xml_files)]

        for file_path, format in all_files:
            get_info = get_json_info if format == "json" else get_xml_info
            result = get_info(file_path)
            
            if result is False:
                failed.append(str(file_path))
                continue
            
            resource, resource_id, resource_type = result
            
            if not upload_resource(file_path, resource, resource_id, resource_type, format):
                failed.append(str(file_path))
    
    if failed:
        print(f"\nFailed to upload {len(failed)} assets:")
        for f in failed:
            print(f"  - {f}")
        return 1
    
    print(f"\nSuccessfully uploaded all {total} assets")
    return 0

if __name__ == "__main__":
    sys.exit(main())
