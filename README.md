# FHIR Validation with GitHub Actions

Automated FHIR validation using HAPI FHIR server and CapabilityStatement-driven profile validation.

## Overview

This setup validates FHIR examples against profiles defined in your CapabilityStatement, without requiring `meta.profile` in each example.

**Workflow:**
1. Install FHIR package dependencies (from `package.json`)
2. Upload conformance assets (StructureDefinitions, ValueSets, CodeSystems)
3. Validate assets are valid FHIR
4. Upload CapabilityStatement (defines which profile to use per resource type)
5. Validate examples against profiles from CapabilityStatement
6. Generate validation report and post to PR

## Directory Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── fhir-validation.yml
├── scripts/
│   ├── configure-packages.py
│   ├── upload-assets.py
│   ├── validate-assets.py
│   ├── upload-capability.py
│   ├── validate-examples.py
│   └── generate-report.py
├── fhir/                           # Your conformance resources
│   ├── StructureDefinition-*.json
│   ├── ValueSet-*.json
│   └── CodeSystem-*.json
├── examples/                       # Example instances
│   ├── Patient-example.json
│   └── Observation-example.json
├── CapabilityStatement.json        # Profile requirements
└── package.json                    # FHIR package dependencies
```

## Setup

### 1. Configure Your Custom HAPI FHIR Docker Image

If you have a custom HAPI FHIR Docker image with terminology interceptors, update the workflow:

```yaml
services:
  hapi-fhir:
    image: your-registry/your-custom-hapi:latest  # Change this
    ports:
      - 8080:8080
```

Or build it in the workflow:

```yaml
steps:
  - name: Build HAPI FHIR
    run: |
      cd docker/hapi-fhir
      docker build -t custom-hapi .
      docker run -d -p 8080:8080 custom-hapi
```

### 2. Create package.json

Define your FHIR package dependencies:

```json
{
  "name": "your-fhir-ig",
  "version": "1.0.0",
  "dependencies": {
    "hl7.fhir.r4.core": "4.0.1",
    "hl7.fhir.uv.ips": "1.1.0",
    "hl7.fhir.us.core": "6.1.0"
  }
}
```

### 3. Create CapabilityStatement

Define which profile each resource type should conform to:

```json
{
  "resourceType": "CapabilityStatement",
  "id": "your-conformance",
  "url": "https://your-domain.org/CapabilityStatement/your-conformance",
  "version": "1.0.0",
  "name": "YourConformance",
  "status": "active",
  "kind": "requirements",
  "fhirVersion": "4.0.1",
  "rest": [
    {
      "mode": "server",
      "resource": [
        {
          "type": "Patient",
          "profile": "https://your-domain.org/StructureDefinition/your-patient-profile"
        },
        {
          "type": "Observation",
          "profile": "https://your-domain.org/StructureDefinition/your-observation-profile"
        }
      ]
    }
  ]
}
```

### 4. Adjust Directory Paths

If your directories differ from the defaults, update these variables in the scripts:

- `configure-packages.py`: (no changes needed - reads package.json from root)
- `upload-assets.py`: `ASSETS_DIR = "fhir"` (line 9)
- `upload-capability.py`: `CAPABILITY_FILE = "CapabilityStatement.json"` (line 8)
- `validate-examples.py`: `EXAMPLES_DIR = "examples"` (line 9)
- `validate-assets.py`: `ASSETS_DIR = "fhir"` (line 8)

### 5. Make Scripts Executable

```bash
chmod +x scripts/*.py
```

## Usage

### Automatic Validation

Push to a PR and the workflow runs automatically. Results are posted as a PR comment.

### Manual Testing Locally

You can test locally with Docker:

```bash
# Start HAPI FHIR
docker run -d -p 8080:8080 hapiproject/hapi:latest

# Wait for startup
sleep 30

# Run validation
python3 scripts/configure-packages.py
python3 scripts/upload-assets.py
python3 scripts/validate-assets.py
python3 scripts/upload-capability.py
python3 scripts/validate-examples.py
python3 scripts/generate-report.py
```

## Validation Rules

- **Examples WITHOUT `meta.profile`**: Validated against profile from CapabilityStatement
- **Examples WITH `meta.profile`**: Still validated against CapabilityStatement profile (meta.profile is ignored)
- **Resource types NOT in CapabilityStatement**: Skipped (not an error)
- **Invalid conformance assets**: Fails the build
- **Validation errors**: Fails the build with detailed OperationOutcome

## Customization

### Skip Certain Examples

Add a `.validation-ignore` file with patterns:

```
examples/draft/*.json
examples/experimental/*.json
```

Then update `validate-examples.py` to read and respect this file.

### Custom Validation Rules

Modify `validate-examples.py` to add additional checks:

```python
# Example: Require specific extensions
if resource_type == "Patient":
    required_ext = "http://your-domain.org/StructureDefinition/required-extension"
    extensions = [e.get('url') for e in resource.get('extension', [])]
    if required_ext not in extensions:
        # Add to validation errors
```

## Troubleshooting

### "Failed to install package X"

- Check package name and version exist at https://packages.fhir.org
- Increase timeout in `configure-packages.py` (line 21)
- Some packages are large and take time to install

### "No profile in CapabilityStatement"

- Ensure CapabilityStatement has `rest.resource.profile` for that resource type
- Check resource type spelling matches exactly

### "Validation endpoint not responding"

- Increase health check timeout in workflow (lines 17-20)
- Check HAPI FHIR logs: `docker logs <container-id>`

### "CapabilityStatement not found"

- Ensure file is named `CapabilityStatement.json` (or update script)
- Check file is in repo root or `fhir/` directory
- Verify JSON is valid

## License

MIT
