# =========================
# Etapa 1: Build da aplicação
# =========================
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# =========================
# Etapa 2: Servir com Nginx
# =========================
FROM nginx:1.25-alpine

# Copia o build para o Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copia o nginx.conf personalizado
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
