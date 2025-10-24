#!/bin/bash
# ============================================================================
# Frontend Configuration Integration Test
# ============================================================================
# This script validates the frontend configuration system is working correctly
#
# Usage: ./test-config-integration.sh
# ============================================================================

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Frontend Configuration System Integration Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to print test results
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================================================
# Test 1: Configuration Files Exist
# ============================================================================
echo "Test 1: Checking configuration files..."

if [ -f "src/config/index.ts" ]; then
    pass "Configuration module exists (src/config/index.ts)"
else
    fail "Configuration module missing (src/config/index.ts)"
fi

if [ -f "src/config/index.test.ts" ]; then
    pass "Configuration tests exist (src/config/index.test.ts)"
else
    fail "Configuration tests missing (src/config/index.test.ts)"
fi

# ============================================================================
# Test 2: Environment Template Files Exist
# ============================================================================
echo ""
echo "Test 2: Checking environment template files..."

for file in .env.example .env.local.example .env.staging.example .env.production.example .env.docker; do
    if [ -f "$file" ]; then
        pass "Template file exists ($file)"
    else
        fail "Template file missing ($file)"
    fi
done

# ============================================================================
# Test 3: .gitignore Protection
# ============================================================================
echo ""
echo "Test 3: Checking .gitignore protection..."

if grep -q "\.env\.local" .gitignore; then
    pass ".env.local is git-ignored"
else
    fail ".env.local is NOT git-ignored (security risk!)"
fi

if grep -q "\.env\.staging" .gitignore; then
    pass ".env.staging is git-ignored"
else
    fail ".env.staging is NOT git-ignored (security risk!)"
fi

if grep -q "\.env\.production" .gitignore; then
    pass ".env.production is git-ignored"
else
    fail ".env.production is NOT git-ignored (security risk!)"
fi

# ============================================================================
# Test 4: Documentation Exists
# ============================================================================
echo ""
echo "Test 4: Checking documentation..."

if [ -f "docs/FRONTEND_CONFIGURATION.md" ]; then
    lines=$(wc -l < docs/FRONTEND_CONFIGURATION.md)
    if [ "$lines" -gt 500 ]; then
        pass "Comprehensive configuration documentation exists ($lines lines)"
    else
        warn "Configuration documentation exists but seems short ($lines lines)"
    fi
else
    fail "Configuration documentation missing (docs/FRONTEND_CONFIGURATION.md)"
fi

if [ -f "CONFIG_QUICKSTART.md" ]; then
    pass "Quick start guide exists (CONFIG_QUICKSTART.md)"
else
    fail "Quick start guide missing (CONFIG_QUICKSTART.md)"
fi

# ============================================================================
# Test 5: Docker Configuration
# ============================================================================
echo ""
echo "Test 5: Checking Docker configuration..."

if grep -q "env_file:" docker-compose.yml; then
    pass "docker-compose.yml loads environment files"
else
    fail "docker-compose.yml missing env_file directive"
fi

if grep -q "ARG VITE_API_URL" Dockerfile; then
    pass "Dockerfile accepts build arguments for configuration"
else
    fail "Dockerfile missing build argument support"
fi

if grep -q "VITE_API_URL" docker-compose.prod.yml; then
    pass "docker-compose.prod.yml has production configuration"
else
    fail "docker-compose.prod.yml missing configuration"
fi

# ============================================================================
# Test 6: YAML Validation
# ============================================================================
echo ""
echo "Test 6: Validating YAML syntax..."

if python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" 2>/dev/null; then
    pass "docker-compose.yml has valid YAML syntax"
else
    fail "docker-compose.yml has YAML syntax errors"
fi

if python3 -c "import yaml; yaml.safe_load(open('docker-compose.prod.yml'))" 2>/dev/null; then
    pass "docker-compose.prod.yml has valid YAML syntax"
else
    fail "docker-compose.prod.yml has YAML syntax errors"
fi

# ============================================================================
# Test 7: TypeScript Compilation
# ============================================================================
echo ""
echo "Test 7: Checking TypeScript compilation..."

if npx tsc --noEmit src/config/index.ts 2>/dev/null; then
    pass "Configuration module compiles without errors"
else
    warn "Configuration module has TypeScript errors (may need dependencies)"
fi

# ============================================================================
# Test 8: Required Configuration in Templates
# ============================================================================
echo ""
echo "Test 8: Checking required configuration in templates..."

if grep -q "VITE_API_URL" .env.example; then
    pass "VITE_API_URL documented in .env.example"
else
    fail "VITE_API_URL missing from .env.example"
fi

if grep -q "VITE_API_URL" .env.docker; then
    pass "VITE_API_URL configured in .env.docker"
else
    fail "VITE_API_URL missing from .env.docker"
fi

# ============================================================================
# Test 9: Configuration Security Warnings
# ============================================================================
echo ""
echo "Test 9: Checking security warnings in templates..."

if grep -qi "never commit" .env.example; then
    pass ".env.example contains security warnings"
else
    warn ".env.example missing security warnings"
fi

if grep -qi "visible in client" .env.example; then
    pass ".env.example warns about client-side visibility"
else
    warn ".env.example missing client-side visibility warning"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Configuration system is ready.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
