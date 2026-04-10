# File Deployment Guide

This guide shows exactly which files go to which repository.

## Repository Breakdown

### 📁 Validation Repository: ryma2fhir/Validation-github-action

```
Validation-github-action/
├── .github/
│   └── workflows/
│       └── validation-service.yml          ← Deploy this
│
├── scripts/
│   ├── configure-packages.py              ← Deploy this
│   ├── upload-assets.py                   ← Deploy this
│   ├── validate-assets.py                 ← Deploy this
│   ├── upload-capability.py               ← Deploy this
│   ├── validate-examples.py               ← Deploy this
│   └── generate-report.py                 ← Deploy this
│
├── verify-setup.sh                        ← Deploy this (optional, for verification)
└── test-local.sh                          ← Deploy this (optional, for local testing)
```

**Actions:**
```bash
cd Validation-github-action

# Copy workflows
mkdir -p .github/workflows
cp validation-service.yml .github/workflows/

# Copy scripts
mkdir -p scripts
cp configure-packages.py upload-assets.py validate-assets.py \
   upload-capability.py validate-examples.py generate-report.py \
   scripts/

# Make scripts executable
chmod +x scripts/*.py verify-setup.sh test-local.sh

# Verify setup
./verify-setup.sh

# Commit
git add .github/workflows/ scripts/ verify-setup.sh test-local.sh
git commit -m "Add cross-repo validation system"
git push
```

### 📁 Assets Repository: your-org/your-fhir-assets

```
your-fhir-assets/
├── .github/
│   └── workflows/
│       └── trigger-validation.yml          ← Deploy this
│
├── fhir/                                   ← Your conformance resources
│   ├── StructureDefinition-*.json
│   ├── ValueSet-*.json
│   └── CodeSystem-*.json
│
├── examples/                               ← Your example instances
│   ├── Patient-*.json
│   └── Observation-*.json
│
├── CapabilityStatement.json                ← Your capability statement
└── package.json                            ← Your FHIR dependencies
```

**Actions:**
```bash
cd your-fhir-assets

# Copy trigger workflow
mkdir -p .github/workflows
cp trigger-validation.yml .github/workflows/

# Update repository name in workflow
sed -i 's/your-org\/your-fhir-assets/YOUR_ACTUAL_ORG\/YOUR_ACTUAL_REPO/g' \
  .github/workflows/trigger-validation.yml

# Commit
git add .github/workflows/trigger-validation.yml
git commit -m "Add FHIR validation trigger"
git push
```

### 📁 Service Repository: ryma2fhir/FHIR-JPA-Service

```
FHIR-JPA-Service/
├── Dockerfile                              ← Must exist
├── application.yaml                        ← Your HAPI config
├── (custom interceptors)                   ← Your terminology interceptors
└── (other service files)
```

**Requirements:**
- Dockerfile builds successfully
- Service exposes port 8080
- Health check at `/fhir/metadata` works
- No changes needed if already working

## Files Reference

### Workflow Files (GitHub Actions)

| File | Repository | Purpose |
|------|-----------|---------|
| `validation-service.yml` | Validation-github-action | Main validation workflow (receives triggers) |
| `trigger-validation.yml` | Assets repo | Triggers validation on push/PR |

### Python Scripts (Validation Logic)

| File | Repository | Purpose |
|------|-----------|---------|
| `configure-packages.py` | Validation-github-action | Install FHIR packages via $install |
| `upload-assets.py` | Validation-github-action | Upload conformance resources |
| `validate-assets.py` | Validation-github-action | Validate conformance resources |
| `upload-capability.py` | Validation-github-action | Upload CapabilityStatement |
| `validate-examples.py` | Validation-github-action | Validate examples against profiles |
| `generate-report.py` | Validation-github-action | Generate PR comment report |

### Utility Scripts

| File | Repository | Purpose |
|------|-----------|---------|
| `verify-setup.sh` | Validation-github-action | Verify setup is correct |
| `test-local.sh` | Validation-github-action | Test validation locally |

### Documentation Files (Reference Only)

These files are for your reference and don't get deployed:

| File | Purpose |
|------|---------|
| `MAIN-README.md` | Overview of complete system |
| `SETUP-CHECKLIST.md` | Quick setup checklist |
| `CROSS-REPO-SETUP.md` | Detailed setup guide |
| `ASSETS-REPO-EXAMPLE.md` | Example assets repo structure |
| `QUICKSTART.md` | Original single-repo guide |
| `README.md` | Original detailed documentation |

### Configuration Files

| File | Repository | Purpose |
|------|-----------|---------|
| `package.json` | Assets repo | FHIR package dependencies |
| `package.json.example` | Reference | Example package.json |
| `CapabilityStatement.json` | Assets repo | Profile requirements |
| `CapabilityStatement.json.example` | Reference | Example CapabilityStatement |

## Step-by-Step Deployment

### Phase 1: Validation Repository Setup

1. Clone validation repo
   ```bash
   git clone https://github.com/ryma2fhir/Validation-github-action.git
   cd Validation-github-action
   ```

2. Copy files
   ```bash
   # Workflow
   mkdir -p .github/workflows
   cp /path/to/validation-service.yml .github/workflows/
   
   # Scripts
   mkdir -p scripts
   cp /path/to/scripts/*.py scripts/
   
   # Tools
   cp /path/to/verify-setup.sh .
   cp /path/to/test-local.sh .
   
   # Make executable
   chmod +x scripts/*.py verify-setup.sh test-local.sh
   ```

3. Verify
   ```bash
   ./verify-setup.sh
   ```

4. Commit and push
   ```bash
   git add .
   git commit -m "Add cross-repo validation system"
   git push
   ```

### Phase 2: Assets Repository Setup

1. Clone assets repo
   ```bash
   git clone https://github.com/your-org/your-fhir-assets.git
   cd your-fhir-assets
   ```

2. Copy trigger workflow
   ```bash
   mkdir -p .github/workflows
   cp /path/to/trigger-validation.yml .github/workflows/
   ```

3. Update repository references
   ```bash
   # Edit trigger-validation.yml
   # Change: repository: ryma2fhir/Validation-github-action (correct)
   # And any references to your-org/your-fhir-assets (update to actual)
   ```

4. Ensure structure exists
   ```bash
   mkdir -p fhir examples
   # Add your FHIR files, package.json, CapabilityStatement.json
   ```

5. Commit and push
   ```bash
   git add .github/workflows/trigger-validation.yml
   git commit -m "Add FHIR validation trigger"
   git push
   ```

### Phase 3: Secrets Configuration

For **BOTH** repositories:

1. Go to: Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `PAT_TOKEN`
4. Value: (your Personal Access Token)
5. Add secret

See [SETUP-CHECKLIST.md](./SETUP-CHECKLIST.md) for PAT creation.

### Phase 4: Testing

1. Manual test (validation repo)
   ```bash
   # GitHub UI: Actions → FHIR Validation Service → Run workflow
   ```

2. Automatic test (assets repo)
   ```bash
   # Make a change to a FHIR file
   git checkout -b test-validation
   echo '{}' > fhir/test.json
   git add fhir/test.json
   git commit -m "Test validation"
   git push -u origin test-validation
   # Create PR and watch validation run
   ```

## Quick Deployment Commands

### All-in-One: Validation Repo

```bash
#!/bin/bash
cd Validation-github-action

# Copy files
mkdir -p .github/workflows scripts
cp validation-service.yml .github/workflows/
cp configure-packages.py upload-assets.py validate-assets.py \
   upload-capability.py validate-examples.py generate-report.py scripts/
cp verify-setup.sh test-local.sh .

# Make executable
chmod +x scripts/*.py verify-setup.sh test-local.sh

# Verify
./verify-setup.sh

# Commit
git add .github/workflows/ scripts/ verify-setup.sh test-local.sh
git commit -m "Add cross-repo validation system"
git push

echo "✓ Validation repository setup complete"
```

### All-in-One: Assets Repo

```bash
#!/bin/bash
cd your-fhir-assets

# Copy workflow
mkdir -p .github/workflows
cp trigger-validation.yml .github/workflows/

# Update if needed (replace YOUR_ORG and YOUR_REPO)
sed -i 's/your-org\/your-fhir-assets/YOUR_ORG\/YOUR_REPO/g' \
  .github/workflows/trigger-validation.yml

# Ensure structure
mkdir -p fhir examples

# Commit
git add .github/workflows/trigger-validation.yml
git commit -m "Add FHIR validation trigger"
git push

echo "✓ Assets repository setup complete"
echo "⚠ Don't forget to add PAT_TOKEN secret!"
```

## Verification Checklist

After deployment, verify:

- [ ] validation-service.yml in Validation-github-action/.github/workflows/
- [ ] All 6 Python scripts in Validation-github-action/scripts/
- [ ] trigger-validation.yml in assets/.github/workflows/
- [ ] PAT_TOKEN secret in Validation-github-action
- [ ] PAT_TOKEN secret in assets repo
- [ ] package.json in assets repo
- [ ] CapabilityStatement.json in assets repo
- [ ] FHIR resources in assets/fhir/
- [ ] Examples in assets/examples/
- [ ] FHIR-JPA-Service has Dockerfile

## Next Steps

1. ✅ Read [SETUP-CHECKLIST.md](./SETUP-CHECKLIST.md)
2. ✅ Deploy files following this guide
3. ✅ Add PAT_TOKEN secrets
4. ✅ Test manually
5. ✅ Test automatically with PR
6. ✅ Celebrate! 🎉
