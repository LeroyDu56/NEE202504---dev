# opcua_server.py
import asyncio
import logging
from asyncua import Client
from typing import Dict, Any, Optional

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

    async def read_node_value(self, node_id: str) -> Any:
        """
        Lit la valeur d'un nœud OPC UA.
        """
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return None
        try:
            node = self.client.get_node(node_id)
            value = await node.read_value()
            logger.info(f"Valeur lue depuis {node_id} : {value}")
            return value
        except Exception as e:
            logger.error(f"Erreur de lecture dans {node_id} : {e}")
            return None

    async def read_multiple_values(self, node_ids: list[str]) -> Dict[str, Any]:
        """
        Lit plusieurs nœuds OPC UA en une seule opération.
        """
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return {}
        results = {}
        try:
            for node_id in node_ids:
                node = self.client.get_node(node_id)
                value = await node.read_value()
                results[node_id] = value
                logger.info(f"Valeur lue depuis {node_id} : {value}")
            return results
        except Exception as e:
            logger.error(f"Erreur de lecture multiple : {e}")
            return results

    # ------------------- Méthodes d'écriture -------------------

    async def write_node_value(self, node_id: str, value: Any) -> bool:
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return False
        try:
            node = self.client.get_node(node_id)
            await node.write_value(value)
            logger.info(f"Valeur {value} écrite dans {node_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur d'écriture dans {node_id} : {e}")
            return False

    async def write_multiple_values(self, values: Dict[str, Any]) -> bool:
        if not self.is_connected or not self.client:
            logger.error("Pas de connexion OPC UA active.")
            return False
        try:
            for node_id, value in values.items():
                node = self.client.get_node(node_id)
                await node.write_value(value)
            logger.info(f"Écriture multiple réussie : {len(values)} valeurs.")
            return True
        except Exception as e:
            logger.error(f"Erreur d'écriture multiple : {e}")
            return False

    # ------------------- Déconnexion -------------------

    async def disconnect(self):
        if self.is_connected and self.client:
            await self.client.disconnect()
            self.is_connected = False
            logger.info("Connexion OPC UA fermée.")
