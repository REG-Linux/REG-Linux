#!/bin/bash
# REG-Linux ConfigGen - Code Quality Verification Script
# Run all linting, formatting, and type checking tools

set -e

# Get the directory where the script is located and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================"
echo "REG-Linux ConfigGen - Quality Check"
echo "========================================"
echo "Location: $PROJECT_ROOT"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# 1. Ruff Check
echo -e "${YELLOW}[1/4] Running Ruff Check...${NC}"
if ruff check configgen/; then
    echo -e "${GREEN}✓ Ruff Check: PASSED${NC}"
else
    echo -e "${RED}✗ Ruff Check: FAILED${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 2. Ruff Format
echo -e "${YELLOW}[2/4] Running Ruff Format Check...${NC}"
if ruff format configgen/ --check; then
    echo -e "${GREEN}✓ Ruff Format: PASSED${NC}"
else
    echo -e "${RED}✗ Ruff Format: FAILED${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 3. Pyright
echo -e "${YELLOW}[3/4] Running Pyright Type Check...${NC}"
if pyright configgen/; then
    echo -e "${GREEN}✓ Pyright: PASSED${NC}"
else
    echo -e "${RED}✗ Pyright: FAILED${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 4. Rumdl (Markdown lint)
echo -e "${YELLOW}[4/4] Running Rumdl Markdown Check...${NC}"
if rumdl check README.md QWEN.md; then
    echo -e "${GREEN}✓ Rumdl: PASSED${NC}"
else
    echo -e "${RED}✗ Rumdl: FAILED${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Summary
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All checks passed! ✓${NC}"
    echo "========================================"
    exit 0
else
    echo -e "${RED}$ERRORS check(s) failed! ✗${NC}"
    echo "========================================"
    exit 1
fi
