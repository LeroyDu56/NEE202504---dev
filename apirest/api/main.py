from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from services.odoo_service import Odoo
from services.opcua_service import OpcUaServer
from api.schemas.of_schema import OFData
import os
from dotenv import load_dotenv
import uvicorn

app = FastAPI(title="API NEE202504")

# Configurer CORS (pour autoriser les requêtes depuis ta supervision)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Instance de la classe Odoo (à initialiser une seule fois)
odoo = Odoo(
    url=os.getenv("ODOO_URL", "http://localhost:8069"),
    database=os.getenv("ODOO_DB", "mydb"),
    username=os.getenv("ODOO_USER", "OperateurA@nee.com"),
    password=os.getenv("ODOO_PASSWORD", "ton_mot_de_passe"),
)

# Instance de la classe OpcUaServer
opcua = OpcUaServer(endpoint_url="opc.tcp://localhost:53530/OPCUA/SimulationServer")



# Endpoint pour récupérer les OFs
@app.get("/api/erp/ofs", response_model=List[Dict], tags=["Ordre de Fabrication"])
async def get_ofs():
    """
    Récupère la liste des ordres de fabrication depuis Odoo.
    Retourne :
    - Liste des OFs (avec leurs champs principaux)
    - Code 200 si succès
    - Code 500 si erreur
    """
    try:
        # Connexion à Odoo si ce n'est pas déjà fait
        if not odoo.is_connected:
            if not odoo.connect():
                raise HTTPException(status_code=500, detail="Échec de la connexion à Odoo")

        # Récupération des OFs
        ofs = odoo.get_ofs()
        if not ofs:
            raise HTTPException(status_code=404, detail="Aucun ordre de fabrication trouvé")

        return ofs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


@app.post("/api/opcua/write-of")
async def write_of_to_opcua(of_data: OFData):
    try:
        # Vérification de la variable booléenne avant d'écrire
        aut_write_of = await opcua.read_node_value("ns=3;s:AutWriteOF")

        if not isinstance(aut_write_of, bool):
            raise HTTPException(status_code=500, detail="La variable de contrôle n'est pas booléenne")
        if not aut_write_of:
            raise HTTPException(status_code=403, detail="Écriture OPC UA interdite (AutWriteOF=False)")

        # Écriture dans OPC UA
        success = await opcua.write_multiple_values({
            "ns=3;s=NumeroOF": of_data.OF,
            "ns=3;s=Recette": of_data.Recette,
            "ns=3;s=Quantite": of_data.Quantite
        })

        if not success:
            raise HTTPException(status_code=500, detail="Échec de l'écriture dans OPC UA")

        # Lecture pour vérification
        vals = await opcua.read_multiple_values([
            "ns=3;s=NumeroOF",
            "ns=3;s=Recette",
            "ns=3;s=Quantite"
        ])
        return {"status": "success", "values": vals}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur : {str(e)}")

# Point d'entrée pour lancer l'API
if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)