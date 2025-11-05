# Тест оновлення звернення
# Перевіряє, чи працює PATCH /api/cases/{case_id}

$apiUrl = "http://localhost:8000"

# Отримуємо токен ADMIN
Write-Host "Авторизація ADMIN..." -ForegroundColor Cyan
$loginResponse = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method Post -Body (@{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json) -ContentType "application/json"

$token = $loginResponse.access_token
Write-Host "✓ Авторизація успішна" -ForegroundColor Green

# Отримуємо список звернень
Write-Host "`nОтримання списку звернень..." -ForegroundColor Cyan
$casesResponse = Invoke-RestMethod -Uri "$apiUrl/api/cases?limit=1" -Method Get -Headers @{
    Authorization = "Bearer $token"
}

if ($casesResponse.cases.Count -eq 0) {
    Write-Host "✗ Немає звернень для тестування" -ForegroundColor Red
    exit 1
}

$testCase = $casesResponse.cases[0]
$caseId = $testCase.id
Write-Host "✓ Звернення знайдено: #$($testCase.public_id)" -ForegroundColor Green
Write-Host "  Поточне ім'я заявника: $($testCase.applicant_name)" -ForegroundColor Gray
Write-Host "  Поточний телефон: $($testCase.applicant_phone)" -ForegroundColor Gray
Write-Host "  Поточний email: $($testCase.applicant_email)" -ForegroundColor Gray

# Оновлюємо звернення
Write-Host "`nОновлення звернення..." -ForegroundColor Cyan
$updateData = @{
    applicant_name = "Тестовий Заявник (Оновлено)"
    applicant_phone = "+380671234567"
    applicant_email = "updated@test.com"
    summary = "Оновлений опис звернення - тест $(Get-Date -Format 'HH:mm:ss')"
}

try {
    $updateResponse = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Patch -Body ($updateData | ConvertTo-Json) -ContentType "application/json" -Headers @{
        Authorization = "Bearer $token"
    }
    
    Write-Host "✓ Звернення успішно оновлено!" -ForegroundColor Green
    Write-Host "  Нове ім'я: $($updateResponse.applicant_name)" -ForegroundColor Green
    Write-Host "  Новий телефон: $($updateResponse.applicant_phone)" -ForegroundColor Green
    Write-Host "  Новий email: $($updateResponse.applicant_email)" -ForegroundColor Green
    Write-Host "  Новий опис: $($updateResponse.summary)" -ForegroundColor Green
    
    # Перевірка
    if ($updateResponse.applicant_name -eq $updateData.applicant_name -and
        $updateResponse.applicant_phone -eq $updateData.applicant_phone -and
        $updateResponse.applicant_email -eq $updateData.applicant_email) {
        Write-Host "`n✓✓✓ ТЕСТ ПРОЙДЕНО УСПІШНО ✓✓✓" -ForegroundColor Green
    } else {
        Write-Host "`n✗ Дані не збіглися після оновлення" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Помилка при оновленні:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}
