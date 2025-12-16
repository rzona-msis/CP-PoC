# Fix .env file for Docker - Update port from 5000 to 8080

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Fixing .env for Docker Deployment" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$envFile = ".env"

if (Test-Path $envFile) {
    Write-Host "✅ Found .env file" -ForegroundColor Green
    
    # Read the file
    $content = Get-Content $envFile -Raw
    
    # Check if update is needed
    if ($content -match "localhost:5000/calendar/callback") {
        Write-Host "🔧 Updating GOOGLE_REDIRECT_URI port 5000 → 8080..." -ForegroundColor Yellow
        
        # Make the change
        $newContent = $content -replace "localhost:5000/calendar/callback", "localhost:8080/calendar/callback"
        
        # Backup original
        Copy-Item $envFile "$envFile.backup"
        Write-Host "📁 Created backup: .env.backup" -ForegroundColor Gray
        
        # Write new content
        Set-Content $envFile $newContent -NoNewline
        
        Write-Host "✅ Updated .env file successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Changed:" -ForegroundColor White
        Write-Host "  GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback" -ForegroundColor Red
        Write-Host "  ↓" -ForegroundColor Yellow
        Write-Host "  GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback" -ForegroundColor Green
    }
    elseif ($content -match "localhost:8080/calendar/callback") {
        Write-Host "✅ .env already configured for Docker (port 8080)!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Could not find GOOGLE_REDIRECT_URI in .env" -ForegroundColor Yellow
        Write-Host "   You may need to add it manually." -ForegroundColor Yellow
    }
}
else {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "   Please create .env file first" -ForegroundColor Red
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "1. Update Google Cloud Console redirect URI" -ForegroundColor White
Write-Host "   Add: http://localhost:8080/calendar/callback" -ForegroundColor White
Write-Host ""
Write-Host "2. Restart Docker:" -ForegroundColor White
Write-Host "   docker-compose down" -ForegroundColor Gray
Write-Host "   docker-compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test at: http://localhost:8080" -ForegroundColor White
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

