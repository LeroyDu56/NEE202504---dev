#!/usr/bin/env python3
import asyncio
from asyncua import Client
from dotenv import load_dotenv
import os
import sys

# Charger le .env
load_dotenv()

# --- Configuration ---
OPCUA_ENDPOINT = os.getenv("OPCUA_ENDPOINT")
USERNAME = os.getenv("OPCUA_USERNAME")
PASSWORD = os.getenv("OPCUA_PASSWORD")

# --- NodeIds ---
# Lecture côté Ilot3
NODE_bDemande_fin_OF = os.getenv("NODE_bDemande_fin_OF")
NODE_nEtat_OF        = os.getenv("NODE_nEtat_OF")
NODE_nId_of          = os.getenv("NODE_nId_of")
NODE_sOF_RFID        = os.getenv("NODE_sOF_RFID")

# Écriture côté Service
NODE_srv_Recette     = os.getenv("NODE_srv_Recette")
NODE_srv_OF_Valide   = os.getenv("NODE_srv_OF_Valide")

# Vérification des variables
required_vars = [
    "OPCUA_ENDPOINT", "OPCUA_USERNAME", "OPCUA_PASSWORD",
    "NODE_bDemande_fin_OF", "NODE_nEtat_OF", "NODE_nId_of", "NODE_sOF_RFID",
    "NODE_srv_Recette", "NODE_srv_OF_Valide"
]
for var in required_vars:
    if os.getenv(var) is None:
        print(f"❌ Variable manquante dans .env : {var}")
        sys.exit(1)


class SubHandler:
    """Callback appelé automatiquement lors d'un changement de valeur."""
    def __init__(self, service):
        self.service = service

    def datachange_notification(self, node, val, data):
        print(f"🔔 Changement {node}: {val}")

        # Exemple logique : si fin OF demandée → envoyer validation
        if node == self.service.node_flag and val is True:
            asyncio.create_task(self.service.send_validation())


class OPCUAService:
    def __init__(self, endpoint, username, password):
        self.client = Client(endpoint)
        self.client.set_user(username)
        self.client.set_password(password)

        # Nodes
        self.node_flag = None
        self.node_etat = None
        self.node_idof = None
        self.node_rfid = None
        self.node_recette = None
        self.node_valide = None

        self.sub = None

    async def connect(self):
        await self.client.connect()
        print(f"✅ Connecté à {OPCUA_ENDPOINT} en tant que {USERNAME}/{PASSWORD}")

        # Récupérer les nœuds
        self.node_flag   = self.client.get_node(NODE_bDemande_fin_OF)
        self.node_etat   = self.client.get_node(NODE_nEtat_OF)
        self.node_idof   = self.client.get_node(NODE_nId_of)
        self.node_rfid   = self.client.get_node(NODE_sOF_RFID)
        self.node_recette = self.client.get_node(NODE_srv_Recette)
        self.node_valide  = self.client.get_node(NODE_srv_OF_Valide)

        # Vérifier une lecture initiale
        init_flag = await self.node_flag.read_value()
        print(f"📖 Lecture initiale bDemande_fin_OF = {init_flag}")

        # Créer la subscription
        handler = SubHandler(self)
        self.sub = await self.client.create_subscription(500, handler)
        await self.sub.subscribe_data_change(self.node_flag)
        await self.sub.subscribe_data_change(self.node_etat)
        await self.sub.subscribe_data_change(self.node_idof)
        await self.sub.subscribe_data_change(self.node_rfid)

        print("📡 Subscriptions créées, attente des notifications...")

    async def send_validation(self):
        """Écrit TRUE sur Recette_RFID et OF_Valide."""
        print("➡️  Validation envoyée : Recette_RFID=TRUE, OF_Valide=TRUE")
        await self.node_recette.write_value(True)
        await self.node_valide.write_value(True)

    async def set_booleans(self, recette: bool, valide: bool):
        """Envoi manuel de booléens."""
        print(f"➡️  Envoi manuel : Recette_RFID={recette}, OF_Valide={valide}")
        await self.node_recette.write_value(recette)
        await self.node_valide.write_value(valide)

    async def run(self):
        try:
            await self.connect()

            # --- Test envoi manuel ---
            await self.set_booleans(True, True)
            await asyncio.sleep(3)
            await self.set_booleans(False, False)

            # Boucle infinie pour garder le service actif
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ Erreur : {e}")
        finally:
            await self.client.disconnect()
            print("⏹️ Déconnecté")


async def main():
    service = OPCUAService(OPCUA_ENDPOINT, USERNAME, PASSWORD)
    await service.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé par utilisateur")
