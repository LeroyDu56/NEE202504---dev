import xmlrpc.client
from typing import List, Dict
from dotenv import load_dotenv
import logging
load_dotenv()

logger = logging.getLogger("ERP")

class ERP:
    """
    Classe pour gérer la connexion à Odoo et récupérer les ordres de fabrication
    """

    def __init__(self, url: str, database: str, username: str, password: str):
        """
        Initialise la connexion Odoo
        
        Args:
            url: URL du serveur Odoo (ex: http://localhost:8069)
            database: Nom de la base de données Odoo
            username: Nom d'utilisateur Odoo
            password: Mot de passe Odoo
        """
        self.url = url
        self.database = database
        self.username = username
        self.password = password

        self.uid = None
        self.models = None
        self.is_connected = False

    def connect(self) -> bool:
        """
        Établit la connexion avec le serveur Odoo
        
        Returns:
            bool: True si la connexion est établie, False sinon
        """
        try:
            logger.info(f"Tentative de connexion à Odoo: {self.url}")
            logger.info(f"Base de données: {self.database}")
            logger.info(f"Utilisateur: {self.username}")

            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(
                self.database,
                self.username,
                self.password,
                {}
            )

            if not self.uid:
                logger.error("Échec de l'authentification Odoo")
                logger.error("Vérifiez vos identifiants (URL, database, username, password)")
                return False

            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            self.is_connected = True
            logger.info(f"Connexion Odoo réussie - UID: {self.uid}")
            return True

        except ConnectionError as e:
            logger.error(f"Erreur de connexion réseau: {e}")
            logger.error("   Vérifiez que le serveur Odoo est accessible")
            return False
        except Exception as e:
            logger.error(f"Erreur de connexion Odoo: {e}")
            return False

    def get_ofs(self) -> List[Dict]:
        """
        Récupère tous les ordres de fabrication depuis Odoo
        
        Returns:
            List[Dict]: Liste des ordres de fabrication avec leurs données
        """
        # Si non connecté, essaie de se connecter
        if not self.is_connected and not self.connect():
            logger.error("Impossible de récupérer les OFs : pas de connexion Odoo")
            return []

        try:
            logger.info("Récupération des ordres de fabrication depuis Odoo...")

            manufacturing_orders = self.models.execute_kw(
                self.database, self.uid, self.password,
                'mrp.production',
                'search_read',
                [[]],  # Domaine vide = tous les ordres
                {
                    'fields': [
                        'name',
                        'product_id',
                        'product_qty',
                        'qty_produced',
                        'state',
                        'date_planned_start',
                        'date_planned_finished',
                    ],
                    'order': 'date_planned_start desc',
                    'limit': 500
                }
            )

            processed_orders: List[Dict] = []
            for order in manufacturing_orders:
                try:
                    # Ici tu peux transformer les données si besoin,
                    # par exemple convertir les dates en objets datetime, etc.
                    processed_order = order
                    processed_orders.append(processed_order)
                except Exception as e:
                    logger.error(f"⚠️ Erreur traitement OF {order.get('id', 'N/A')}: {e}")
                    # On continue sur l’ordre suivant
                    continue

            logger.info(f"{len(processed_orders)} ordres de fabrication récupérés avec succès")
            return processed_orders

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des OFs : {e}")
            return []

    def disconnect(self):
        """Ferme la connexion Odoo"""
        self.uid = None
        self.models = None
        self.is_connected = False
        logger.info("Connexion Odoo fermée")
