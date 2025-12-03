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
EXPOSE 80
