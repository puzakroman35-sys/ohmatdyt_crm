# Тестування пошуку каналів (кілька варіантів)
$baseUrl = "https://10.24.2.187/api"

# Ігноруємо SSL помилки
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

Write-Host "=== Тестування пошуку каналів ===" -ForegroundColor Green

# Тест 1: Пошук "Emai"
Write-Host "`n1. Пошук 'Emai':" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$baseUrl/api/channels?search=Emai&include_inactive=true"
Write-Host "   Знайдено: $($response.total) ($($response.channels.name -join ', '))" -ForegroundColor Yellow

# Тест 2: Пошук "QR"
Write-Host "`n2. Пошук 'QR':" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$baseUrl/api/channels?search=QR&include_inactive=true"
Write-Host "   Знайдено: $($response.total) ($($response.channels.name -join ', '))" -ForegroundColor Yellow

# Тест 3: Пошук "онта" (має знайти "Контакт-центр")
Write-Host "`n3. Пошук 'онта':" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$baseUrl/api/channels?search=онта&include_inactive=true"
Write-Host "   Знайдено: $($response.total) ($($response.channels.name -join ', '))" -ForegroundColor Yellow

# Тест 4: Пошук "ре" (має знайти "Рецепція")
Write-Host "`n4. Пошук 'ре':" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$baseUrl/api/channels?search=ре&include_inactive=true"
Write-Host "   Знайдено: $($response.total) ($($response.channels.name -join ', '))" -ForegroundColor Yellow

# Тест 5: Без пошуку (всі канали)
Write-Host "`n5. Без пошуку (всі):" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$baseUrl/api/channels?include_inactive=true"
Write-Host "   Знайдено: $($response.total) каналів" -ForegroundColor Yellow

Write-Host "`n=== Тести завершено! ===" -ForegroundColor Green
