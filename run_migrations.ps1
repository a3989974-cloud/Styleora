# Run Django migrations against the production database
# Usage: .\run_migrations.ps1

$dbUrl = Read-Host -Prompt "Paste your DATABASE_URL from Vercel Dashboard"
$env:DATABASE_URL = $dbUrl

Write-Host "Running migrations..."
python manage.py migrate --noinput

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Migration failed. Check the error above." -ForegroundColor Red
}
