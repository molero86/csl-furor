# 🚀 Guía de Instalación y Configuración - Furor App

## Requisitos Previos
- ✅ Docker y Docker Compose instalados
- ✅ Base de datos MySQL accesible
- ✅ (Producción) Dominio configurado con certificado SSL

## 📦 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/molero86/csl-furor.git
cd csl-furor-app
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# ⚠️ IMPORTANTE: Usa tu URL pública, NO localhost
VITE_API_URL=https://api.furor.molero.org

# Conexión a MySQL (ajusta con tus credenciales)
DATABASE_URL=mysql+pymysql://usuario:contraseña@host:3306/furor

# Dominios permitidos (incluye TODOS desde donde accederás)
CORS_ORIGINS=https://furor.molero.org,https://www.furor.molero.org
```

### 3. Construir e Iniciar

```bash
# Construir las imágenes
docker-compose build

# Iniciar los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f
```

### 4. Verificar Instalación

**Opción A - Script automático:**
```bash
# Linux/Mac
chmod +x diagnose.sh
./diagnose.sh

# Windows PowerShell
.\diagnose.ps1
```

**Opción B - Manual:**
```bash
# ✓ Verificar que los contenedores estén corriendo
docker ps | grep furor

# ✓ Verificar env.js del frontend
docker exec furor_frontend cat /usr/share/nginx/html/env.js
# Debe mostrar: window.__env = { VITE_API_URL: "https://..." };

# ✓ Verificar CORS en backend
docker exec furor_backend printenv | grep CORS

# ✓ Acceder a la app
# Frontend: http://localhost:4018
# Backend: http://localhost:4017
```

## 🔥 Problemas Comunes y Soluciones

### ❌ "No funciona desde fuera de mi red"

**Causa:** Variables de entorno no configuradas o backend no accesible públicamente.

**Solución:**

1. Verifica que `VITE_API_URL` tenga tu URL pública (no localhost):
```bash
docker exec furor_frontend cat /usr/share/nginx/html/env.js
```

2. Si muestra localhost o está vacío, reconstruye:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

3. Verifica que tu backend sea accesible desde internet:
```bash
# Desde otro equipo o móvil con datos
curl https://api.furor.molero.org
```

### ❌ Error CORS en el navegador

**Síntoma:** "Access to XMLHttpRequest has been blocked by CORS policy"

**Solución:**

1. Añade tu dominio a `CORS_ORIGINS` en `.env`:
```env
CORS_ORIGINS=https://furor.molero.org,https://www.furor.molero.org,http://localhost:4018
```

2. Reconstruye el backend:
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

### ❌ WebSocket no conecta

**Síntoma:** Error "WebSocket connection failed"

**Causas y soluciones:**

1. **Proxy reverso sin soporte WebSocket:**
```nginx
# Añade esto a tu configuración de Nginx
location /ws/ {
    proxy_pass http://localhost:4017;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

2. **URL incorrecta:** Verifica que use `wss://` (no `ws://`) con HTTPS

3. **Firewall bloqueando:** Verifica que el puerto 4017 esté abierto

### ❌ Error de conexión a base de datos

**Síntoma:** Error 500 al crear/unirse a partida, logs muestran "Can't connect to MySQL"

**Soluciones:**

1. **Si la DB está en el mismo servidor (Docker):**
```env
DATABASE_URL=mysql+pymysql://user:pass@host.docker.internal:3306/furor
```

2. **Si la DB está en otro servidor:**
```bash
# Verifica conectividad desde el contenedor
docker exec -it furor_backend bash
apt-get update && apt-get install -y mysql-client
mysql -h tu_host -u tu_usuario -p
```

3. **Permisos en MySQL:**
```sql
-- Permite conexiones remotas
GRANT ALL PRIVILEGES ON furor.* TO 'usuario'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

### ❌ Puerto ya en uso

**Síntoma:** "port is already allocated"

**Solución:**

1. Encuentra qué usa el puerto:
```bash
# Linux/Mac
lsof -i :4017
lsof -i :4018

# Windows
netstat -ano | findstr :4017
```

2. Detén el proceso o cambia el puerto en `docker-compose.yml`:
```yaml
ports:
  - "5017:8000"  # Cambiar aquí
```

## 🔄 Actualizar la Aplicación

Después de hacer cambios en el código:

```bash
# 1. Detener servicios
docker-compose down

# 2. Reconstruir (sin caché para cambios importantes)
docker-compose build --no-cache

# 3. Iniciar
docker-compose up -d

# 4. Verificar logs
docker-compose logs -f
```

## 📊 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver solo logs del backend
docker-compose logs -f backend

# Ver solo logs del frontend
docker-compose logs -f frontend

# Reiniciar un servicio específico
docker-compose restart backend

# Entrar en un contenedor
docker exec -it furor_backend bash
docker exec -it furor_frontend sh

# Ver todos los contenedores
docker ps -a

# Eliminar todo y empezar de cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 Configuración de Producción con Nginx

Si usas Nginx como proxy reverso:

```nginx
# Frontend
server {
    listen 443 ssl http2;
    server_name furor.molero.org;
    
    ssl_certificate /ruta/cert.pem;
    ssl_certificate_key /ruta/key.pem;
    
    location / {
        proxy_pass http://localhost:4018;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Backend + WebSocket
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:4017;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
```

## 📞 Soporte

Si sigues teniendo problemas:

1. Ejecuta el script de diagnóstico: `./diagnose.sh` o `.\diagnose.ps1`
2. Revisa los logs: `docker-compose logs -f`
3. Verifica la configuración: revisa tu archivo `.env`
4. Consulta [DEPLOYMENT.md](DEPLOYMENT.md) para más detalles

## ✅ Checklist de Producción

Antes de desplegar en producción, verifica:

- [ ] Archivo `.env` configurado con URLs públicas
- [ ] `VITE_API_URL` usa HTTPS (no HTTP)
- [ ] Todos los dominios incluidos en `CORS_ORIGINS`
- [ ] Base de datos accesible desde el servidor
- [ ] Certificados SSL configurados
- [ ] Puertos 4017 y 4018 abiertos en firewall (o proxy reverso configurado)
- [ ] `env.js` generado correctamente en el contenedor frontend
- [ ] WebSocket funcionando (verificar en navegador)
- [ ] Logs sin errores: `docker-compose logs`
