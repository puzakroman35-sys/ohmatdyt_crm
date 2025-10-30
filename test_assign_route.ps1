# Test script to check if /assign route exists
$response = Invoke-WebRequest -Uri "http://localhost:8000/openapi.json" -Method GET
$json = $response.Content | ConvertFrom-Json

Write-Host "Checking for 'assign' routes..." -ForegroundColor Yellow
Write-Host ""

$assignRoutes = $json.paths.PSObject.Properties | Where-Object { $_.Name -like "*assign*" }

if ($assignRoutes) {
    Write-Host "Found assign routes:" -ForegroundColor Green
    foreach ($route in $assignRoutes) {
        Write-Host "  $($route.Name)" -ForegroundColor Cyan
        $methods = $route.Value.PSObject.Properties.Name
        Write-Host "    Methods: $($methods -join ', ')" -ForegroundColor Gray
    }
} else {
    Write-Host "No assign routes found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "All available routes:" -ForegroundColor Yellow
    foreach ($path in $json.paths.PSObject.Properties) {
        if ($path.Name -like "*cases*") {
            Write-Host "  $($path.Name)" -ForegroundColor Cyan
        }
    }
}
