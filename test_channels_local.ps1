# Тестування пошуку каналів напряму через локальний API
$baseUrl = "http://localhost:8000"

Write-Host "Testing channels search on local API..." -ForegroundColor Green

try {
    # Робимо запит з пошуком
    $url = "$baseUrl/api/channels?skip=0&limit=10&search=Emai&include_inactive=true"
    Write-Host "URL: $url" -ForegroundColor Cyan
    
    $response = Invoke-RestMethod -Uri $url -Method Get
    
    Write-Host "`nTotal channels found: $($response.total)" -ForegroundColor Yellow
    Write-Host "Channels returned: $($response.channels.Count)" -ForegroundColor Yellow
    
    Write-Host "`nChannels:" -ForegroundColor Cyan
    $response.channels | ForEach-Object {
        Write-Host "  - $($_.name) (Active: $($_.is_active))"
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
