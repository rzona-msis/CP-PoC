# Update Gemini API Key in .env file
param(
    [Parameter(Mandatory=$true)]
    [string]$NewApiKey
)

$envFile = ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    exit 1
}

# Backup original
$backup = ".env.backup." + (Get-Date -Format "yyyyMMdd-HHmmss")
Copy-Item $envFile $backup
Write-Host "✅ Backed up .env to: $backup" -ForegroundColor Green

# Read and update
$content = Get-Content $envFile -Raw

# Replace the API key
if ($content -match "GEMINI_API_KEY=.*") {
    $content = $content -replace "GEMINI_API_KEY=.*", "GEMINI_API_KEY=$NewApiKey"
    Set-Content $envFile $content
    Write-Host "✅ Updated GEMINI_API_KEY in .env" -ForegroundColor Green
    Write-Host "`nNew key: $($NewApiKey.Substring(0, [Math]::Min(20, $NewApiKey.Length)))..." -ForegroundColor Yellow
} else {
    # Add if doesn't exist
    Add-Content $envFile "`nGEMINI_API_KEY=$NewApiKey"
    Write-Host "✅ Added GEMINI_API_KEY to .env" -ForegroundColor Green
}

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Next: Rebuild Docker to use the new key:" -ForegroundColor Cyan
Write-Host "  docker-compose down" -ForegroundColor White
Write-Host "  docker-compose up --build -d" -ForegroundColor White
Write-Host "="*60 -ForegroundColor Cyan

