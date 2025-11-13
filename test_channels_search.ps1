# Тестування пошуку каналів
$baseUrl = "https://10.24.2.187/api"

Write-Host "Testing channels search..." -ForegroundColor Green

try {
    # Робимо запит з пошуком
    $url = "$baseUrl/api/channels?skip=0&limit=10&search=Emai&include_inactive=true"
    Write-Host "URL: $url" -ForegroundColor Cyan
    
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
    
    $response = Invoke-RestMethod -Uri $url -Method Get
    
    Write-Host "`nTotal channels found: $($response.total)" -ForegroundColor Yellow
    Write-Host "Channels returned: $($response.channels.Count)" -ForegroundColor Yellow
    
    Write-Host "`nChannels:" -ForegroundColor Cyan
    $response.channels | ForEach-Object {
        Write-Host "  - $($_.name) (Active: $($_.is_active))"
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.Exception.ToString() -ForegroundColor Red
}
