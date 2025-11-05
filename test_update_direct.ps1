# Прямий тест PATCH /api/cases/{id}
$apiUrl = "http://localhost:8000"
$caseId = "930e9c0f-66e6-474e-9e1e-000f9e0ce5d3"

# 1. Логін
Write-Host "Логін..." -ForegroundColor Cyan
$login = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method Post -ContentType "application/json" -Body (@{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json)
$token = $login.access_token
Write-Host "OK: Token отримано" -ForegroundColor Green

# 2. Отримати поточні дані
Write-Host "`nОтримання поточних даних..." -ForegroundColor Cyan
$current = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Get -Headers @{
    Authorization = "Bearer $token"
}
Write-Host "Поточний summary: $($current.summary)" -ForegroundColor Yellow

# 3. Оновити summary
Write-Host "`nОновлення summary..." -ForegroundColor Cyan
$newSummary = "ТЕСТ ОНОВЛЕННЯ - $(Get-Date -Format 'HH:mm:ss')"
$updateData = @{
    summary = $newSummary
} | ConvertTo-Json

Write-Host "Відправляю: $updateData" -ForegroundColor Gray

try {
    $updated = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Patch -ContentType "application/json" -Headers @{
        Authorization = "Bearer $token"
    } -Body $updateData
    
    Write-Host "OK: Оновлено успішно" -ForegroundColor Green
    Write-Host "Новий summary: $($updated.summary)" -ForegroundColor Green
    
    if ($updated.summary -eq $newSummary) {
        Write-Host "`nДАНІ ЗБЕРЕГЛИСЯ ПРАВИЛЬНО" -ForegroundColor Green
    } else {
        Write-Host "`nДАНІ НЕ ЗБІГЛИСЯ" -ForegroundColor Red
        Write-Host "Очікували: $newSummary" -ForegroundColor Yellow
        Write-Host "Отримали: $($updated.summary)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ПОМИЛКА" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}
