# Base de données NEE_Electronic (Docker)

Une base MySQL + Adminer pour tracer les opérations RFID et OF de l’application **NEE_Electronic**.

---

## 📋 Prérequis

- [Docker](https://www.docker.com/) installé (version 20+ conseillée)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🚀 Installation & Lancement

1. Placez-vous dans le dossier du projet :

```bash
cd ~/Documents/local/base_de_donnees
```

2. Construisez et démarrez les conteneurs :

```bash
docker compose up -d --build
```

3. Accédez à Adminer :  
👉 [http://localhost:8080](http://localhost:8080)

---

## 🔄 Réinitialisation avec `down -v`

À chaque fois que vous modifiez le fichier **init/** (par ex. création de tables ou données seed), ou s'il y a eu un problème lors de l'installation et qu'il faut la refaire, il faut relancer la base de zéro.  
Sinon, MySQL ne rejoue pas les scripts d’initialisation.

```bash
docker compose down -v      # arrête et supprime les conteneurs + volumes
docker compose up -d --build
```

- L’option `-v` supprime le **volume** contenant les données MySQL.  
- Sans `-v`, les données restent et vos changements dans `init/` ne seront **pas pris en compte**.

---

## ⚠️ Attention au bon `docker-compose.yml`

Si, au lancement, vous voyez un message comme :

```
WARN[0000] /home/user/docker-compose.yml: the attribute `version` is obsolete...
no such service: mysql
```

Cela signifie que Docker n’utilise **pas le bon fichier compose**.  
Dans ce cas, pointez explicitement vers celui du projet :

```bash
docker compose -f ~/Documents/local/base_de_donnees/docker-compose.yml down -v
docker compose -f ~/Documents/local/base_de_donnees/docker-compose.yml up -d --build
```

---

## 📂 Structure du projet

```
base_de_donnees/
├─ init/                # Scripts SQL exécutés au premier lancement
│  └─ 01-schema.sql
├─ .env                 # Variables d'environnement (Mots de passe, DB, etc.)
├─ docker-compose.yml   # Définition des services (mysql, adminer)
├─ Dockerfile           # Image MySQL custom avec init
└─ README.md            # Documentation
```

---

## 🔑 Connexion avec Adminer

Dans l’interface [Adminer](http://localhost:8080), utilisez les infos suivantes :

- **Système** : MySQL  
- **Serveur** : `mysql` (nom du service Docker)  
- **Utilisateur** : `nee_user`  
- **Mot de passe** : `password`  
- **Base de données** : `NEE_Electronic`  

> ⚠️ Ces valeurs sont définies dans le fichier `.env`.  
Si vous les modifiez, ajustez-les ici aussi.

---

## ✅ Vérification en ligne de commande

Pour vérifier que la base et les tables sont créées :

```bash
docker exec nee-mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD"   -e "SHOW TABLES FROM NEE_Electronic;"
```

---

## 🛠️ Dépannage

- Voir les logs de MySQL :
```bash
docker logs nee-mysql
```
- Voir les logs d’Adminer :
```bash
docker logs nee-adminer
```
- Supprimer un conteneur bloqué :
```bash
docker rm -f nom_du_conteneur
```

---

## 👤 Auteur / Licence

- Auteur : Projet **NEE Electronics**
- Licence : Usage interne (ajuster selon besoin)
