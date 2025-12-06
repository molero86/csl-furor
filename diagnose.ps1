# Script de diagnóstico para Furor App en Windows
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO FUROR APP" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Verificando contenedores en ejecución..." -ForegroundColor Yellow
docker ps --filter "name=furor"

Write-Host ""
Write-Host "2. Verificando variables de entorno en frontend..." -ForegroundColor Yellow
try {
    docker exec furor_frontend cat /usr/share/nginx/html/env.js
} catch {
    Write-Host "❌ No se pudo leer env.js" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Verificando que index.html tiene el script env.js..." -ForegroundColor Yellow
try {
    docker exec furor_frontend grep "env.js" /usr/share/nginx/html/index.html
} catch {
    Write-Host "❌ env.js no está en index.html" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Verificando CORS en backend..." -ForegroundColor Yellow
docker exec furor_backend printenv | Select-String "CORS"

Write-Host ""
Write-Host "5. Verificando DATABASE_URL en backend..." -ForegroundColor Yellow
$dbUrl = docker exec furor_backend printenv | Select-String "DATABASE_URL"
if ($dbUrl) {
    Write-Host "✓ DATABASE_URL está configurada (no mostrando credenciales)" -ForegroundColor Green
}

Write-Host ""
Write-Host "6. Logs recientes del backend (últimas 30 líneas)..." -ForegroundColor Yellow
docker logs furor_backend --tail 30

Write-Host ""
Write-Host "7. Logs recientes del frontend (últimas 10 líneas)..." -ForegroundColor Yellow
docker logs furor_frontend --tail 10

Write-Host ""
Write-Host "8. Verificando puertos expuestos..." -ForegroundColor Yellow
Write-Host "Frontend:"
docker ps --filter name=furor_frontend --format "{{.Ports}}"
Write-Host "Backend:"
docker ps --filter name=furor_backend --format "{{.Ports}}"

Write-Host ""
Write-Host "9. Test de conectividad desde localhost..." -ForegroundColor Yellow
Write-Host "Frontend (http://localhost:4018):"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4018" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Responde: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ No responde o error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Backend (http://localhost:4017):"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4017" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Responde: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ No responde o error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "10. Verificando archivo .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ Archivo .env encontrado" -ForegroundColor Green
    Write-Host "Contenido (sin credenciales):" -ForegroundColor Gray
    Get-Content .env | ForEach-Object {
        if ($_ -match "PASSWORD|SECRET|KEY") {
            Write-Host "$($_ -replace '=.*', '=***')" -ForegroundColor Gray
        } elseif ($_ -match "VITE_API_URL|CORS") {
            Write-Host $_ -ForegroundColor Cyan
        } else {
            Write-Host $_ -ForegroundColor Gray
        }
    }
} else {
    Write-Host "❌ Archivo .env NO encontrado" -ForegroundColor Red
    Write-Host "IMPORTANTE: Debes crear un archivo .env con:" -ForegroundColor Yellow
    Write-Host "VITE_API_URL=https://api.furor.molero.org" -ForegroundColor Yellow
    Write-Host "DATABASE_URL=mysql+pymysql://user:pass@host:3306/db" -ForegroundColor Yellow
    Write-Host "CORS_ORIGINS=https://furor.molero.org" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO COMPLETADO" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "RECOMENDACIONES:" -ForegroundColor Yellow
Write-Host "1. Si env.js está vacío, reconstruir: docker-compose build --no-cache" -ForegroundColor White
Write-Host "2. Si CORS falla, añadir tu dominio en .env y reiniciar" -ForegroundColor White
Write-Host "3. Si la base de datos falla, verificar DATABASE_URL y conectividad" -ForegroundColor White
Write-Host "4. Para ver errores en tiempo real: docker-compose logs -f" -ForegroundColor White
