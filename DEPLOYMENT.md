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

#### WebSocket no conecta desde fuera de la red local

1. Verifica que `VITE_API_URL` en `.env` apunte a la URL pública (https://)
2. Asegúrate de que el backend sea accesible desde internet
3. Verifica que el proxy reverso tenga configurado el upgrade de WebSocket
4. Revisa los logs: `docker-compose logs -f backend`

#### CORS errors

1. Añade todos los dominios necesarios a `CORS_ORIGINS` en `.env`
2. Reinicia los contenedores: `docker-compose restart`

#### La variable de entorno no se aplica

1. Reconstruye con la nueva variable:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

2. Verifica que el archivo `env.js` se genere correctamente:
```bash
docker exec furor_frontend cat /usr/share/nginx/html/env.js
```

Debería mostrar:
```javascript
window.__env = {
  VITE_API_URL: "https://api.furor.molero.org"
};
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
