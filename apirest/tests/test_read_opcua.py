from services.opcua_service import OpcUaServer
import asyncio

async def main():
    # URL du serveur et NodeId de ta variable booléenne
    url = "opc.tcp://localhost:53530/OPCUA/SimulationServer"
    node_id = "ns=3;s=AutWriteOF"

    client = OpcUaServer(url)
    await client.connect()

    value = await client.read_node_value(node_id)
    print(f"Valeur brute : {value}")
    print(f"Type Python : {type(value)}")

    if isinstance(value, bool):
        print("✅ La variable est bien un booléen")
    elif value is None:
        print("⚠️ La variable n'a pas de valeur (None) → pense à lui assigner true/false dans Prosys")
    else:
        print("⚠️ La variable existe mais n'est pas un booléen pur")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())