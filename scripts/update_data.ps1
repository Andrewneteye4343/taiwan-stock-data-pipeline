Write-Host "========================================"
Write-Host " Taiwan Stock Data Pipeline"
Write-Host " Updating latest market data..."
Write-Host "========================================"
Write-Host ""

docker compose run --rm pipeline python -m src.cli update

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Data update completed successfully." -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "Data update failed." -ForegroundColor Red
    exit $LASTEXITCODE
}