#!/bin/bash

echo "========================================"
echo "CONFIGURACIÓN RÁPIDA - IP PÚBLICA"
echo "========================================"
echo ""

# Obtener IP pública
echo "1. Detectando tu IP pública..."
IP_PUBLICA=$(curl -s ifconfig.me)
echo "   Tu IP pública es: $IP_PUBLICA"

echo ""
echo "2. Generando archivo .env..."
cat > .env << EOF
VITE_API_URL=http://${IP_PUBLICA}:4017
DATABASE_URL=mysql+pymysql://root:root@host.docker.internal:3306/furor
CORS_ORIGINS=http://${IP_PUBLICA}:4018,http://localhost:4018,http://localhost:5173
EOF

echo "   ✓ Archivo .env creado"
cat .env

echo ""
echo "3. IMPORTANTE: Abre estos puertos en tu router:"
echo "   - Puerto 4017 (Backend)"
echo "   - Puerto 4018 (Frontend)"
echo "   Redirige ambos a la IP de tu ordenador en la red local"

echo ""
echo "4. Reconstruyendo contenedores..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo ""
echo "5. Verificando..."
sleep 5
docker exec furor_frontend cat /usr/share/nginx/html/env.js

echo ""
echo "========================================"
echo "¡LISTO!"
echo "========================================"
echo ""
echo "Comparte esta URL con todos:"
echo "   👉 http://${IP_PUBLICA}:4018"
echo ""
echo "⚠️  RECUERDA:"
echo "   1. Abrir puertos 4017 y 4018 en el router"
echo "   2. Mantener tu ordenador encendido"
echo "   3. No cerrar Docker"
