Write-Host "=== Seeding USER SERVICE ===" -ForegroundColor Cyan
docker compose exec user-service python -m app.seed.run
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== Seeding CATALOG SERVICE ===" -ForegroundColor Cyan
docker compose exec catalog-service python -m app.seed.run
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== Seeding CIRCULATION SERVICE ===" -ForegroundColor Cyan
docker compose exec circulation-service python -m app.seed.run
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Demo data seeded successfully." -ForegroundColor Green
