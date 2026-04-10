# Cross-Repo Validation Quick Setup Checklist

## One-Time Setup (5 minutes)

### Step 1: Create Personal Access Token
- [ ] Go to GitHub → Settings → Developer settings → Personal access tokens
- [ ] Generate new token (classic)
- [ ] Select scopes: `repo` ✅ and `workflow` ✅
- [ ] Generate and copy token (save it temporarily)

### Step 2: Add Secret to Validation Repo
- [ ] Go to `ryma2fhir/Validation-github-action`
- [ ] Settings → Secrets and variables → Actions
- [ ] New repository secret
- [ ] Name: `PAT_TOKEN`
- [ ] Value: (paste token)
- [ ] Add secret

### Step 3: Add Secret to Assets Repo
- [ ] Go to your FHIR assets repo
- [ ] Settings → Secrets and variables → Actions
- [ ] New repository secret
- [ ] Name: `PAT_TOKEN`
- [ ] Value: (paste same token)
- [ ] Add secret

### Step 4: Setup Validation Repo
```bash
cd Validation-github-action

# Copy validation service workflow
cp validation-service.yml .github/workflows/

# Copy all scripts from previous setup
cp -r scripts/ .

# Commit and push
git add .github/workflows/validation-service.yml scripts/
git commit -m "Add cross-repo validation service"
git push
```

### Step 5: Setup Assets Repo
```bash
cd your-fhir-assets-repo

# Copy trigger workflow
cp trigger-validation.yml .github/workflows/

# Update repo name in workflow
sed -i 's/ryma2fhir\/your-assets-repo/YOUR_ORG\/YOUR_REPO/g' .github/workflows/trigger-validation.yml

# Commit and push
git add .github/workflows/trigger-validation.yml
git commit -m "Add FHIR validation trigger"
git push
```

### Step 6: Verify FHIR Service Repo
- [ ] `ryma2fhir/FHIR-JPA-Service` has a Dockerfile
- [ ] Service runs on port 8080
- [ ] Has `/fhir/metadata` endpoint

## Quick Test

### Manual Test
1. [ ] Go to `ryma2fhir/Validation-github-action`
2. [ ] Actions → FHIR Validation Service → Run workflow
3. [ ] Enter your assets repo name
4. [ ] Run and check it completes

### Automatic Test
1. [ ] Make a change to a FHIR resource in assets repo
2. [ ] Create a pull request
3. [ ] Watch "Trigger FHIR Validation" run in assets repo
4. [ ] Watch "FHIR Validation Service" run in validation repo
5. [ ] Check PR comment with results appears

## Expected Directory Structures

### Validation Repo
```
Validation-github-action/
├── .github/
│   └── workflows/
│       └── validation-service.yml
└── scripts/
    ├── configure-packages.py
    ├── upload-assets.py
    ├── validate-assets.py
    ├── upload-capability.py
    ├── validate-examples.py
    └── generate-report.py
```

### Assets Repo
```
your-fhir-assets/
├── .github/
│   └── workflows/
│       └── trigger-validation.yml
├── fhir/                      # Or your conformance dir
│   └── StructureDefinition-*.json
├── examples/                  # Or your examples dir
│   └── *.json
├── package.json
└── CapabilityStatement.json
```

### FHIR Service Repo
```
FHIR-JPA-Service/
├── Dockerfile
├── application.yaml
└── (your custom code)
```

## Common Issues Checklist

If validation doesn't trigger:
- [ ] PAT_TOKEN added to BOTH repos?
- [ ] validation-service.yml on main branch?
- [ ] trigger-validation.yml on main branch?
- [ ] Repository names correct in workflows?

If FHIR service doesn't start:
- [ ] Dockerfile builds successfully?
- [ ] Port 8080 exposed?
- [ ] Health check endpoint working?

If validation fails:
- [ ] Assets copied to correct location?
- [ ] package.json present?
- [ ] CapabilityStatement.json present?
- [ ] FHIR resources valid?

## Success Indicators

You know it's working when:
✅ Push to assets repo triggers workflow
✅ Validation repo workflow starts automatically  
✅ FHIR service builds and starts
✅ Validation completes
✅ PR comment appears with results
✅ Commit status shows success/failure

## Next Steps After Setup

1. Customize validation rules in scripts
2. Adjust paths to match your repo structure
3. Configure FHIR service environment variables
4. Add validation badge to README
5. Set up branch protection rules requiring validation

## Need Help?

See CROSS-REPO-SETUP.md for:
- Detailed setup instructions
- Troubleshooting guide
- Advanced configuration
- Security notes
