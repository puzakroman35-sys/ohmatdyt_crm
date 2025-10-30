# Check all /api/cases routes
$response = Invoke-WebRequest -Uri "http://localhost:8000/openapi.json" -Method GET
$json = $response.Content | ConvertFrom-Json

Write-Host "All /api/cases routes:" -ForegroundColor Yellow
Write-Host ""

foreach ($path in $json.paths.PSObject.Properties) {
    if ($path.Name -like "/api/cases*") {
        Write-Host "$($path.Name)" -ForegroundColor Cyan
        $methods = $path.Value.PSObject.Properties.Name
        foreach ($method in $methods) {
            Write-Host "  $($method.ToUpper())" -ForegroundColor Gray
        }
        Write-Host ""
    }
}
