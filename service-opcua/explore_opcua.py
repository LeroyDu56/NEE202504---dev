#!/usr/bin/env python3
import asyncio
from asyncua import Client

OPCUA_ENDPOINT = "opc.tcp://192.168.10.10:4840"
USERNAME = "admin"
PASSWORD = "wago"

async def browse_node(node, indent=0):
    try:
        children = await node.get_children()
        for c in children:
            browse_name = await c.read_browse_name()
            nodeid = c.nodeid.to_string()
            print("  " * indent + f"- {browse_name.Name} ({nodeid})")
            # appel récursif (descend dans la hiérarchie)
            await browse_node(c, indent + 1)
    except Exception as e:
        print("  " * indent + f"❌ Impossible de parcourir ce nœud : {e}")

async def main():
    client = Client(OPCUA_ENDPOINT)
    client.set_user(USERNAME)
    client.set_password(PASSWORD)

    try:
        await client.connect()
        print(f"✅ Connecté à {OPCUA_ENDPOINT}")
        print("🌳 Parcours complet de l'arborescence OPC UA...\n")

        objects = client.nodes.objects
        await browse_node(objects)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
