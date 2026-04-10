# Example FHIR Assets Repository Structure

This shows the expected structure of your FHIR assets repository.

## Directory Structure

```
your-fhir-assets-repo/
├── .github/
│   └── workflows/
│       └── trigger-validation.yml          # Triggers validation on push/PR
│
├── fhir/                                   # Conformance resources
│   ├── StructureDefinition-CustomPatient.json
│   ├── StructureDefinition-CustomObservation.json
│   ├── ValueSet-CustomCodes.json
│   ├── CodeSystem-CustomSystem.json
│   └── ...
│
├── examples/                               # Example instances
│   ├── Patient-example1.json
│   ├── Patient-example2.json
│   ├── Observation-example1.json
│   └── ...
│
├── CapabilityStatement.json                # Defines validation rules
├── package.json                            # FHIR package dependencies
└── README.md
```

## Required Files

### 1. package.json

Defines FHIR package dependencies:

```json
{
  "name": "your-fhir-ig",
  "version": "1.0.0",
  "description": "Your FHIR Implementation Guide",
  "dependencies": {
    "hl7.fhir.r4.core": "4.0.1",
    "hl7.fhir.uv.ips": "1.1.0",
    "hl7.fhir.us.core": "6.1.0"
  }
}
```

### 2. CapabilityStatement.json

Defines which profile each resource type must conform to:

```json
{
  "resourceType": "CapabilityStatement",
  "id": "your-conformance",
  "url": "https://your-domain.org/CapabilityStatement/your-conformance",
  "version": "1.0.0",
  "name": "YourFHIRConformance",
  "status": "active",
  "date": "2024-01-01",
  "publisher": "Your Organization",
  "description": "Conformance requirements for your FHIR implementation",
  "kind": "requirements",
  "fhirVersion": "4.0.1",
  "format": [
    "application/fhir+json",
    "application/fhir+xml"
  ],
  "rest": [
    {
      "mode": "server",
      "resource": [
        {
          "type": "Patient",
          "profile": "https://your-domain.org/StructureDefinition/CustomPatient",
          "documentation": "Patient resource conformance"
        },
        {
          "type": "Observation",
          "profile": "https://your-domain.org/StructureDefinition/CustomObservation",
          "documentation": "Observation resource conformance"
        }
      ]
    }
  ]
}
```

### 3. trigger-validation.yml

Workflow to trigger validation:

```yaml
name: Trigger FHIR Validation

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'fhir/**'
      - 'examples/**'
      - 'package.json'
      - 'CapabilityStatement.json'
  
  pull_request:
    branches:
      - main
    paths:
      - 'fhir/**'
      - 'examples/**'
      - 'package.json'
      - 'CapabilityStatement.json'

jobs:
  trigger-validation:
    runs-on: ubuntu-latest
    
    steps:
      - name: Trigger validation service
        uses: peter-evans/repository-dispatch@v2
        with:
          token: ${{ secrets.PAT_TOKEN }}
          repository: ryma2fhir/Validation-github-action
          event-type: validate-fhir-assets
          client-payload: |
            {
              "repository": "${{ github.repository }}",
              "ref": "${{ github.ref }}",
              "sha": "${{ github.sha }}",
              "pr_number": "${{ github.event.pull_request.number }}",
              "triggered_by": "${{ github.actor }}",
              "event_name": "${{ github.event_name }}"
            }
      
      - name: Wait for validation to start
        run: |
          echo "Validation triggered in ryma2fhir/Validation-github-action"
          echo "Repository: ${{ github.repository }}"
          sleep 10
```

## Example Conformance Resources

### StructureDefinition (fhir/StructureDefinition-CustomPatient.json)

```json
{
  "resourceType": "StructureDefinition",
  "id": "CustomPatient",
  "url": "https://your-domain.org/StructureDefinition/CustomPatient",
  "version": "1.0.0",
  "name": "CustomPatient",
  "status": "active",
  "kind": "resource",
  "abstract": false,
  "type": "Patient",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
  "derivation": "constraint",
  "differential": {
    "element": [
      {
        "id": "Patient.identifier",
        "path": "Patient.identifier",
        "min": 1,
        "mustSupport": true
      },
      {
        "id": "Patient.name",
        "path": "Patient.name",
        "min": 1,
        "mustSupport": true
      }
    ]
  }
}
```

### ValueSet (fhir/ValueSet-CustomCodes.json)

```json
{
  "resourceType": "ValueSet",
  "id": "CustomCodes",
  "url": "https://your-domain.org/ValueSet/CustomCodes",
  "version": "1.0.0",
  "name": "CustomCodes",
  "status": "active",
  "compose": {
    "include": [
      {
        "system": "https://your-domain.org/CodeSystem/CustomSystem",
        "concept": [
          {
            "code": "code1",
            "display": "Code 1"
          },
          {
            "code": "code2",
            "display": "Code 2"
          }
        ]
      }
    ]
  }
}
```

## Example Instances

### Patient Example (examples/Patient-example1.json)

**Note:** No `meta.profile` needed - validation uses CapabilityStatement!

```json
{
  "resourceType": "Patient",
  "id": "example1",
  "identifier": [
    {
      "system": "https://your-domain.org/identifiers",
      "value": "12345"
    }
  ],
  "name": [
    {
      "family": "Smith",
      "given": ["John"]
    }
  ],
  "gender": "male",
  "birthDate": "1970-01-01"
}
```

### Observation Example (examples/Observation-example1.json)

```json
{
  "resourceType": "Observation",
  "id": "example1",
  "status": "final",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "85354-9",
        "display": "Blood pressure"
      }
    ]
  },
  "subject": {
    "reference": "Patient/example1"
  },
  "effectiveDateTime": "2024-01-01T10:00:00Z",
  "valueQuantity": {
    "value": 120,
    "unit": "mmHg",
    "system": "http://unitsofmeasure.org",
    "code": "mm[Hg]"
  }
}
```

## Alternative Directory Structures

If your repo uses different paths, update the validation workflow.

### Option 1: Flat structure

```
your-repo/
├── StructureDefinition-*.json    # All in root
├── ValueSet-*.json
├── Patient-example.json
├── Observation-example.json
├── CapabilityStatement.json
└── package.json
```

Update `validation-service.yml`:
```yaml
cp assets/*.json validation/fhir/
```

### Option 2: Different naming

```
your-repo/
├── resources/              # Instead of "fhir"
│   └── *.json
├── instances/              # Instead of "examples"
│   └── *.json
└── ...
```

Update `validation-service.yml`:
```yaml
cp -r assets/resources/* validation/fhir/
cp -r assets/instances/* validation/examples/
```

### Option 3: Multiple IGs

```
your-repo/
├── ig-core/
│   ├── fhir/
│   ├── examples/
│   ├── CapabilityStatement.json
│   └── package.json
└── ig-extensions/
    ├── fhir/
    └── examples/
```

Update workflow to validate each IG separately.

## Validation Behavior

### What Gets Validated

1. **Conformance Resources** (fhir/*.json)
   - Validated as valid FHIR resources
   - Uploaded to HAPI FHIR server
   - Used as validation targets

2. **Examples** (examples/*.json)
   - Validated against profiles from CapabilityStatement
   - No `meta.profile` required
   - Profile determined by resourceType

### Validation Rules

| Resource Type | Profile (from CapabilityStatement) | Result |
|--------------|-----------------------------------|--------|
| Patient | https://your-domain.org/StructureDefinition/CustomPatient | Validated |
| Observation | https://your-domain.org/StructureDefinition/CustomObservation | Validated |
| Condition | (not in CapabilityStatement) | Skipped |

### Example Results

**PR Comment:**
```markdown
## ✅ FHIR Validation Report - PASSED

### Summary
- ✅ Passed: 5
- ❌ Failed: 0
- ⊘ Skipped: 1

### ✅ Passed Examples
- examples/Patient-example1.json → CustomPatient
- examples/Patient-example2.json → CustomPatient
- examples/Observation-example1.json → CustomObservation
...
```

## Setup Steps

1. Create your assets repo with this structure
2. Add `trigger-validation.yml` to `.github/workflows/`
3. Add `PAT_TOKEN` secret to repository
4. Push changes
5. Create a PR to test

See SETUP-CHECKLIST.md for detailed setup instructions.
