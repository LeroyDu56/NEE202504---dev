import asyncio
from asyncua import Client
import traceback

async def test():
    url = "opc.tcp://192.168.10.10:4840"  # ton serveur OPC UA
    try:
        async with Client(url=url) as client:
            # On se connecte et on récupère le Node "Server" pour le parcourir
            server_node = client.nodes.server
            children = await server_node.get_children()
            print("✅ Connexion réussie ! Nombre d'enfants du nœud serveur :", len(children))
            for child in children:
                print(" -", await child.read_browse_name())
    except Exception as e:
        print("❌ Erreur OPC UA :")
        traceback.print_exc()

asyncio.run(test())
