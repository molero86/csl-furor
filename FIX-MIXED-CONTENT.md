# 🚨 SOLUCIÓN AL ERROR "Mixed Content" y "Failed to fetch"

## ❌ Problema Detectado

```
Mixed Content: The page at 'https://furor.molero.org/' was loaded over HTTPS, 
but requested an insecure resource 'http://192.168.68.10:4017/games'
```

## 🔍 Diagnóstico

Tu archivo `env.js` en el contenedor tiene:
```javascript
window.__env = {
  VITE_API_URL: "http://furorapi.molero.org"  // ❌ INCORRECTO
};
```

**Problemas:**
1. Usa HTTP en vez de HTTPS (Mixed Content Error)
2. Usa IP local (192.168.68.10) que no es accesible desde fuera

## ✅ SOLUCIÓN

Necesitas que `VITE_API_URL` apunte a tu backend público con HTTPS.

### Opción A: Si tienes dominio para el backend

**En tu servidor, edita el archivo `.env`:**

```bash
nano .env
```

**Cámbialo a:**
```env
VITE_API_URL=https://api.furor.molero.org
DATABASE_URL=mysql+pymysql://TU_USUARIO:TU_PASSWORD@TU_HOST:3306/TU_BD
CORS_ORIGINS=https://furor.molero.org,https://www.furor.molero.org
```

**Luego reconstruye:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Y configura nginx para el backend (api.furor.molero.org):**
```nginx
server {
    listen 443 ssl http2;
    server_name api.furor.molero.org;
    
    ssl_certificate /ruta/cert.pem;
    ssl_certificate_key /ruta/key.pem;
    
    # API REST
    location / {
        proxy_pass http://localhost:4017;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:4017;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

---

### Opción B: Si NO tienes dominio para backend (Solución rápida con mismo dominio)

**En nginx, añade el backend bajo /api:**

```nginx
server {
    listen 443 ssl http2;
    server_name furor.molero.org;
    
    ssl_certificate /ruta/cert.pem;
    ssl_certificate_key /ruta/key.pem;
    
    # Frontend (Vue app)
    location / {
        proxy_pass http://localhost:4018;
        proxy_set_header Host $host;
    }
    
    # Backend bajo /api
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:4017;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket bajo /api/ws
    location /api/ws/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:4017;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

**Luego en `.env`:**
```env
VITE_API_URL=https://furor.molero.org/api
DATABASE_URL=mysql+pymysql://TU_USUARIO:TU_PASSWORD@TU_HOST:3306/TU_BD
CORS_ORIGINS=https://furor.molero.org
```

**Y reconstruye:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

### Opción C: Con ngrok (Para testing rápido)

Si necesitas una solución temporal AHORA:

```bash
# Terminal 1 - ngrok para backend
ngrok http 4017

# Copia la URL HTTPS que te da, ej: https://abc123.ngrok.io

# Terminal 2 - Actualiza .env
echo "VITE_API_URL=https://abc123.ngrok.io" > .env
echo "DATABASE_URL=..." >> .env
echo "CORS_ORIGINS=https://furor.molero.org,https://abc123.ngrok.io" >> .env

# Reconstruye frontend
docker-compose build --no-cache frontend
docker-compose restart
```

---

## 🔍 Verificar la Solución

Después de aplicar los cambios:

```bash
# 1. Verificar que env.js tiene la URL correcta
docker exec furor_frontend cat /usr/share/nginx/html/env.js

# Debe mostrar:
# window.__env = {
#   VITE_API_URL: "https://api.furor.molero.org"  // o la URL HTTPS correcta
# };

# 2. Verificar que el backend es accesible por HTTPS
curl https://api.furor.molero.org/games
# o
curl https://furor.molero.org/api/games

# 3. Ver logs
docker-compose logs -f
```

---

## 📋 Checklist

Antes de que funcione necesitas:

- [ ] `.env` tiene `VITE_API_URL` con HTTPS (no HTTP)
- [ ] `.env` tiene una URL pública (no 192.168.x.x ni localhost)
- [ ] Nginx configurado con SSL para el backend
- [ ] `CORS_ORIGINS` incluye tu dominio frontend
- [ ] Contenedores reconstruidos después de cambiar `.env`
- [ ] `env.js` generado correctamente con la URL HTTPS

---

## 🎯 Recomendación

**Para tu exposición HOY, usa la Opción B** (mismo dominio, ruta /api):
- No necesitas crear otro dominio
- Usa el mismo certificado SSL
- Configuración más simple
- 10 minutos para implementar

Pasos exactos:

1. Edita tu nginx para añadir las rutas `/api` y `/api/ws`
2. Recarga nginx: `sudo systemctl reload nginx`
3. Edita `.env`: `VITE_API_URL=https://furor.molero.org/api`
4. Reconstruye: `docker-compose build --no-cache && docker-compose up -d`
5. Verifica: `docker exec furor_frontend cat /usr/share/nginx/html/env.js`

¡En 10 minutos estará funcionando! 🚀
