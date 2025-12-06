# SOLUCIÓN CON NGROK - Sin configurar router
# ngrok crea un túnel público a tu localhost

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURACIÓN CON NGROK (Sin Router)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 PASOS PREVIOS:" -ForegroundColor Yellow
Write-Host "1. Descarga ngrok: https://ngrok.com/download" -ForegroundColor White
Write-Host "2. Regístrate gratis en ngrok.com" -ForegroundColor White
Write-Host "3. Copia tu authtoken de: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
Write-Host ""

$ngrokInstalled = $false
try {
    $null = Get-Command ngrok -ErrorAction Stop
    $ngrokInstalled = $true
    Write-Host "✓ ngrok está instalado" -ForegroundColor Green
} catch {
    Write-Host "❌ ngrok no está instalado" -ForegroundColor Red
    Write-Host "   Descárgalo de: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "   Y agrega ngrok.exe a tu PATH o cópialo a esta carpeta" -ForegroundColor Yellow
    Write-Host ""
    $continuar = Read-Host "¿Ya lo instalaste? (s/n)"
    if ($continuar -ne 's') {
        exit
    }
}

Write-Host ""
$authtoken = Read-Host "Ingresa tu authtoken de ngrok"
if ($authtoken) {
    Write-Host "Configurando authtoken..." -ForegroundColor Yellow
    & ngrok config add-authtoken $authtoken
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASO 1: Iniciar servicios localmente" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Crear .env temporal para localhost
Write-Host "Creando configuración local temporal..." -ForegroundColor Yellow
$envContent = @"
VITE_API_URL=http://localhost:4017
DATABASE_URL=mysql+pymysql://root:root@host.docker.internal:3306/furor
CORS_ORIGINS=http://localhost:4018,http://localhost:5173
"@
$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host "Iniciando Docker..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "Esperando a que los servicios inicien..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASO 2: Crear túneles ngrok" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  ABRE DOS VENTANAS NUEVAS DE POWERSHELL y ejecuta:" -ForegroundColor Yellow
Write-Host ""
Write-Host "📍 VENTANA 1 - Backend:" -ForegroundColor Cyan
Write-Host "   ngrok http 4017" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""
Write-Host "📍 VENTANA 2 - Frontend:" -ForegroundColor Cyan
Write-Host "   ngrok http 4018" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""
Write-Host "Presiona ENTER cuando hayas iniciado ambos túneles..." -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "Ahora copia las URLs que aparecen en ngrok:" -ForegroundColor Yellow
Write-Host ""
$backendUrl = Read-Host "URL del backend (ej: https://abc123.ngrok.io)"
$frontendUrl = Read-Host "URL del frontend (ej: https://def456.ngrok.io)"

Write-Host ""
Write-Host "Actualizando configuración..." -ForegroundColor Yellow

$envContent = @"
VITE_API_URL=$backendUrl
DATABASE_URL=mysql+pymysql://root:root@host.docker.internal:3306/furor
CORS_ORIGINS=$frontendUrl,http://localhost:4018
"@
$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host "Reconstruyendo frontend..." -ForegroundColor Yellow
docker-compose build --no-cache frontend
docker-compose up -d

Write-Host ""
Write-Host "Esperando reconstrucción..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "¡LISTO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📱 URL PÚBLICA PARA COMPARTIR:" -ForegroundColor Yellow
Write-Host "   👉 $frontendUrl" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host "⚠️  IMPORTANTE - Mantén esto corriendo:" -ForegroundColor Yellow
Write-Host "   ✓ Docker (docker-compose)" -ForegroundColor White
Write-Host "   ✓ Ventana de ngrok para backend (puerto 4017)" -ForegroundColor White
Write-Host "   ✓ Ventana de ngrok para frontend (puerto 4018)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Los túneles de ngrok se mantienen activos mientras las ventanas estén abiertas" -ForegroundColor Gray
