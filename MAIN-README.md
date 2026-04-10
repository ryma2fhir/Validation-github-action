# FHIR Cross-Repo Validation System

Complete GitHub Actions setup for automated FHIR validation using HAPI FHIR server across multiple repositories.

## 📋 Overview

This system enables automatic FHIR validation when you push changes to your FHIR assets repository:

1. **Assets Repo** (your FHIR resources) → Push triggers validation
2. **Validation Repo** → Runs validation service
3. **FHIR Service Repo** → Custom HAPI FHIR with terminology interceptors
4. **Results** → Posted back to your assets repo PR

```
┌──────────────────┐
│  Assets Repo     │  Push/PR with FHIR changes
│  (your content)  │
└────────┬─────────┘
         │ trigger
         ▼
┌────────────────────────────┐
│  Validation-github-action  │
│  • Builds FHIR service     │──── Uses ────┐
│  • Starts service          │              │
│  • Runs validation         │              ▼
│  • Posts results           │      ┌──────────────────┐
└────────┬───────────────────┘      │ FHIR-JPA-Service │
         │                          │ (custom HAPI)    │
         │                          └──────────────────┘
         ▼
┌──────────────────┐
│  PR Comment      │
│  ✅ Passed: 5    │
│  ❌ Failed: 0    │
└──────────────────┘
```

## 🚀 Quick Start

**5-minute setup:**

1. **Read:** [SETUP-CHECKLIST.md](./SETUP-CHECKLIST.md) - Step-by-step checklist
2. **Setup:** Create PAT token, add to both repos
3. **Install:** Copy workflows to your repositories
4. **Test:** Push a change and watch validation run
5. **Done:** Validation runs automatically on all PRs

**Detailed guides:**
- [CROSS-REPO-SETUP.md](./CROSS-REPO-SETUP.md) - Complete setup guide with troubleshooting
- [ASSETS-REPO-EXAMPLE.md](./ASSETS-REPO-EXAMPLE.md) - Example assets repo structure

## 📦 What's Included

### For Validation Repository (ryma2fhir/Validation-github-action)

**Workflows:**
- `validation-service.yml` - Main validation service (triggered by assets repo)

**Scripts:**
- `configure-packages.py` - Install FHIR packages using $install
- `upload-assets.py` - Upload conformance resources
- `validate-assets.py` - Validate conformance resources
- `upload-capability.py` - Upload CapabilityStatement
- `validate-examples.py` - Validate examples against profiles
- `generate-report.py` - Generate PR comment

**Tools:**
- `verify-setup.sh` - Verify validation repo setup is correct
- `test-local.sh` - Test validation locally with Docker

### For Assets Repository (your FHIR content)

**Workflows:**
- `trigger-validation.yml` - Triggers validation on push/PR

**Required Files:**
- `package.json` - FHIR package dependencies
- `CapabilityStatement.json` - Profile requirements per resource type
- `fhir/*.json` - Your conformance resources
- `examples/*.json` - Example instances to validate

## 🏗️ Repository Setup

### 1. Validation Repository

```bash
cd Validation-github-action

# Copy files
cp validation-service.yml .github/workflows/
cp -r scripts/ .
cp verify-setup.sh .
cp test-local.sh .

# Verify setup
chmod +x verify-setup.sh
./verify-setup.sh

# Commit
git add .
git commit -m "Add cross-repo validation system"
git push
```

### 2. Assets Repository

```bash
cd your-fhir-assets

# Copy workflow
cp trigger-validation.yml .github/workflows/

# Create structure (if needed)
mkdir -p fhir examples

# Add your files
# - fhir/*.json (StructureDefinitions, ValueSets, etc.)
# - examples/*.json (example instances)
# - CapabilityStatement.json
# - package.json

# Commit
git add .
git commit -m "Add FHIR validation trigger"
git push
```

### 3. FHIR Service Repository

Ensure `ryma2fhir/FHIR-JPA-Service` has:
- `Dockerfile` at root
- Service runs on port 8080
- `/fhir/metadata` endpoint for health check

## 🔑 Authentication Setup

**Required:** Personal Access Token (PAT)

1. Create PAT with `repo` and `workflow` scopes
2. Add as `PAT_TOKEN` secret to **BOTH** repositories:
   - ryma2fhir/Validation-github-action
   - your-assets-repo

See [SETUP-CHECKLIST.md](./SETUP-CHECKLIST.md) for detailed instructions.

## 🎯 Key Features

### No meta.profile Required

Examples don't need `meta.profile` - the CapabilityStatement defines which profile each resource type validates against:

```json
{
  "resourceType": "Patient",
  "id": "example1",
  "identifier": [...],
  "name": [...]
  // No meta.profile needed!
}
```

CapabilityStatement says: `Patient → CustomPatient profile`

### Package Management via $install

Just maintain `package.json`:

```json
{
  "dependencies": {
    "hl7.fhir.us.core": "6.1.0"
  }
}
```

Packages installed automatically using FHIR `$install` operation.

### Custom HAPI FHIR Service

Uses your `ryma2fhir/FHIR-JPA-Service` with:
- Custom terminology interceptors
- External terminology server connections
- Your specific HAPI configuration

### Rich PR Comments

Detailed validation results posted to PRs:

```markdown
## ✅ FHIR Validation Report - PASSED

### Summary
- ✅ Passed: 5
- ❌ Failed: 0
- ⊘ Skipped: 1

### ✅ Passed Examples (click to expand)
- examples/Patient-example1.json → CustomPatient
- examples/Observation-example1.json → CustomObservation
...
```

## 🧪 Testing

### Local Testing

```bash
# Start your FHIR service
docker run -d -p 8080:8080 ryma2fhir-hapi:latest

# Wait for startup
sleep 30

# Run validation
./test-local.sh
```

### Manual GitHub Actions Test

1. Go to Validation-github-action repo
2. Actions → FHIR Validation Service → Run workflow
3. Enter your assets repo name and branch
4. Run and verify it completes

### Automatic Test

1. Push a change to FHIR resource in assets repo
2. Watch workflows run in both repos
3. Check PR comment appears with results

## 📚 Documentation

| File | Description |
|------|-------------|
| [SETUP-CHECKLIST.md](./SETUP-CHECKLIST.md) | Quick setup checklist with verification steps |
| [CROSS-REPO-SETUP.md](./CROSS-REPO-SETUP.md) | Complete setup guide with troubleshooting |
| [ASSETS-REPO-EXAMPLE.md](./ASSETS-REPO-EXAMPLE.md) | Example assets repo structure and files |
| [QUICKSTART.md](./QUICKSTART.md) | Original single-repo validation quickstart |
| [README.md](./README.md) | Original single-repo detailed documentation |

## 🔧 Configuration

### Custom Directory Paths

If your assets repo uses different paths, update `validation-service.yml`:

```yaml
- name: Copy assets to validation workspace
  run: |
    cp -r assets/YOUR_RESOURCES_DIR/* validation/fhir/
    cp -r assets/YOUR_EXAMPLES_DIR/* validation/examples/
```

### Environment Variables

If FHIR service needs environment variables, update `validation-service.yml`:

```yaml
- name: Start FHIR JPA Service
  run: |
    docker run -d \
      -e TERMINOLOGY_SERVER="https://tx.fhir.org/r4" \
      -e YOUR_VAR="value" \
      ryma2fhir-hapi:latest
```

### Trigger on Specific Branches

Edit `trigger-validation.yml`:

```yaml
on:
  push:
    branches:
      - main
      - release/*
      - feature/fhir-*
```

## 🐛 Troubleshooting

### Common Issues

**"Resource not accessible by integration"**
- Add PAT_TOKEN to both repos with correct permissions

**"FHIR service failed to become healthy"**
- Check Dockerfile and health check configuration
- View logs in failed workflow

**"Repository dispatch not triggering"**
- Ensure validation-service.yml is on main branch
- Verify repository names in workflows

See [CROSS-REPO-SETUP.md](./CROSS-REPO-SETUP.md) troubleshooting section for more.

### Verification Tool

Run in validation repo:
```bash
./verify-setup.sh
```

## 📊 Workflow Details

### Assets Repo Workflow

**File:** `trigger-validation.yml`

**Triggers:**
- Push to main/develop
- Pull requests to main
- Only when FHIR files change

**Actions:**
1. Sends repository_dispatch to Validation-github-action
2. Sets pending status on PR

### Validation Repo Workflow

**File:** `validation-service.yml`

**Triggers:**
- Repository dispatch from assets repo
- Manual workflow dispatch

**Steps:**
1. Checkout validation scripts
2. Checkout FHIR assets
3. Checkout and build FHIR-JPA-Service
4. Start FHIR service (wait until healthy)
5. Install packages ($install operation)
6. Upload conformance resources
7. Validate conformance resources
8. Upload CapabilityStatement
9. Validate examples
10. Post results to assets repo PR

## 🔒 Security

- ✅ Use repository secrets for PAT_TOKEN
- ✅ Never commit tokens to repository
- ✅ Limit PAT scope to minimum required
- ✅ Rotate PAT periodically
- ✅ Review access permissions regularly

## 📈 Next Steps

After setup:

1. ✅ Customize validation rules in scripts
2. ✅ Add validation status badge to README
3. ✅ Set up branch protection requiring validation
4. ✅ Configure FHIR service environment
5. ✅ Add custom validation checks as needed

## 🤝 Support

For issues:
1. Check workflow logs in both repositories
2. Run `./verify-setup.sh` in validation repo
3. Review troubleshooting guides
4. Check FHIR service logs in failed runs

## 📝 License

MIT

---

**Start here:** [SETUP-CHECKLIST.md](./SETUP-CHECKLIST.md)
