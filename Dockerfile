# Étape 1 : Build de l'application avec Node.js
FROM node:18-alpine AS build

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier tout le reste du code
COPY . .

# Build avec Vite
RUN npm run build

# Étape 2 : Servir l'app statique avec nginx
FROM nginx:stable-alpine

# Copier les fichiers build depuis l'étape précédente
COPY --from=build /app/dist /usr/share/nginx/html

# Exposer le port 80
EXPOSE 80

# Lancer nginx en mode foreground
CMD ["nginx", "-g", "daemon off;"]
