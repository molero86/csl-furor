# 🚨 SOLUCIÓN URGENTE - Acceso Externo a Furor App

## ⚡ Situación
Necesitas que personas fuera de tu red local accedan a la app **AHORA**.

## 🎯 Dos Opciones Rápidas

---

## ✅ OPCIÓN 1: Usar tu IP Pública + Abrir Puertos (Recomendado)

### Ventajas
- ✅ Gratis
- ✅ Mejor rendimiento
- ✅ Sin límites de tiempo

### Desventajas
- ⚠️ Requiere configurar el router (5-10 minutos)

### Pasos:

**1. Ejecuta el script automático:**

```powershell
.\quick-setup-ip.ps1
```

**2. Configura tu router:**

El script te dará tu IP pública (ej: `85.123.45.67`)

Entra a tu router (normalmente `192.168.1.1` o `192.168.0.1`):
- Usuario/Pass: Admin/admin o mira la pegatina del router
- Busca: "Port Forwarding" o "NAT" o "Redirección de puertos"
- Añade dos reglas:

```
Puerto Externo: 4017 → IP Interna: 192.168.X.X → Puerto Interno: 4017
Puerto Externo: 4018 → IP Interna: 192.168.X.X → Puerto Interno: 4018
```

*(192.168.X.X es la IP de tu ordenador en la red local - encuéntrala con `ipconfig`)*

**3. Comparte la URL:**
```
http://TU_IP_PUBLICA:4018
```

---

## ✅ OPCIÓN 2: Usar ngrok (Sin Configurar Router - MÁS FÁCIL)

### Ventajas
- ✅ No necesitas configurar el router
- ✅ HTTPS automático
- ✅ Configuración en 5 minutos

### Desventajas
- ⚠️ Cuenta gratis tiene límites (pero suficientes para una sesión)
- ⚠️ URLs cambian cada vez que reinicias

### Pasos:

**1. Descarga ngrok:**
- Ve a: https://ngrok.com/download
- Descarga para Windows
- Descomprime `ngrok.exe` en la carpeta del proyecto

**2. Regístrate gratis:**
- https://dashboard.ngrok.com/signup
- Copia tu authtoken

**3. Ejecuta el script:**
```powershell
.\quick-setup-ngrok.ps1
```

**4. El script te pedirá:**
- Tu authtoken de ngrok
- Abrirá dos túneles (backend y frontend)
- Te dará una URL pública para compartir

**5. Comparte la URL:**
```
https://random123.ngrok.io
```

---

## 🆘 SOLUCIÓN ULTRA RÁPIDA (1 Minuto)

Si no tienes tiempo ni para los scripts:

**1. Instala ngrok:**
```powershell
# Descarga de https://ngrok.com/download
# Descomprime en esta carpeta
```

**2. Ejecuta en esta carpeta:**
```powershell
# Terminal 1 (Docker)
docker-compose up -d

# Terminal 2 (ngrok backend)
ngrok http 4017

# Terminal 3 (ngrok frontend)  
ngrok http 4018
```

**3. Copia las URLs que aparecen en ngrok:**
- Frontend: `https://abc123.ngrok.io` (esta es la que compartes)
- Backend: `https://def456.ngrok.io`

**4. Actualiza .env:**
```env
VITE_API_URL=https://def456.ngrok.io
CORS_ORIGINS=https://abc123.ngrok.io
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/furor
```

**5. Reconstruye:**
```powershell
docker-compose build --no-cache frontend
docker-compose restart
```

**6. Comparte:**
```
https://abc123.ngrok.io
```

---

## 🎯 ¿Cuál Elegir?

### Usa **OPCIÓN 1** (IP Pública) si:
- Tienes acceso al router
- Es para una presentación larga o evento
- Quieres mejor rendimiento

### Usa **OPCIÓN 2** (ngrok) si:
- NO puedes/sabes configurar el router
- Es para una demo rápida
- Necesitas HTTPS

---

## ⚠️ Checklist Final

Antes de compartir la URL:

- [ ] Docker está corriendo: `docker ps`
- [ ] Puedes acceder localmente: http://localhost:4018
- [ ] El archivo env.js tiene la URL correcta:
  ```powershell
  docker exec furor_frontend cat /usr/share/nginx/html/env.js
  ```
- [ ] Los logs no muestran errores:
  ```powershell
  docker-compose logs -f
  ```

---

## 🐛 Si Algo Falla

```powershell
# Ver logs
docker-compose logs -f

# Reiniciar todo
docker-compose down
docker-compose up -d

# Verificar que env.js es correcto
docker exec furor_frontend cat /usr/share/nginx/html/env.js
```

---

## 💡 Tips

1. **ngrok gratis tiene límite de conexiones simultáneas** - Si muchas personas se conectan a la vez, considera la opción 1
2. **Mantén las ventanas abiertas** - Si cierras la terminal de ngrok, se pierde el túnel
3. **IP pública puede cambiar** - Si tu ISP te da IP dinámica, puede cambiar al reiniciar el router
4. **Firewall de Windows** - Puede pedir permiso para abrir puertos, acepta

---

## 🎉 ¡Ya está!

Ahora cualquiera puede acceder a tu app con la URL que compartas, desde cualquier red.
