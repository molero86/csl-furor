#!/bin/bash

echo "======================================"
echo "DIAGNÓSTICO FUROR APP"
echo "======================================"
echo ""

echo "1. Verificando contenedores en ejecución..."
docker ps | grep furor

echo ""
echo "2. Verificando variables de entorno en frontend..."
docker exec furor_frontend cat /usr/share/nginx/html/env.js 2>/dev/null || echo "❌ No se pudo leer env.js"

echo ""
echo "3. Verificando que index.html tiene el script env.js..."
docker exec furor_frontend grep "env.js" /usr/share/nginx/html/index.html 2>/dev/null || echo "❌ env.js no está en index.html"

echo ""
echo "4. Verificando conexión al backend desde dentro del contenedor frontend..."
docker exec furor_frontend wget -qO- http://furor_backend:8000/ 2>/dev/null || echo "❌ No se puede conectar al backend"

echo ""
echo "5. Verificando CORS en backend..."
docker exec furor_backend printenv | grep CORS

echo ""
echo "6. Verificando DATABASE_URL en backend..."
docker exec furor_backend printenv | grep DATABASE_URL | sed 's/:[^@]*@/:***@/'

echo ""
echo "7. Logs recientes del backend (últimas 20 líneas)..."
docker logs furor_backend --tail 20

echo ""
echo "8. Logs recientes del frontend (últimas 10 líneas)..."
docker logs furor_frontend --tail 10

echo ""
echo "9. Verificando puertos expuestos..."
echo "Frontend debería estar en 4018:"
netstat -tuln 2>/dev/null | grep 4018 || ss -tuln 2>/dev/null | grep 4018 || echo "Usando Docker ps..."
docker ps --filter name=furor_frontend --format "{{.Ports}}"

echo ""
echo "Backend debería estar en 4017:"
netstat -tuln 2>/dev/null | grep 4017 || ss -tuln 2>/dev/null | grep 4017 || echo "Usando Docker ps..."
docker ps --filter name=furor_backend --format "{{.Ports}}"

echo ""
echo "10. Test de conectividad externa..."
echo "Probando frontend desde localhost:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4018/ || echo "❌ No responde"

echo ""
echo "Probando backend desde localhost:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4017/ || echo "❌ No responde"

echo ""
echo "======================================"
echo "DIAGNÓSTICO COMPLETADO"
echo "======================================"
