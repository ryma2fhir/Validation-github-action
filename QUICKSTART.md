# Quick Start Guide

## What This Does

Validates FHIR examples against profiles defined in your CapabilityStatement using GitHub Actions and HAPI FHIR.

**Key Feature:** Examples don't need `meta.profile` - the CapabilityStatement defines which profile each resource type validates against.

## Setup (5 minutes)

### 1. Copy Files to Your Repo

```bash
# Copy all files to your repo root
cp -r .github scripts *.example test-local.sh your-repo/

# Rename examples
cd your-repo
mv package.json.example package.json
mv CapabilityStatement.json.example CapabilityStatement.json
```

### 2. Update Paths

If your directories differ, edit these files:

- `scripts/upload-assets.py` - line 9: `ASSETS_DIR = "fhir"`
- `scripts/validate-examples.py` - line 9: `EXAMPLES_DIR = "examples"`
- `scripts/upload-capability.py` - line 8: `CAPABILITY_FILE = "CapabilityStatement.json"`

### 3. Configure Your HAPI FHIR

**Option A - Use your custom Docker image:**

Edit `.github/workflows/fhir-validation.yml` line 12:
```yaml
image: your-registry/your-custom-hapi:latest
```

**Option B - Build in workflow:**

Add before validation steps:
```yaml
- name: Build HAPI FHIR
  run: |
    docker build -t custom-hapi ./path/to/dockerfile
    docker run -d -p 8080:8080 custom-hapi
```

### 4. Add Your Files

```
your-repo/
├── fhir/                      # Your conformance resources
│   ├── StructureDefinition-YourPatient.json
│   ├── ValueSet-YourValueSet.json
│   └── ...
├── examples/                  # Examples to validate
│   ├── Patient-example1.json
│   └── Observation-example1.json
├── CapabilityStatement.json   # Defines profile per resource type
└── package.json              # FHIR package dependencies
```

### 5. Edit CapabilityStatement.json

```json
{
  "resourceType": "CapabilityStatement",
  "id": "your-id",
  "rest": [{
    "mode": "server",
    "resource": [
      {
        "type": "Patient",
        "profile": "https://your-domain.org/StructureDefinition/YourPatient"
      },
      {
        "type": "Observation",
        "profile": "https://your-domain.org/StructureDefinition/YourObservation"
      }
    ]
  }]
}
```

### 6. Edit package.json

```json
{
  "name": "your-ig",
  "version": "1.0.0",
  "dependencies": {
    "hl7.fhir.r4.core": "4.0.1",
    "hl7.fhir.us.core": "6.1.0"
  }
}
```

### 7. Test Locally

```bash
# Start HAPI FHIR
docker run -d -p 8080:8080 hapiproject/hapi:latest

# Wait 30 seconds for startup
sleep 30

# Run validation
./test-local.sh
```

### 8. Commit and Push

```bash
git add .github/ scripts/ package.json CapabilityStatement.json
git commit -m "Add FHIR validation workflow"
git push
```

## How It Works

1. **GitHub Actions triggers** on PR to main with changes to `fhir/`, `examples/`, or `package.json`
2. **Starts HAPI FHIR** as a service container
3. **Installs packages** from package.json using `$install` operation
4. **Uploads conformance assets** (your StructureDefinitions, ValueSets, etc.)
5. **Validates assets** are valid FHIR
6. **Uploads CapabilityStatement** which defines profile requirements
7. **Validates examples** using profiles from CapabilityStatement
8. **Posts results** to PR as a comment

## Example Validation Flow

Given:
- Example: `examples/Patient-example1.json` with `resourceType: "Patient"`
- CapabilityStatement says: `Patient` → `https://example.org/StructureDefinition/ExamplePatient`

Result:
- Example is validated against `ExamplePatient` profile
- No `meta.profile` needed in the example file
- Validation results posted to PR

## What Gets Validated

✅ **All examples** in `examples/` directory with matching CapabilityStatement entry
⊘ **Skipped** if resource type not in CapabilityStatement
❌ **Fails** if validation errors found

## Troubleshooting

**"Package installation failed"**
- Check package exists: https://packages.fhir.org
- Increase timeout in `scripts/configure-packages.py` line 21

**"No profile in CapabilityStatement"**
- Add resource type to CapabilityStatement
- Check spelling matches exactly

**"HAPI FHIR not ready"**
- Increase health check timeout in workflow lines 17-20
- Check custom interceptors aren't blocking startup

## Support

See full README.md for detailed documentation.
