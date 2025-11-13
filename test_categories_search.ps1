# Тестування пошуку категорій (локально)
$baseUrl = "http://localhost:8000"

Write-Host "=== Тестування пошуку категорій ===" -ForegroundColor Green

try {
    # Тест 1: Пошук "Інш" (має знайти "Інше")
    Write-Host "`n1. Пошук 'Інш':" -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/api/categories?search=Інш&include_inactive=true"
    Write-Host "   Знайдено: $($response.total) категорій" -ForegroundColor Yellow
    $response.categories | ForEach-Object { Write-Host "     - $($_.name)" }

    # Тест 2: Пошук "Сервіс"
    Write-Host "`n2. Пошук 'Сервіс':" -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/api/categories?search=Сервіс&include_inactive=true"
    Write-Host "   Знайдено: $($response.total) категорій" -ForegroundColor Yellow
    $response.categories | ForEach-Object { Write-Host "     - $($_.name)" }

    # Тест 3: Пошук "ком" (має знайти "Комунікація...")
    Write-Host "`n3. Пошук 'ком':" -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/api/categories?search=ком&include_inactive=true"
    Write-Host "   Знайдено: $($response.total) категорій" -ForegroundColor Yellow
    $response.categories | ForEach-Object { Write-Host "     - $($_.name)" }

    # Тест 4: Без пошуку (всі категорії)
    Write-Host "`n4. Без пошуку (всі):" -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/api/categories?include_inactive=true"
    Write-Host "   Знайдено: $($response.total) категорій" -ForegroundColor Yellow

    Write-Host "`n=== Локальні тести успішні! ===" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
