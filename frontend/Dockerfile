FROM node:20 as build
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Ensure Vite picks up VITE_API_URL at build time
RUN echo "VITE_API_URL=$VITE_API_URL" > .env.production && npm run build

# Servidor web liviano para producción
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Inject a small runtime loader into index.html so we can set API URL at container start
RUN if [ -f /usr/share/nginx/html/index.html ]; then \
			sed -i "s#<head>#<head>\n    <script src=\"/env.js\"></script>#" /usr/share/nginx/html/index.html || true; \
		fi
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
