#!/bin/bash

# Smoke Test Runner for CultureBridge
# This script runs critical smoke tests to verify the application is working

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "========================================="
echo "CultureBridge Smoke Tests"
echo "========================================="
echo "API URL: $API_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Initialize counters
TOTAL_TESTS=0
FAILED_TESTS=0

# Test 1: Health Check
echo "Running Test 1: Health Check..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Health endpoint returns 200"
else
    print_result 1 "Health endpoint returns $HTTP_CODE (expected 200)"
fi

# Test 2: API Documentation
echo "Running Test 2: API Documentation..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/docs")
if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Swagger UI accessible"
else
    print_result 1 "Swagger UI returns $HTTP_CODE (expected 200)"
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/openapi.json")
if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "OpenAPI JSON accessible"
else
    print_result 1 "OpenAPI JSON returns $HTTP_CODE (expected 200)"
fi

# Test 3: User Signup
echo "Running Test 3: User Signup..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
RANDOM_EMAIL="smoketest_$(date +%s)@test.com"
SIGNUP_RESPONSE=$(curl -s -X POST "$API_URL/auth/signup" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$RANDOM_EMAIL\",\"password\":\"TestPassword123!\",\"role\":\"client\"}")

if echo "$SIGNUP_RESPONSE" | grep -q "\"email\""; then
    print_result 0 "User signup successful"
    
    # Test 4: User Login
    echo "Running Test 4: User Login..."
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$RANDOM_EMAIL\",\"password\":\"TestPassword123!\"}")
    
    if echo "$LOGIN_RESPONSE" | grep -q "\"access_token\""; then
        print_result 0 "User login successful"
        
        # Extract token
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        
        # Test 5: Authenticated Request
        echo "Running Test 5: Authenticated Request..."
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/profile" \
            -H "Authorization: Bearer $TOKEN")
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
            print_result 0 "Authenticated request successful (status: $HTTP_CODE)"
        else
            print_result 1 "Authenticated request failed (status: $HTTP_CODE)"
        fi
        
        # Test 6: List Coaches
        echo "Running Test 6: List Coaches..."
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/coaches" \
            -H "Authorization: Bearer $TOKEN")
        if [ "$HTTP_CODE" = "200" ]; then
            print_result 0 "List coaches endpoint accessible"
        else
            print_result 1 "List coaches returns $HTTP_CODE (expected 200)"
        fi
        
        # Test 7: Community Posts
        echo "Running Test 7: Community Posts..."
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/community/posts" \
            -H "Authorization: Bearer $TOKEN")
        if [ "$HTTP_CODE" = "200" ]; then
            print_result 0 "Community posts endpoint accessible"
        else
            print_result 1 "Community posts returns $HTTP_CODE (expected 200)"
        fi
    else
        print_result 1 "User login failed"
    fi
else
    print_result 1 "User signup failed"
fi

# Test 8: Unauthenticated Request Rejection
echo "Running Test 8: Unauthenticated Request Rejection..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/profile")
if [ "$HTTP_CODE" = "401" ]; then
    print_result 0 "Unauthenticated request properly rejected"
else
    print_result 1 "Unauthenticated request returns $HTTP_CODE (expected 401)"
fi

# Test 9: Frontend Accessibility
echo "Running Test 9: Frontend Accessibility..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Frontend accessible"
else
    print_result 1 "Frontend returns $HTTP_CODE (expected 200)"
fi

# Test 10: Database Connectivity (via health check)
echo "Running Test 10: Database Connectivity..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q '"database":"connected"'; then
    print_result 0 "Database connected"
else
    print_result 1 "Database connection issue"
fi

# Test 11: Redis Connectivity (via health check)
echo "Running Test 11: Redis Connectivity..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if echo "$HEALTH_RESPONSE" | grep -q '"redis":"connected"'; then
    print_result 0 "Redis connected"
else
    print_result 1 "Redis connection issue"
fi

# Summary
echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $((TOTAL_TESTS - FAILED_TESTS))"
echo "Failed: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the output above.${NC}"
    exit 1
fi
