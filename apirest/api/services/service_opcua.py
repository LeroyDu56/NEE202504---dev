import logging
from typing import Any, Dict, List, Optional

from asyncua import Client, ua
from asyncua.ua.uaerrors import UaStatusCodeError

logger = logging.getLogger("OPCUA")


class OPCUAClientError(Exception):
    """Exception pour les erreurs liées au client OPC UA."""
    pass


class OPCUAClient:
    """
    Client OPC UA minimal mais structuré :
    - connect / disconnect
    - check_connection (ping + reconnexion)
    - read / read_multiple
    - write / write_multiple
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.client: Optional[Client] = None
        self.logger = logging.getLogger("opcua_api")

    async def connect(self):
        """Connexion au serveur OPC UA."""
        if self.client is not None:
            self.logger.warning(f"Tentative de connexion alors que déjà initialisé : {self.endpoint}")
            return
        self.client = Client(self.endpoint)
        try:
            await self.client.connect()
            self.logger.info(f"✅ Connecté au serveur OPC UA : {self.endpoint}")
        except Exception as e:
            self.logger.error(f"❌ Impossible de se connecter à {self.endpoint}: {e}")
            self.client = None
            raise OPCUAClientError(f"Erreur de connexion : {e}")

    async def disconnect(self):
        """Déconnexion du serveur OPC UA."""
        if self.client:
            try:
                await self.client.disconnect()
                self.logger.info(f"🔌 Déconnecté du serveur OPC UA : {self.endpoint}")
            except Exception as e:
                self.logger.error(f"Erreur de déconnexion : {e}")
        self.client = None

    def is_connected(self) -> bool:
        """Retourne True si une session OPC UA existe (mais pas forcément valide)."""
        return self.client is not None

    async def check_connection(self) -> bool:
        """
        Vérifie si la connexion OPC UA est encore valide en lisant l'état du serveur.
        Si la session est cassée, tente une reconnexion.
        """
        if self.client is None:
            self.logger.warning("⚠️ Client OPC UA non initialisé.")
            return False
        try:
            await self.client.nodes.server_state.read_value()
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ Connexion OPC UA cassée : {e}. Tentative de reconnexion...")
            await self.disconnect()
            try:
                await self.connect()
                return True
            except Exception as err:
                self.logger.error(f"❌ Échec de reconnexion OPC UA : {err}")
                return False

    async def read(self, node_id: str) -> Any:
        """Lecture simple d’un nœud OPC UA."""
        if self.client is None:
            raise OPCUAClientError("Client non connecté")
        try:
            node = self.client.get_node(node_id)
            val = await node.read_value()
            self.logger.info(f"📖 Lecture {node_id} -> {val}")
            return val
        except Exception as e:
            self.logger.error(f"Erreur lecture {node_id}: {e}")
            raise OPCUAClientError(f"Lecture échouée {node_id}: {e}")

    async def read_multiple(self, node_ids: List[str]) -> Dict[str, Any]:
        """Lecture multiple de nœuds OPC UA."""
        res: Dict[str, Any] = {}
        for nid in node_ids:
            try:
                v = await self.read(nid)
                res[nid] = v
            except OPCUAClientError as e:
                res[nid] = f"Erreur: {e}"
        return res

    async def write(self, node_id: str, value: Any, variant_type: Optional[ua.VariantType] = None) -> Any:
        """Écriture simple sur un nœud OPC UA avec auto-détection du type."""
        if self.client is None:
            raise OPCUAClientError("Client non connecté")
        try:
            node = self.client.get_node(node_id)
        except Exception as e:
            self.logger.error(f"Nœud non trouvé {node_id}: {e}")
            raise OPCUAClientError(f"Nœud non trouvé {node_id}")

        # Fonction interne pour deviner le VariantType
        def guess_variant_type(val: Any) -> ua.VariantType:
            if isinstance(val, bool):
                return ua.VariantType.Boolean
            if isinstance(val, int):
                return ua.VariantType.UInt16  # ou Int64 si besoin
            if isinstance(val, float):
                return ua.VariantType.Double
            if isinstance(val, str):
                return ua.VariantType.String
            raise OPCUAClientError(f"Type non supporté pour conversion Variant: {type(val)}")

        # Préparer le Variant
        try:
            if variant_type is None:
                variant_type = guess_variant_type(value)
            var = ua.Variant(value, variant_type)
        except Exception as e:
            self.logger.error(f"Erreur conversion variant pour {node_id}: {e}")
            raise OPCUAClientError(f"Conversion variant échouée {node_id}: {e}")

        # Écriture
        try:
            await node.write_value(var)
            self.logger.info(f"✍️ Écriture : {node_id} = {value} ({variant_type.name})")
        except UaStatusCodeError as e:
            self.logger.error(f"Write rejeté pour {node_id}: {e}")
            raise OPCUAClientError(f"Write rejeté {node_id}: {e}")
        except Exception as e:
            self.logger.error(f"Erreur écriture {node_id}: {e}")
            raise OPCUAClientError(f"Écriture échouée {node_id}: {e}")

        # Vérification post-écriture
        try:
            new_val = await node.read_value()
            if new_val != value:
                self.logger.warning(f"⚠️ Mismatch post-écriture {node_id}: écrit {value}, lu {new_val}")
                raise OPCUAClientError(f"Valeur non appliquée {node_id}: {new_val}")
            return new_val
        except Exception as e:
            self.logger.error(f"Erreur lecture post-écriture {node_id}: {e}")
            raise OPCUAClientError(f"Lecture vérification échouée {node_id}: {e}")

    async def write_multiple(self, mapping: Dict[str, Any], variant_types: Optional[Dict[str, ua.VariantType]] = None) -> Dict[str, Any]:
        """Écriture multiple de nœuds OPC UA."""
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