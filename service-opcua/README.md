# NEE202504 - service-opcua

Ce projet implémente un service **OPC UA** en Python avec la librairie `asyncua`.  
Il permet de **surveiller les variables de production** (ilot 3) et de **piloter les validations côté service**.

---

## 🚀 Fonctionnalités

- Connexion à un serveur OPC UA (WAGO 751-9301 Compact Controller 100).
- Surveillance en temps réel des variables côté **ilot 3** :
  - `bDemande_fin_OF`
  - `nEtat_OF`
  - `nId_of`
  - `sOF_RFID`
- Actions côté **service** (Écriture):
  - `srv_bRecette_RFID`
  - `srv_bOF_Valide`

---

## 📦 Installation

1. Cloner le dépôt (branche `feature/service-opcua`) :
   ```bash
   git clone -b feature/service-opcua https://github.com/LeroyDu56/NEE202504---dev.git
   cd NEE202504/service-opcua
Créer et activer un environnement virtuel :

bash
Copier le code
python3 -m venv .venv
source .venv/bin/activate
Installer les dépendances :

bash
Copier le code
pip install -r requirements.txt
⚙️ Configuration
Créer un fichier .env à la racine du projet avec les variables suivantes :

ini
Copier le code
# Connexion OPC UA
OPCUA_ENDPOINT=opc.tcp://192.168.10.10:4840
OPCUA_USERNAME=admin
OPCUA_PASSWORD=wago

# NodeIds - Lecture Ilot3
NODE_bDemande_fin_OF=ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL_Ilot3.bDemande_fin_OF
NODE_nEtat_OF=ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL_Ilot3.nEtat_OF
NODE_nId_of=ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL_Ilot3.nId_of
NODE_sOF_RFID=ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL_Ilot3.sOF_RFID

# NodeIds - Écriture Service
NODE_srv_Recette=ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL_Service.srv_bRecette_RFID
NODE_srv_OF_Valide=ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL_Service.srv_bOF_Valide
⚠️ Le fichier .env ne doit pas être versionné (il est déjà dans .gitignore).

▶️ Utilisation
Lancer le service principal :

bash
Copier le code
python service_opcua.py
Explorer ou tester les nœuds OPC UA :

bash
Copier le code
python explore_opcua.py
📄 Structure du projet
graphql
Copier le code
service-opcua/
├── .gitignore
├── README.md
├── requirements.txt
├── service_opcua.py   # Service principal OPC UA
└── explore_opcua.py   # Script d’exploration/test
