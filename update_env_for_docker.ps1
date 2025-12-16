# Update .env file for Docker (port 8080)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Updating .env for Docker Deployment" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$envFile = ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Creating .env from env.docker.template..." -ForegroundColor Yellow
    
    if (Test-Path "env.docker.template") {
        Copy-Item "env.docker.template" $envFile
        Write-Host "✅ Created .env file from template" -ForegroundColor Green
        Write-Host "`nPlease edit .env and add your actual API keys!" -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "ERROR: env.docker.template not found!" -ForegroundColor Red
        exit 1
    }
}

# Backup original
$backup = ".env.backup." + (Get-Date -Format "yyyyMMdd-HHmmss")
Copy-Item $envFile $backup
Write-Host "✅ Backed up .env to: $backup" -ForegroundColor Green

# Read file
$content = Get-Content $envFile -Raw

# Update redirect URI from port 5000 to 8080
$updated = $content -replace 'GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback', 'GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback'

# Write back
Set-Content $envFile $updated

Write-Host "`n✅ Updated GOOGLE_REDIRECT_URI to use port 8080" -ForegroundColor Green

# Display changes
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Current Google API Configuration:" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Get-Content $envFile | Select-String "GOOGLE_CLIENT_ID|GOOGLE_CLIENT_SECRET|GOOGLE_REDIRECT_URI|GEMINI_API_KEY|GA_MEASUREMENT_ID|GOOGLE_CLOUD_PROJECT" | ForEach-Object {
    $line = $_.Line.Trim()
    if ($line -match "=(.+)") {
        $value = $matches[1]
        if ($value -and $value -ne "your-" -and -not $value.StartsWith("your-")) {
            Write-Host "✅ $line" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $line" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "1. Update Google Cloud Console redirect URI to port 8080" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/apis/credentials`n" -ForegroundColor Gray
Write-Host "2. Rebuild Docker container:" -ForegroundColor White
Write-Host "   docker-compose down" -ForegroundColor Gray
Write-Host "   docker-compose up --build -d`n" -ForegroundColor Gray
Write-Host "3. Test at: http://localhost:8080" -ForegroundColor White
Write-Host "`nSee DOCKER_ALL_GOOGLE_APIS_SETUP.md for complete guide" -ForegroundColor Yellow
Write-Host "="*60 -ForegroundColor Cyan

