import asyncio
from services.opcua_service import OpcUaServer

async def test():
    opcua = OpcUaServer("opc.tcp://localhost:53530/OPCUA/SimulationServer")
    if await opcua.connect():
        # --- Test écriture dans l'objet OFs ---
        await opcua.write_multiple_values({
            "ns=3;s=NumeroOF": 2,
            "ns=3;s=Recette": 5,
            "ns=3;s=Quantite": 1

        })

        # Vérification en lecture
        vals = await opcua.read_multiple_values([
            "ns=3;s=NumeroOF",
            "ns=3;s=Recette",
            "ns=3;s=Quantite"
        ])
        print("Valeurs OF :", vals)

        await opcua.disconnect()

asyncio.run(test())
