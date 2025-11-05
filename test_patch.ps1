$apiUrl = "http://localhost:8000"
$caseId = "930e9c0f-66e6-474e-9e1e-000f9e0ce5d3"

Write-Host "Login..." -ForegroundColor Cyan
$login = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method Post -ContentType "application/json" -Body (@{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json)
$token = $login.access_token
Write-Host "OK: Token received" -ForegroundColor Green

Write-Host "Getting current data..." -ForegroundColor Cyan
$current = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Get -Headers @{
    Authorization = "Bearer $token"
}
Write-Host "Current summary: $($current.summary)" -ForegroundColor Yellow

Write-Host "Updating summary..." -ForegroundColor Cyan
$newSummary = "TEST UPDATE - $(Get-Date -Format 'HH:mm:ss')"
$updateData = @{
    summary = $newSummary
} | ConvertTo-Json

Write-Host "Sending: $updateData" -ForegroundColor Gray

try {
    $updated = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Patch -ContentType "application/json" -Headers @{
        Authorization = "Bearer $token"
    } -Body $updateData
    
    Write-Host "SUCCESS: Updated" -ForegroundColor Green
    Write-Host "New summary: $($updated.summary)" -ForegroundColor Green
    
    if ($updated.summary -eq $newSummary) {
        Write-Host "DATA SAVED CORRECTLY" -ForegroundColor Green
    } else {
        Write-Host "DATA MISMATCH" -ForegroundColor Red
        Write-Host "Expected: $newSummary" -ForegroundColor Yellow
        Write-Host "Got: $($updated.summary)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}
