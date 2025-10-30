# INF-003: Quick Production Setup Script
# This script helps setup production environment with HTTPS

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "self-signed", "letsencrypt")]
    [string]$Mode = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$Domain = "localhost",
    
    [Parameter(Mandatory=$false)]
    [string]$Email = ""
)

$ErrorActionPreference = "Stop"

Write-Host "================================================================================`n" -ForegroundColor Cyan
Write-Host "  INF-003: Production Nginx Setup`n" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Show mode selection
Write-Host "Вибраний режим: $Mode" -ForegroundColor Yellow
Write-Host ""

switch ($Mode) {
    "dev" {
        Write-Host "🔧 Development Mode (HTTP Only)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Запуск Nginx без HTTPS..." -ForegroundColor White
        Write-Host "Команда: docker compose up -d nginx" -ForegroundColor Gray
        Write-Host ""
        
        docker compose up -d nginx
        
        Write-Host ""
        Write-Host "✅ Nginx запущено в режимі розробки" -ForegroundColor Green
        Write-Host ""
        Write-Host "Доступ:" -ForegroundColor Yellow
        Write-Host "  - Frontend: http://localhost" -ForegroundColor Cyan
        Write-Host "  - API: http://localhost/api/" -ForegroundColor Cyan
        Write-Host "  - Health: http://localhost/health" -ForegroundColor Cyan
    }
    
    "self-signed" {
        Write-Host "🔒 Production Mode with Self-Signed Certificates" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  WARNING: Self-signed certificates призведуть до попереджень в браузері!" -ForegroundColor Yellow
        Write-Host "   Використовуйте цей режим тільки для тестування." -ForegroundColor Yellow
        Write-Host ""
        
        # Check if certificates exist
        if (Test-Path "ohmatdyt-crm/nginx/ssl/cert.pem") {
            Write-Host "ℹ️  SSL сертифікати вже існують" -ForegroundColor Cyan
            $regenerate = Read-Host "Згенерувати нові сертифікати? (y/N)"
            if ($regenerate -eq "y" -or $regenerate -eq "Y") {
                Write-Host ""
                Write-Host "Генерація self-signed сертифікатів..." -ForegroundColor White
                Push-Location ohmatdyt-crm/nginx
                bash generate-ssl-certs.sh
                Pop-Location
            }
        } else {
            Write-Host "Генерація self-signed сертифікатів..." -ForegroundColor White
            Write-Host ""
            
            # Create ssl directory
            New-Item -Path "ohmatdyt-crm/nginx/ssl" -ItemType Directory -Force | Out-Null
            
            # Generate certificates using OpenSSL
            Push-Location ohmatdyt-crm/nginx
            
            Write-Host "Домен: $Domain" -ForegroundColor Cyan
            
            # Generate certificate
            & openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
                -keyout "ssl/key.pem" `
                -out "ssl/cert.pem" `
                -subj "/C=UA/ST=Kyiv/L=Kyiv/O=Ohmatdyt CRM/CN=$Domain" `
                -addext "subjectAltName=DNS:$Domain,DNS:www.$Domain,DNS:localhost,IP:127.0.0.1"
            
            # Set permissions (on Windows, just create files)
            Write-Host ""
            Write-Host "✅ Сертифікати створено:" -ForegroundColor Green
            Write-Host "   - ssl/cert.pem" -ForegroundColor Cyan
            Write-Host "   - ssl/key.pem" -ForegroundColor Cyan
            
            Pop-Location
        }
        
        Write-Host ""
        Write-Host "Запуск Nginx з HTTPS..." -ForegroundColor White
        Write-Host "Команда: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx" -ForegroundColor Gray
        Write-Host ""
        
        Push-Location ohmatdyt-crm
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx
        Pop-Location
        
        Write-Host ""
        Write-Host "✅ Nginx запущено з HTTPS (self-signed)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Доступ:" -ForegroundColor Yellow
        Write-Host "  - Frontend: https://localhost (⚠️  Certificate Warning)" -ForegroundColor Cyan
        Write-Host "  - API: https://localhost/api/ (⚠️  Certificate Warning)" -ForegroundColor Cyan
        Write-Host "  - Health: https://localhost/health" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Перевірка:" -ForegroundColor Yellow
        Write-Host "  .\test_inf003.ps1" -ForegroundColor Cyan
    }
    
    "letsencrypt" {
        Write-Host "🔐 Production Mode with Let's Encrypt" -ForegroundColor Green
        Write-Host ""
        
        if ([string]::IsNullOrEmpty($Domain) -or $Domain -eq "localhost") {
            Write-Host "❌ Для Let's Encrypt потрібен публічний домен!" -ForegroundColor Red
            Write-Host ""
            Write-Host "Використання:" -ForegroundColor Yellow
            Write-Host "  .\setup-nginx-prod.ps1 -Mode letsencrypt -Domain crm.example.com -Email admin@example.com" -ForegroundColor Cyan
            Write-Host ""
            exit 1
        }
        
        if ([string]::IsNullOrEmpty($Email)) {
            Write-Host "❌ Для Let's Encrypt потрібен email!" -ForegroundColor Red
            Write-Host ""
            Write-Host "Використання:" -ForegroundColor Yellow
            Write-Host "  .\setup-nginx-prod.ps1 -Mode letsencrypt -Domain crm.example.com -Email admin@example.com" -ForegroundColor Cyan
            Write-Host ""
            exit 1
        }
        
        Write-Host "Домен: $Domain" -ForegroundColor Cyan
        Write-Host "Email: $Email" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠️  ВАЖЛИВО: Перевірте що:" -ForegroundColor Yellow
        Write-Host "   1. DNS A-record для $Domain вказує на цей сервер" -ForegroundColor Gray
        Write-Host "   2. Порти 80 та 443 відкриті в firewall" -ForegroundColor Gray
        Write-Host "   3. Сервер доступний з інтернету" -ForegroundColor Gray
        Write-Host ""
        
        $confirm = Read-Host "Продовжити? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "Скасовано." -ForegroundColor Yellow
            exit 0
        }
        
        Write-Host ""
        Write-Host "Запуск Let's Encrypt setup..." -ForegroundColor White
        Write-Host "ℹ️  Цей процес потребує доступу до Bash" -ForegroundColor Cyan
        Write-Host ""
        
        Push-Location ohmatdyt-crm/nginx
        bash setup-letsencrypt.sh
        Pop-Location
        
        Write-Host ""
        Write-Host "✅ Nginx запущено з Let's Encrypt HTTPS" -ForegroundColor Green
        Write-Host ""
        Write-Host "Доступ:" -ForegroundColor Yellow
        Write-Host "  - Frontend: https://$Domain" -ForegroundColor Cyan
        Write-Host "  - API: https://$Domain/api/" -ForegroundColor Cyan
        Write-Host "  - Health: https://$Domain/health" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Auto-renewal:" -ForegroundColor Yellow
        Write-Host "  Certbot перевірятиме сертифікати кожні 12 годин" -ForegroundColor Cyan
        Write-Host "  Запустіть certbot service:" -ForegroundColor Gray
        Write-Host "    docker compose --profile letsencrypt up -d certbot" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Show logs
Write-Host "Перегляд логів:" -ForegroundColor Yellow
Write-Host "  docker compose logs -f nginx" -ForegroundColor Cyan
Write-Host ""

Write-Host "Зупинка:" -ForegroundColor Yellow
Write-Host "  docker compose stop nginx" -ForegroundColor Cyan
Write-Host ""
