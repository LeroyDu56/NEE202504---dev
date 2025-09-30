# Vue 3 + TypeScript + Vite

# Se placer dans le dossier du projet
cd /chemin/vers/ton/projet

# Construire l'image Docker
docker build -t mon-vue-app .

# Lancer le conteneur
docker run -d -p 8080:80 --name mon-vue-conteneur mon-vue-app

# Vérifier que le conteneur tourne
docker ps

# Arrêter le conteneur
docker stop mon-vue-conteneur

# Redémarrer le conteneur
docker start mon-vue-conteneur
