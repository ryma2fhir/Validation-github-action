#!/bin/bash
# Local FHIR validation test runner
# Runs the same validation steps as GitHub Actions

set -e

echo "=================================================="
echo "FHIR Validation Test Runner"
echo "=================================================="
echo ""

# Check if HAPI FHIR is running
echo "Checking HAPI FHIR server..."
if ! curl -sf http://localhost:8080/fhir/metadata > /dev/null; then
    echo "HAPI FHIR not running on localhost:8080"
    echo ""
    echo "Start it with:"
    echo "  docker run -d -p 8080:8080 hapiproject/hapi:latest"
    echo ""
    echo "Or use your custom image:"
    echo "  docker run -d -p 8080:8080 your-registry/your-custom-hapi:latest"
    exit 1
fi
echo "HAPI FHIR is running"
echo ""

# Run validation steps
echo "Step 1: Installing FHIR packages..."
python3 scripts/configure-packages.py || exit 1
echo ""

echo "Step 2: Uploading conformance assets..."
python3 scripts/upload-assets.py || exit 1
echo ""

echo "Step 3: Validating conformance assets..."
python3 scripts/validate-assets.py || exit 1
echo ""

echo "Step 4: Uploading CapabilityStatement..."
python3 scripts/upload-capability.py || exit 1
echo ""

echo "Step 5: Validating examples..."
python3 scripts/validate-examples.py || exit 1
echo ""

echo "Step 6: Generating report..."
python3 scripts/generate-report.py || exit 1
echo ""

echo "=================================================="
echo "Validation Complete!"
echo "=================================================="
echo ""
echo "Report saved to: validation-report.md"
echo "Results saved to: validation-results.json"
echo ""
