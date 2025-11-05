# Тест виправлення редагування звернень
# Перевіряє, чи зберігаються зміни після редагування адміністратором

$apiUrl = "http://localhost:8000"

Write-Host "===== Тест виправлення редагування звернень =====" -ForegroundColor Cyan

# 1. Авторізація ADMIN
Write-Host "`n[1] Авторізація ADMIN..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method Post -Body (@{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json) -ContentType "application/json"

$token = $loginResponse.access_token
Write-Host "✓ Авторизація успішна" -ForegroundColor Green

# 2. Отримуємо список звернень
Write-Host "`n[2] Отримання списку звернень..." -ForegroundColor Yellow
$casesResponse = Invoke-RestMethod -Uri "$apiUrl/api/cases?limit=1" -Method Get -Headers @{
    "Authorization" = "Bearer $token"
}

if ($casesResponse.cases.Count -eq 0) {
    Write-Host "✗ Немає звернень для тестування" -ForegroundColor Red
    exit 1
}

$caseId = $casesResponse.cases[0].id
$casePublicId = $casesResponse.cases[0].public_id
Write-Host "✓ Звернення отримано: #$casePublicId (ID: $caseId)" -ForegroundColor Green

# 3. Отримуємо детальну інформацію про звернення
Write-Host "`n[3] Отримання деталей звернення..." -ForegroundColor Yellow
$beforeUpdate = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Get -Headers @{
    "Authorization" = "Bearer $token"
}
Write-Host "Поточні дані:" -ForegroundColor Cyan
Write-Host "  Ім'я: $($beforeUpdate.applicant_name)" -ForegroundColor White
Write-Host "  Телефон: $($beforeUpdate.applicant_phone)" -ForegroundColor White
Write-Host "  Email: $($beforeUpdate.applicant_email)" -ForegroundColor White
Write-Host "  Опис: $($beforeUpdate.summary.Substring(0, [Math]::Min(50, $beforeUpdate.summary.Length)))..." -ForegroundColor White

# 4. Редагуємо звернення
Write-Host "`n[4] Редагування звернення..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "HH:mm:ss"
$updateData = @{
    applicant_name = "Тестовий Користувач (Оновлено $timestamp)"
    applicant_phone = "+380671234567"
    applicant_email = "test_updated@example.com"
    summary = "Оновлений опис звернення - тест виправлення багу ($timestamp)"
}

Write-Host "Відправляємо оновлені дані:" -ForegroundColor Cyan
$updateData | ConvertTo-Json | Write-Host -ForegroundColor Gray

try {
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    $body = $updateData | ConvertTo-Json
    $updateResponse = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Patch -Body $body -Headers $headers
    Write-Host "✓ Запит на оновлення виконано успішно" -ForegroundColor Green
}
catch {
    Write-Host "✗ Помилка при оновленні: $_" -ForegroundColor Red
    exit 1
}

# 5. Перевіряємо, чи збереглися зміни
Write-Host "`n[5] Перевірка збережених змін..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
$afterUpdate = Invoke-RestMethod -Uri "$apiUrl/api/cases/$caseId" -Method Get -Headers @{
    "Authorization" = "Bearer $token"
}

Write-Host "Оновлені дані:" -ForegroundColor Cyan
Write-Host "  Ім'я: $($afterUpdate.applicant_name)" -ForegroundColor White
Write-Host "  Телефон: $($afterUpdate.applicant_phone)" -ForegroundColor White
Write-Host "  Email: $($afterUpdate.applicant_email)" -ForegroundColor White
Write-Host "  Опис: $($afterUpdate.summary.Substring(0, [Math]::Min(50, $afterUpdate.summary.Length)))..." -ForegroundColor White

# 6. Порівнюємо значення
Write-Host "`n[6] Перевірка результатів..." -ForegroundColor Yellow
$allMatch = $true

if ($afterUpdate.applicant_name -ne $updateData.applicant_name) {
    Write-Host "✗ Ім'я не збереглося!" -ForegroundColor Red
    Write-Host "  Очікувалось: $($updateData.applicant_name)" -ForegroundColor Gray
    Write-Host "  Отримано: $($afterUpdate.applicant_name)" -ForegroundColor Gray
    $allMatch = $false
} else {
    Write-Host "✓ Ім'я збережено правильно" -ForegroundColor Green
}

if ($afterUpdate.applicant_phone -ne $updateData.applicant_phone) {
    Write-Host "✗ Телефон не зберігся!" -ForegroundColor Red
    Write-Host "  Очікувалось: $($updateData.applicant_phone)" -ForegroundColor Gray
    Write-Host "  Отримано: $($afterUpdate.applicant_phone)" -ForegroundColor Gray
    $allMatch = $false
} else {
    Write-Host "✓ Телефон збережено правильно" -ForegroundColor Green
}

if ($afterUpdate.applicant_email -ne $updateData.applicant_email) {
    Write-Host "✗ Email не зберігся!" -ForegroundColor Red
    Write-Host "  Очікувалось: $($updateData.applicant_email)" -ForegroundColor Gray
    Write-Host "  Отримано: $($afterUpdate.applicant_email)" -ForegroundColor Gray
    $allMatch = $false
} else {
    Write-Host "✓ Email збережено правильно" -ForegroundColor Green
}

if ($afterUpdate.summary -ne $updateData.summary) {
    Write-Host "✗ Опис не зберігся!" -ForegroundColor Red
    Write-Host "  Очікувалось: $($updateData.summary)" -ForegroundColor Gray
    Write-Host "  Отримано: $($afterUpdate.summary)" -ForegroundColor Gray
    $allMatch = $false
} else {
    Write-Host "✓ Опис збережено правильно" -ForegroundColor Green
}

# Підсумок
Write-Host "`n===== ПІДСУМОК =====" -ForegroundColor Cyan
if ($allMatch) {
    Write-Host "✓ ВСІ ЗМІНИ ЗБЕРЕГЛИСЯ ПРАВИЛЬНО!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ ДЕЯКІ ЗМІНИ НЕ ЗБЕРЕГЛИСЯ!" -ForegroundColor Red
    exit 1
}
