#!/bin/sh
set -e
# Write runtime env file consumed by the SPA
cat > /usr/share/nginx/html/env.js <<'EOF'
window.__env = {
  VITE_API_URL: "${VITE_API_URL:-}"
};
EOF

# If VITE_API_URL not provided, leave empty string
if [ -z "$VITE_API_URL" ]; then
  echo "[entrypoint] VITE_API_URL not set; env.js will have empty value"
else
  echo "[entrypoint] VITE_API_URL=$VITE_API_URL"
fi

# Start nginx in foreground
nginx -g 'daemon off;' 
