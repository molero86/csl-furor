# Guía de Despliegue - Furor App

## Configuración para Producción

### Variables de Entorno Requeridas

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# URL del backend (debe ser accesible desde internet)
VITE_API_URL=https://api.furor.molero.org

# URL de la base de datos
DATABASE_URL=mysql+pymysql://usuario:password@host:3306/nombre_bd

# CORS Origins (separados por comas)
CORS_ORIGINS=https://furor.molero.org,https://www.furor.molero.org
```

### Construir y Desplegar

1. **Build del Frontend:**
```bash
cd frontend
npm run build
```

2. **Construir los contenedores:**
```bash
docker-compose build
```

3. **Iniciar los servicios:**
```bash
docker-compose up -d
```

### Verificación

1. **Frontend:** http://localhost:4018
2. **Backend:** http://localhost:4017
3. **WebSocket:** ws://localhost:4017/ws/{game_code}

### Configuración de Nginx/Proxy Reverso

Si usas un proxy reverso (recomendado), configura:

```nginx
# Frontend
server {
    listen 443 ssl http2;
    server_name furor.molero.org;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:4018;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Backend + WebSocket
server {
    listen 443 ssl http2;
    server_name api.furor.molero.org;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:4017;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket support
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

### Solución de Problemas

#### Script de Diagnóstico Automático

Ejecuta el script de diagnóstico para identificar problemas:

**Linux/Mac:**
```bash
chmod +x diagnose.sh
./diagnose.sh
```

**Windows:**
```powershell
.\diagnose.ps1
```

#### WebSocket no conecta desde fuera de la red local

**Síntomas:** La app funciona en casa pero no desde otra red

**Soluciones:**

1. **Verifica que `VITE_API_URL` apunte a la URL pública:**
```bash
# Debe ser la URL pública, NO localhost
VITE_API_URL=https://api.furor.molero.org
```

2. **Verifica que el backend sea accesible desde internet:**
```bash
# Desde otro equipo o con tu móvil (datos móviles)
curl https://api.furor.molero.org
```

3. **Verifica que el proxy reverso tenga configurado WebSocket:**
```nginx
location /ws/ {
    proxy_pass http://localhost:4017;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

4. **Revisa los logs del backend:**
```bash
docker-compose logs -f backend
```

#### CORS errors

**Síntomas:** Error "CORS policy blocked" en la consola del navegador

**Soluciones:**

1. Añade todos tus dominios a `CORS_ORIGINS` en `.env`:
```env
CORS_ORIGINS=https://furor.molero.org,https://www.furor.molero.org,http://localhost:4018
```

2. Reconstruye y reinicia:
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

3. Verifica que el backend tenga la variable:
```bash
docker exec furor_backend printenv | grep CORS
```

#### La variable de entorno no se aplica

**Síntomas:** El frontend sigue usando localhost o URL incorrecta

**Soluciones:**

1. Verifica que el archivo `.env` exista en la raíz del proyecto
2. Reconstruye completamente:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

3. Verifica que `env.js` se genere correctamente:
```bash
docker exec furor_frontend cat /usr/share/nginx/html/env.js
```

Debería mostrar:
```javascript
window.__env = {
  VITE_API_URL: "https://api.furor.molero.org"
};
```

4. Verifica que el `index.html` tenga el script inyectado:
```bash
docker exec furor_frontend head -20 /usr/share/nginx/html/index.html | grep env.js
```

Debería mostrar: `<script src="/env.js"></script>`

#### Error de conexión a la base de datos

**Síntomas:** Error 500 al crear o unirse a partida

**Soluciones:**

1. Verifica que la base de datos sea accesible desde el contenedor:
```bash
# Desde dentro del contenedor backend
docker exec -it furor_backend bash
apt-get update && apt-get install -y mysql-client
mysql -h HOST -u USER -p DATABASE
```

2. Si la DB está en el mismo servidor, usa `host.docker.internal`:
```env
DATABASE_URL=mysql+pymysql://user:pass@host.docker.internal:3306/db
```

3. Si la DB está en otro servidor, verifica firewall y permisos:
```sql
-- En MySQL, asegúrate de que el usuario tenga permisos remotos
GRANT ALL PRIVILEGES ON database.* TO 'user'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

4. Verifica logs de error:
```bash
docker logs furor_backend | grep -i error
```

#### Puerto ya en uso

**Síntomas:** Error al iniciar: "port is already allocated"

**Soluciones:**

1. Verifica qué proceso usa el puerto:
```bash
# Linux/Mac
lsof -i :4017
lsof -i :4018

# Windows
netstat -ano | findstr :4017
netstat -ano | findstr :4018
```

2. Detén el proceso o cambia el puerto en `docker-compose.yml`:
```yaml
ports:
  - "5017:8000"  # Cambiar 4017 por otro puerto
```

### Actualización del Código

Después de hacer cambios en el código:

```bash
# 1. Rebuild frontend
cd frontend
npm run build

# 2. Rebuild containers
cd ..
docker-compose build

# 3. Restart services
docker-compose up -d

# 4. Verificar logs
docker-compose logs -f
```
