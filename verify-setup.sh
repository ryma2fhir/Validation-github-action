#!/bin/bash
# Verify cross-repo validation setup

set -e

echo "=================================================="
echo "FHIR Validation Setup Verification"
echo "=================================================="
echo ""

VALIDATION_REPO="ryma2fhir/Validation-github-action"
SERVICE_REPO="ryma2fhir/FHIR-JPA-Service"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

ERRORS=0

echo "Checking Validation Repository..."
echo "----------------------------------"

# Check if in validation repo
if [ -d ".github/workflows" ]; then
    check_ok "Found .github/workflows directory"
else
    check_fail "Missing .github/workflows directory"
fi

# Check for validation service workflow
if [ -f ".github/workflows/validation-service.yml" ]; then
    check_ok "Found validation-service.yml"
else
    check_fail "Missing .github/workflows/validation-service.yml"
fi

# Check for scripts
if [ -d "scripts" ]; then
    check_ok "Found scripts directory"
    
    required_scripts=(
        "configure-packages.py"
        "upload-assets.py"
        "validate-assets.py"
        "upload-capability.py"
        "validate-examples.py"
        "generate-report.py"
    )
    
    for script in "${required_scripts[@]}"; do
        if [ -f "scripts/$script" ]; then
            check_ok "Found scripts/$script"
        else
            check_fail "Missing scripts/$script"
        fi
    done
else
    check_fail "Missing scripts directory"
fi

echo ""
echo "Checking Workflow Configuration..."
echo "----------------------------------"

# Check validation-service.yml configuration
if [ -f ".github/workflows/validation-service.yml" ]; then
    # Check for required secrets
    if grep -q "PAT_TOKEN" ".github/workflows/validation-service.yml"; then
        check_ok "Workflow uses PAT_TOKEN"
        check_warn "Make sure PAT_TOKEN secret is set in repository settings"
    else
        check_warn "Workflow might not use PAT_TOKEN"
    fi
    
    # Check for correct repos
    if grep -q "$SERVICE_REPO" ".github/workflows/validation-service.yml"; then
        check_ok "References $SERVICE_REPO"
    else
        check_fail "Doesn't reference $SERVICE_REPO"
    fi
fi

echo ""
echo "Checking Python Scripts..."
echo "----------------------------------"

# Check if scripts are executable
if [ -d "scripts" ]; then
    for script in scripts/*.py; do
        if [ -x "$script" ]; then
            check_ok "$(basename $script) is executable"
        else
            check_warn "$(basename $script) is not executable (chmod +x recommended)"
        fi
    done
fi

# Check for Python dependencies
if command -v python3 &> /dev/null; then
    check_ok "Python3 is installed"
    
    # Check if requests module is available
    if python3 -c "import requests" 2>/dev/null; then
        check_ok "Python requests module available"
    else
        check_warn "Python requests module not found (pip install requests)"
    fi
    
    # Check if yaml module is available
    if python3 -c "import yaml" 2>/dev/null; then
        check_ok "Python yaml module available"
    else
        check_warn "Python yaml module not found (pip install pyyaml)"
    fi
else
    check_fail "Python3 not installed"
fi

echo ""
echo "Checking Docker..."
echo "----------------------------------"

if command -v docker &> /dev/null; then
    check_ok "Docker is installed"
    
    # Check if Docker is running
    if docker info &> /dev/null; then
        check_ok "Docker daemon is running"
    else
        check_warn "Docker daemon not running (start Docker)"
    fi
else
    check_fail "Docker not installed"
fi

echo ""
echo "Summary..."
echo "----------------------------------"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Ensure PAT_TOKEN secret is set in repository settings"
    echo "2. Verify FHIR-JPA-Service repo has a Dockerfile"
    echo "3. Test manually: Actions → FHIR Validation Service → Run workflow"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS error(s)${NC}"
    echo ""
    echo "Please fix the errors above before proceeding"
    exit 1
fi
