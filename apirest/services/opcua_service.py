# opcua_server.py
import asyncio
import logging
from asyncua import Client
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpcUaServer:
    def __init__(self, endpoint_url: str, username: str = "", password: str = ""):
        self.endpoint_url = endpoint_url
        self.username = username
        self.password = password
        self.client: Optional[Client] = None
        self.is_connected = False

    async def connect(self) -> bool:
        try:
            self.client = Client(self.endpoint_url)
            if self.username and self.password:
                await self.client.set_user(self.username)
                await self.client.set_password(self.password)
            await self.client.connect()
            self.is_connected = True
            logger.info(f"Connexion OPC UA réussie : {self.endpoint_url}")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion OPC UA : {e}")
            self.is_connected = False
            return False

    # ------------------- Méthodes de lecture ------------------- 
    async def read_node_value(self, node_id: str) -> Dict[str, Any]:
        """
        Lit la valeur d'un nœud OPC UA en gérant les erreurs.
        Retourne un dictionnaire {node_id: value} ou {node_id: None} si erreur.
        """
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return {node_id: None}
        
        try:
            node = self.client.get_node(node_id)
            value = await node.read_value()
            logger.info(f"Valeur lue depuis {node_id} : {value}")
            return {node_id: value}
        except Exception as e:
            logger.error(f"Erreur de lecture pour {node_id} : {e}")
            return {node_id: None}

    async def read_multiple_values(self, node_ids: List[str]) -> Dict[str, Any]:
        """
        Lit plusieurs nœuds OPC UA en parallèle.
        Retourne un dictionnaire {node_id: value}.
        """
        # Validation d'entrée ajoutée
        if not node_ids:
            return {}
        
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return {node_id: None for node_id in node_ids}
        
        # Gestion des exceptions améliorée
        tasks = [self.read_node_value(node_id) for node_id in node_ids]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Fusionner tous les dictionnaires individuels en un seul
        results = {}
        for i, res in enumerate(results_list):
            if isinstance(res, Exception):
                # Gestion explicite des exceptions dans gather
                logger.error(f"Exception lors de la lecture de {node_ids[i]}: {res}")
                results[node_ids[i]] = None
            elif isinstance(res, dict):
                results.update(res)
            else:
                # Cas imprévu - sécurité
                logger.warning(f"Résultat inattendu pour {node_ids[i]}: {type(res)}")
                results[node_ids[i]] = None
        
        return results

    # ------------------- Méthodes d'écriture -------------------

    async def write_node_value(self, node_id: str, value: Any) -> Dict[str, bool]:
        """
        Écrit une valeur dans un nœud OPC UA en gérant les erreurs.
        Retourne un dictionnaire {node_id: success_status}.
        """
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return {node_id: False}
        
        try:
            node = self.client.get_node(node_id)
            await node.write_value(value)
            logger.info(f"Valeur {value} écrite dans {node_id}")
            return {node_id: True}
        except Exception as e:
            logger.error(f"Erreur d'écriture dans {node_id} : {e}")
            return {node_id: False}

    async def write_multiple_values(self, values: Dict[str, Any]) -> Dict[str, bool]:
        """
        Écrit plusieurs valeurs OPC UA en parallèle.
        Retourne un dictionnaire {node_id: success_status}.
        """
        if not values:
            return {}
        
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return {node_id: False for node_id in values.keys()}

        async def write_safe(node_id: str, value: Any) -> Dict[str, bool]:
            """
            Écrit une valeur et retourne un dictionnaire {node_id: bool} pour la fusion.
            """
            try:
                success = await self.write_node_value(node_id, value)
                return {node_id: bool(success)}
            except Exception as e:
                logger.error(f"Exception lors de l'écriture de {node_id}: {e}")
                return {node_id: False}

        # Créer les tâches d'écriture parallèles
        tasks = [write_safe(node_id, value) for node_id, value in values.items()]
        results_list = await asyncio.gather(*tasks)

        # Fusionner tous les dictionnaires individuels
        results = {}
        for res in results_list:
            results.update(res)

        return results

    # ------------------- Déconnexion -------------------

    async def disconnect(self):
        if self.is_connected and self.client:
            await self.client.disconnect()
            self.is_connected = False
            logger.info("Connexion OPC UA fermée.")
