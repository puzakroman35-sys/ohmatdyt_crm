# Test script to verify /api/cases/{case_id}/assign endpoint
Write-Host "Testing /api/cases/{case_id}/assign endpoint..." -ForegroundColor Yellow
Write-Host ""

$BASE_URL = "http://localhost:8000"
$CASE_ID = "c58671d2-bb38-41cb-845e-e7b7f49faafb"

Write-Host "Step 1: Get admin token" -ForegroundColor Cyan
$loginBody = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-WebRequest `
        -Uri "$BASE_URL/api/auth/login" `
        -Method POST `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = ($loginResponse.Content | ConvertFrom-Json).access_token
    Write-Host "✓ Got admin token" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "✗ Failed to login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Get list of active executors" -ForegroundColor Cyan
try {
    $usersResponse = Invoke-WebRequest `
        -Uri "$BASE_URL/api/users?is_active=true&role=EXECUTOR&limit=10" `
        -Method GET `
        -Headers @{ Authorization = "Bearer $token" }
    
    $users = ($usersResponse.Content | ConvertFrom-Json).users
    
    if ($users.Count -gt 0) {
        $executor = $users[0]
        Write-Host "✓ Found executor: $($executor.username) ($($executor.id))" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "✗ No executors found" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Failed to get users: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Step 3: Assign executor to case" -ForegroundColor Cyan
$assignBody = @{
    assigned_to_id = $executor.id
} | ConvertTo-Json

try {
    $assignResponse = Invoke-WebRequest `
        -Uri "$BASE_URL/api/cases/$CASE_ID/assign" `
        -Method PATCH `
        -Body $assignBody `
        -ContentType "application/json" `
        -Headers @{ Authorization = "Bearer $token" }
    
    $updatedCase = $assignResponse.Content | ConvertFrom-Json
    Write-Host "✓ Successfully assigned executor to case" -ForegroundColor Green
    Write-Host "  Case ID: $($updatedCase.id)" -ForegroundColor Gray
    Write-Host "  Public ID: $($updatedCase.public_id)" -ForegroundColor Gray
    Write-Host "  Status: $($updatedCase.status)" -ForegroundColor Gray
    Write-Host "  Assigned to: $($updatedCase.responsible_id)" -ForegroundColor Gray
    Write-Host ""
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorBody = $_.ErrorDetails.Message
    Write-Host "✗ Failed to assign executor (Status: $statusCode)" -ForegroundColor Red
    Write-Host "  Error: $errorBody" -ForegroundColor Red
    exit 1
}

Write-Host "All tests passed! ✓" -ForegroundColor Green
