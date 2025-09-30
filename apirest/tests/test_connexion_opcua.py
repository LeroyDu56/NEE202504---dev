import asyncio
import logging
from asyncua import Client, ua
from asyncua.common.subscription import DataChangeNotificationHandler

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


logger = logging.getLogger("opcua_subscription_test")
# Configuration du logger pour le module asyncua
logging.getLogger("asyncua").setLevel(logging.WARNING)

class MyHandler(DataChangeNotificationHandler):
    def datachange_notification(self, node, val, data):
        """
        Callback appelé lors d'un changement de valeur sur le nœud abonné.
        """
        logger.info(f"Valeur du nœud {node} changé.")

async def main():
    endpoint = "opc.tcp://192.168.10.10:4840"
    node_id = "i=2256"
    
    # Création du client OPC UA
    client = Client(endpoint)
    try:
        # Connexion au serveur
        await client.connect()
        logger.info(f"Connecté au serveur OPC UA : {endpoint}")
        
        # Obtention du nœud à surveiller
        node = client.get_node(node_id)
        
        # Création du handler pour gérer les notifications de changement
        handler = MyHandler()
        
        # Création de la subscription avec un intervalle de publication de 1000 ms
        subscription = await client.create_subscription(500, handler)
        
        # Abonnement aux changements de données du nœud
        await subscription.subscribe_data_change(node)
        
        # Maintien de la subscription active
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Arrêt de la subscription...")
    except Exception as e:
        logger.error(f"Erreur lors de la connexion ou de la communication avec le serveur OPC UA : {e}")
        logger.info("Tentative de reconnexion...")
        await asyncio.sleep(5)  # Attente avant la reconnexion
        await main()  # Tentative de reconnexion
    finally:
        # Déconnexion du serveur
        await client.disconnect()
        logger.info("Déconnecté du serveur OPC UA.")

if __name__ == "__main__":
    asyncio.run(main())
