# Тестовий запит до API
$url = "http://localhost:8000/api/users?skip=0&limit=20&search=admin&order_by=created_at&order=desc"

Write-Host "Making request to: $url" -ForegroundColor Green

try {
    # Отримуємо токен
    $loginBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    
    $token = $loginResponse.access_token
    Write-Host "Login successful" -ForegroundColor Green
    
    # Робимо запит з токеном
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
    
    Write-Host "Total users: $($response.total)" -ForegroundColor Cyan
    Write-Host "Returned: $($response.users.Count) users" -ForegroundColor Cyan
    
    Write-Host "First 3 users:"
    $response.users | Select-Object -First 3 | ForEach-Object {
        Write-Host "  - $($_.username) ($($_.full_name)) - $($_.email)"
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
