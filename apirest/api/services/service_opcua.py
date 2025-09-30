import logging
from typing import Any, Dict, List, Optional

from asyncua import Client, ua
from asyncua.ua.uaerrors import UaStatusCodeError
from asyncua.common.subscription import Subscription
from asyncua.common.subscription import DataChangeNotificationHandler

logger = logging.getLogger("OPCUA")

class OPCUAClientError(Exception):
    """Exception pour les erreurs liées au client OPC UA."""
    pass

class OPCUAClient:
    """
    Client OPC UA minimal mais structuré :
    - connect / disconnect
    - read (simple / multiple)
    - write (simple / multiple)
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.client: Optional[Client] = None
        self.logger = logging.getLogger("opcua_api")

    async def connect(self):
        if self.client is not None:
            self.logger.warning(f"Tentative de connecter alors que déjà initialisé : {self.endpoint}")
            return
        self.client = Client(self.endpoint)
        try:
            await self.client.connect()
            self.logger.info(f"Connecté au serveur OPC UA : {self.endpoint}")
        except Exception as e:
            self.logger.error(f"Impossible de se connecter à {self.endpoint}: {e}")
            self.client = None
            raise OPCUAClientError(f"Erreur de connexion : {e}")

    async def disconnect(self):
        if self.client:
            try:
                await self.client.disconnect()
                self.logger.info(f"Déconnecté du serveur OPC UA : {self.endpoint}")
            except Exception as e:
                self.logger.error(f"Erreur de déconnexion : {e}")
        self.client = None

    def is_connected(self) -> bool:
        return self.client is not None

    async def read(self, node_id: str) -> Any:
        if self.client is None:
            raise OPCUAClientError("Client non connecté")
        try:
            node = self.client.get_node(node_id)
            val = await node.read_value()
            self.logger.info(f"Lecture {node_id} -> {val}")
            return val
        except Exception as e:
            self.logger.error(f"Erreur lecture {node_id}: {e}")
            raise OPCUAClientError(f"Lecture échouée {node_id}: {e}")

    async def read_multiple(self, node_ids: List[str]) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        for nid in node_ids:
            try:
                v = await self.read(nid)
                res[nid] = v
            except OPCUAClientError as e:
                res[nid] = f"Erreur: {e}"
        return res

    async def write(self, node_id: str, value: Any, variant_type: Optional[ua.VariantType] = None) -> Any:
        if self.client is None:
            raise OPCUAClientError("Client non connecté")
        try:
            node = self.client.get_node(node_id)
        except Exception as e:
            self.logger.error(f"Nœud non trouvé {node_id}: {e}")
            raise OPCUAClientError(f"Nœud non trouvé {node_id}")

        # Préparer variant
        var = None
        if variant_type is not None:
            try:
                var = ua.Variant(value, variant_type)
            except Exception as e:
                self.logger.error(f"Erreur conversion variant pour {node_id}: {e}")
                raise OPCUAClientError(f"Conversion variant échouée {node_id}: {e}")
        else:
            var = ua.Variant(value, value)

        try:
            await node.write_value(var)
            self.logger.info(f"Écriture : {node_id} = {value}")
        except UaStatusCodeError as e:
            self.logger.error(f"Write rejeté pour {node_id}: {e}")
            raise OPCUAClientError(f"Write rejeté {node_id}: {e}")
        except Exception as e:
            self.logger.error(f"Erreur écriture {node_id}: {e}")
            raise OPCUAClientError(f"Écriture échouée {node_id}: {e}")

        # Vérification
        try:
            new_val = await node.read_value()
            if new_val != value:
                self.logger.warning(f"Mismatch post-écriture {node_id}: écrit {value}, lu {new_val}")
                raise OPCUAClientError(f"Valeur non appliquée {node_id}: {new_val}")
            return new_val
        except Exception as e:
            self.logger.error(f"Erreur lecture post-écriture {node_id}: {e}")
            raise OPCUAClientError(f"Lecture vérification échouée {node_id}: {e}")

    async def write_multiple(self, mapping: Dict[str, Any], variant_types: Optional[Dict[str, ua.VariantType]] = None) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        for nid, val in mapping.items():
            vtype = None
            if variant_types and nid in variant_types:
                vtype = variant_types[nid]
            try:
                new = await self.write(nid, val, vtype)
                res[nid] = new
            except OPCUAClientError as e:
                res[nid] = f"Erreur: {e}"
        return res
