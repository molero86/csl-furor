# CONFIGURACIÓN RÁPIDA - IP PÚBLICA (Windows)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURACIÓN RÁPIDA - IP PÚBLICA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Obtener IP pública
Write-Host "1. Detectando tu IP pública..." -ForegroundColor Yellow
try {
    $IP_PUBLICA = (Invoke-WebRequest -Uri "https://ifconfig.me" -UseBasicParsing -TimeoutSec 10).Content.Trim()
    Write-Host "   Tu IP pública es: $IP_PUBLICA" -ForegroundColor Green
} catch {
    Write-Host "   ❌ No se pudo obtener la IP pública automáticamente" -ForegroundColor Red
    $IP_PUBLICA = Read-Host "   Por favor ingresa tu IP pública manualmente"
}

Write-Host ""
Write-Host "2. Generando archivo .env..." -ForegroundColor Yellow

$envContent = @"
VITE_API_URL=http://${IP_PUBLICA}:4017
DATABASE_URL=mysql+pymysql://root:root@host.docker.internal:3306/furor
CORS_ORIGINS=http://${IP_PUBLICA}:4018,http://localhost:4018,http://localhost:5173
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline
Write-Host "   ✓ Archivo .env creado" -ForegroundColor Green
Write-Host ""
Get-Content .env | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }

Write-Host ""
Write-Host "3. IMPORTANTE: Configuración del Router" -ForegroundColor Yellow
Write-Host "   Debes abrir y redirigir estos puertos en tu router:" -ForegroundColor White
Write-Host "   📍 Puerto 4017 (Backend) → IP local de este PC" -ForegroundColor Cyan
Write-Host "   📍 Puerto 4018 (Frontend) → IP local de este PC" -ForegroundColor Cyan
Write-Host ""
Write-Host "   ¿Cómo hacerlo?" -ForegroundColor White
Write-Host "   1. Entra a tu router (normalmente 192.168.1.1)" -ForegroundColor Gray
Write-Host "   2. Busca 'Port Forwarding' o 'NAT'" -ForegroundColor Gray
Write-Host "   3. Añade reglas para puertos 4017 y 4018" -ForegroundColor Gray
Write-Host "   4. Apunta a la IP local de este PC" -ForegroundColor Gray

Write-Host ""
$continuar = Read-Host "¿Has configurado el router? (s/n)"
if ($continuar -ne 's') {
    Write-Host ""
    Write-Host "⚠️  Configura el router primero y vuelve a ejecutar este script" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "4. Reconstruyendo contenedores..." -ForegroundColor Yellow
docker-compose down
docker-compose build --no-cache
docker-compose up -d

Write-Host ""
Write-Host "5. Esperando a que los servicios inicien..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "6. Verificando configuración..." -ForegroundColor Yellow
try {
    $envJs = docker exec furor_frontend cat /usr/share/nginx/html/env.js
    Write-Host "   ✓ env.js generado correctamente:" -ForegroundColor Green
    Write-Host "   $envJs" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Error al verificar env.js" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "¡LISTO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 Comparte esta URL con todos los participantes:" -ForegroundColor Yellow
Write-Host "   👉 http://${IP_PUBLICA}:4018" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host "⚠️  IMPORTANTE - Mantén esto activo:" -ForegroundColor Yellow
Write-Host "   ✓ Tu ordenador encendido" -ForegroundColor White
Write-Host "   ✓ Docker corriendo" -ForegroundColor White
Write-Host "   ✓ Puertos abiertos en el router" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Para ver logs en tiempo real:" -ForegroundColor Gray
Write-Host "   docker-compose logs -f" -ForegroundColor Gray
