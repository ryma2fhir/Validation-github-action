# Cross-Repo FHIR Validation Setup

This setup allows your FHIR assets repo to automatically trigger validation using your custom FHIR service.

## Architecture

```
┌─────────────────────┐
│  FHIR Assets Repo   │  (Your FHIR resources)
│  Push/PR triggers   │
└──────────┬──────────┘
           │ repository_dispatch
           ▼
┌─────────────────────────────────┐
│  Validation-github-action Repo  │
│  1. Checks out assets           │
│  2. Builds FHIR-JPA-Service     │
│  3. Starts service & waits      │
│  4. Runs validation scripts     │
│  5. Posts results back          │
└─────────────────────────────────┘
           │
           ├─ Uses: ryma2fhir/FHIR-JPA-Service
           └─ Posts results to: FHIR Assets Repo
```

## Prerequisites

### 1. Create Personal Access Token (PAT)

You need a PAT with these permissions:
- `repo` (full control of private repositories)
- `workflow` (update GitHub Action workflows)

**Steps:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Name: `FHIR_VALIDATION_TOKEN`
4. Select scopes:
   - ✅ `repo` (all)
   - ✅ `workflow`
5. Generate token
6. **Copy the token** (you won't see it again!)

### 2. Add Secrets to Repositories

**In BOTH repos** (assets repo AND Validation-github-action repo):

1. Go to repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PAT_TOKEN`
4. Value: (paste the PAT from step 1)
5. Click "Add secret"

## Installation

### Repo 1: ryma2fhir/Validation-github-action

```bash
# Clone the validation repo
git clone https://github.com/ryma2fhir/Validation-github-action.git
cd Validation-github-action

# Add the validation service workflow
mkdir -p .github/workflows
cp validation-service.yml .github/workflows/

# Add the validation scripts (from previous setup)
mkdir -p scripts
# Copy all scripts from the previous setup

# Commit and push
git add .github/workflows/validation-service.yml scripts/
git commit -m "Add cross-repo validation service"
git push
```

### Repo 2: Your FHIR Assets Repo

```bash
# Clone your assets repo
git clone https://github.com/your-org/your-fhir-assets.git
cd your-fhir-assets

# Add the trigger workflow
mkdir -p .github/workflows
cp trigger-validation.yml .github/workflows/

# Commit and push
git add .github/workflows/trigger-validation.yml
git commit -m "Add FHIR validation trigger"
git push
```

### Repo 3: ryma2fhir/FHIR-JPA-Service

Ensure this repo has:
- A `Dockerfile` at the root
- The FHIR service starts on port 8080
- Health check endpoint at `/fhir/metadata`

**Example Dockerfile requirements:**
```dockerfile
FROM hapiproject/hapi:latest

# Your custom configuration
COPY application.yaml /app/config/

# Your custom interceptors
COPY custom-interceptors/ /app/interceptors/

# Expose FHIR endpoint
EXPOSE 8080

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=30 \
  CMD curl -f http://localhost:8080/fhir/metadata || exit 1
```

## Configuration

### Update Assets Repo Path (if different structure)

Edit `validation-service.yml` step "Copy assets to validation workspace":

```yaml
- name: Copy assets to validation workspace
  run: |
    mkdir -p validation/fhir
    mkdir -p validation/examples
    
    # Adjust these paths to match your repo structure
    cp -r assets/YOUR_FHIR_DIR/* validation/fhir/
    cp -r assets/YOUR_EXAMPLES_DIR/* validation/examples/
    cp assets/package.json validation/
    cp assets/CapabilityStatement.json validation/
```

### Update Trigger Paths (optional)

Edit `trigger-validation.yml` to match your repo structure:

```yaml
on:
  push:
    paths:
      - 'your-fhir-dir/**'      # Your FHIR resources
      - 'your-examples-dir/**'  # Your examples
      - 'package.json'
```

### Configure FHIR Service Environment Variables

If your FHIR-JPA-Service needs environment variables, update `validation-service.yml`:

```yaml
- name: Start FHIR JPA Service
  run: |
    docker run -d \
      --name fhir-service \
      -p 8080:8080 \
      -e TERMINOLOGY_SERVER_URL="https://tx.fhir.org/r4" \
      -e YOUR_CUSTOM_VAR="value" \
      ryma2fhir-hapi:latest
```

## Testing

### Test Manually

1. Go to Validation-github-action repo
2. Click "Actions" tab
3. Select "FHIR Validation Service" workflow
4. Click "Run workflow"
5. Enter:
   - Assets repo: `your-org/your-fhir-assets`
   - Assets ref: `main`
6. Click "Run workflow"

### Test Automatically

1. In your assets repo, create a test branch
2. Make a change to a FHIR resource
3. Push the change
4. Watch the workflows:
   - Assets repo: "Trigger FHIR Validation" runs
   - Validation repo: "FHIR Validation Service" runs
   - Results posted back to assets repo

## Workflow Details

### Assets Repo Workflow (trigger-validation.yml)

**Triggers on:**
- Push to main/develop branches
- Pull requests to main
- Only when FHIR files change

**Actions:**
1. Sends repository_dispatch to Validation-github-action
2. Passes payload with repo, ref, SHA, PR number
3. Sets pending status check on PR

### Validation Repo Workflow (validation-service.yml)

**Triggered by:**
- Repository dispatch from assets repo
- Manual workflow dispatch (for testing)

**Steps:**
1. ✅ Checkout validation scripts
2. ✅ Checkout FHIR assets from triggering repo
3. ✅ Checkout FHIR-JPA-Service
4. ✅ Build FHIR service Docker image
5. ✅ Start FHIR service container
6. ✅ Wait for service to be healthy (max 10 minutes)
7. ✅ Copy assets to validation workspace
8. ✅ Install FHIR packages
9. ✅ Upload conformance assets
10. ✅ Validate assets
11. ✅ Upload CapabilityStatement
12. ✅ Validate examples
13. ✅ Generate report
14. ✅ Post results to assets repo PR
15. ✅ Set commit status (success/failure)

## Troubleshooting

### "Resource not accessible by integration"

**Cause:** PAT_TOKEN missing or has wrong permissions

**Fix:**
1. Verify PAT has `repo` and `workflow` scopes
2. Add PAT_TOKEN to BOTH repositories
3. Re-run workflow

### "FHIR service failed to become healthy"

**Cause:** Service not starting or taking too long

**Fix:**
1. Check Dockerfile health check is correct
2. Increase timeout in validation-service.yml:
   ```yaml
   max_attempts=120  # Increase from 60
   ```
3. Check service logs in failed workflow

### "Repository dispatch not triggering"

**Cause:** Workflow not in default branch

**Fix:**
1. Ensure `validation-service.yml` is on `main` branch
2. Repository dispatch only works for workflows on default branch

### "Validation scripts not found"

**Cause:** Scripts not in Validation-github-action repo

**Fix:**
1. Copy all scripts from previous setup to `scripts/` directory
2. Commit and push to Validation-github-action repo

### "Assets not found during validation"

**Cause:** Assets repo structure doesn't match expectations

**Fix:**
1. Update the "Copy assets to validation workspace" step
2. Match your actual directory structure
3. Check workflow logs to see what was copied

## Advanced Configuration

### Run validation on specific branches only

Edit `trigger-validation.yml`:
```yaml
on:
  push:
    branches:
      - main
      - release/*
      - feature/fhir-*
```

### Add validation status badge

In your assets repo README.md:
```markdown
![FHIR Validation](https://github.com/ryma2fhir/Validation-github-action/actions/workflows/validation-service.yml/badge.svg)
```

### Customize validation report format

Edit `scripts/generate-report.py` in Validation-github-action repo

### Use different FHIR service versions

Update `validation-service.yml`:
```yaml
- name: Checkout FHIR JPA Service
  with:
    ref: v2.0.0  # Specific version tag
```

## Security Notes

- ✅ PAT_TOKEN has full repo access - keep it secure
- ✅ Never commit tokens to repository
- ✅ Rotate PAT periodically
- ✅ Use repository secrets, not environment variables
- ✅ Limit PAT scope to minimum required permissions

## Support

For issues:
1. Check workflow logs in both repositories
2. Verify PAT_TOKEN is set correctly
3. Ensure FHIR-JPA-Service builds successfully locally
4. Review troubleshooting section above
