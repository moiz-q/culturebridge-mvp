# Smoke Test Runner for CultureBridge (PowerShell)
# This script runs critical smoke tests to verify the application is working

param(
    [string]$ApiUrl = "http://localhost:8000",
    [string]$FrontendUrl = "http://localhost:3000"
)

$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "CultureBridge Smoke Tests" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl"
Write-Host "Frontend URL: $FrontendUrl"
Write-Host ""

# Initialize counters
$TotalTests = 0
$FailedTests = 0

# Function to print test result
function Print-Result {
    param(
        [bool]$Success,
        [string]$Message
    )
    
    if ($Success) {
        Write-Host "✓ PASS: $Message" -ForegroundColor Green
    } else {
        Write-Host "✗ FAIL: $Message" -ForegroundColor Red
        $script:FailedTests++
    }
}

# Test 1: Health Check
Write-Host "Running Test 1: Health Check..."
$TotalTests++
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/health" -Method Get -UseBasicParsing
    Print-Result ($response.StatusCode -eq 200) "Health endpoint returns 200"
} catch {
    Print-Result $false "Health endpoint failed: $_"
}

# Test 2: API Documentation
Write-Host "Running Test 2: API Documentation..."
$TotalTests++
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/docs" -Method Get -UseBasicParsing
    Print-Result ($response.StatusCode -eq 200) "Swagger UI accessible"
} catch {
    Print-Result $false "Swagger UI failed: $_"
}

$TotalTests++
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/openapi.json" -Method Get -UseBasicParsing
    Print-Result ($response.StatusCode -eq 200) "OpenAPI JSON accessible"
} catch {
    Print-Result $false "OpenAPI JSON failed: $_"
}

# Test 3: User Signup
Write-Host "Running Test 3: User Signup..."
$TotalTests++
$RandomEmail = "smoketest_$(Get-Date -Format 'yyyyMMddHHmmss')@test.com"
$SignupBody = @{
    email = $RandomEmail
    password = "TestPassword123!"
    role = "client"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/auth/signup" -Method Post -Body $SignupBody -ContentType "application/json" -UseBasicParsing
    $signupData = $response.Content | ConvertFrom-Json
    
    if ($signupData.email) {
        Print-Result $true "User signup successful"
        
        # Test 4: User Login
        Write-Host "Running Test 4: User Login..."
        $TotalTests++
        $LoginBody = @{
            email = $RandomEmail
            password = "TestPassword123!"
        } | ConvertTo-Json
        
        try {
            $response = Invoke-WebRequest -Uri "$ApiUrl/auth/login" -Method Post -Body $LoginBody -ContentType "application/json" -UseBasicParsing
            $loginData = $response.Content | ConvertFrom-Json
            
            if ($loginData.access_token) {
                Print-Result $true "User login successful"
                $Token = $loginData.access_token
                
                # Test 5: Authenticated Request
                Write-Host "Running Test 5: Authenticated Request..."
                $TotalTests++
                try {
                    $headers = @{
                        Authorization = "Bearer $Token"
                    }
                    $response = Invoke-WebRequest -Uri "$ApiUrl/profile" -Method Get -Headers $headers -UseBasicParsing
                    Print-Result ($response.StatusCode -in @(200, 404)) "Authenticated request successful (status: $($response.StatusCode))"
                } catch {
                    $statusCode = $_.Exception.Response.StatusCode.value__
                    Print-Result ($statusCode -in @(200, 404)) "Authenticated request (status: $statusCode)"
                }
                
                # Test 6: List Coaches
                Write-Host "Running Test 6: List Coaches..."
                $TotalTests++
                try {
                    $response = Invoke-WebRequest -Uri "$ApiUrl/coaches" -Method Get -Headers $headers -UseBasicParsing
                    Print-Result ($response.StatusCode -eq 200) "List coaches endpoint accessible"
                } catch {
                    Print-Result $false "List coaches failed: $_"
                }
                
                # Test 7: Community Posts
                Write-Host "Running Test 7: Community Posts..."
                $TotalTests++
                try {
                    $response = Invoke-WebRequest -Uri "$ApiUrl/community/posts" -Method Get -Headers $headers -UseBasicParsing
                    Print-Result ($response.StatusCode -eq 200) "Community posts endpoint accessible"
                } catch {
                    Print-Result $false "Community posts failed: $_"
                }
            } else {
                Print-Result $false "User login failed - no token returned"
            }
        } catch {
            Print-Result $false "User login failed: $_"
        }
    } else {
        Print-Result $false "User signup failed - no email returned"
    }
} catch {
    Print-Result $false "User signup failed: $_"
}

# Test 8: Unauthenticated Request Rejection
Write-Host "Running Test 8: Unauthenticated Request Rejection..."
$TotalTests++
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/profile" -Method Get -UseBasicParsing
    Print-Result $false "Unauthenticated request should be rejected (got $($response.StatusCode))"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Print-Result ($statusCode -eq 401) "Unauthenticated request properly rejected"
}

# Test 9: Frontend Accessibility
Write-Host "Running Test 9: Frontend Accessibility..."
$TotalTests++
try {
    $response = Invoke-WebRequest -Uri $FrontendUrl -Method Get -UseBasicParsing
    Print-Result ($response.StatusCode -eq 200) "Frontend accessible"
} catch {
    Print-Result $false "Frontend failed: $_"
}

# Test 10: Database Connectivity
Write-Host "Running Test 10: Database Connectivity..."
$TotalTests++
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/health" -Method Get -UseBasicParsing
    $healthData = $response.Content | ConvertFrom-Json
    Print-Result ($healthData.database -eq "connected") "Database connected"
} catch {
    Print-Result $false "Database connectivity check failed: $_"
}

# Test 11: Redis Connectivity
Write-Host "Running Test 11: Redis Connectivity..."
$TotalTests++
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/health" -Method Get -UseBasicParsing
    $healthData = $response.Content | ConvertFrom-Json
    Print-Result ($healthData.redis -eq "connected") "Redis connected"
} catch {
    Print-Result $false "Redis connectivity check failed: $_"
}

# Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Total Tests: $TotalTests"
Write-Host "Passed: $($TotalTests - $FailedTests)"
Write-Host "Failed: $FailedTests"
Write-Host ""

if ($FailedTests -eq 0) {
    Write-Host "All smoke tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed. Please review the output above." -ForegroundColor Red
    exit 1
}
