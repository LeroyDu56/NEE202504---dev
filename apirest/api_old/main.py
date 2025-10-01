from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from services.odoo_service import Odoo
from services.opcua_service import OpcUaServer
from services.bdd_service import Database
from api.schemas.of_schema import OFData
from api.schemas.user_schema import TagRequest, TagResponse
from sqlalchemy.orm import Session
from api.models.user_model import Base, User
import os
from dotenv import load_dotenv
import uvicorn
import logging
from contextlib import contextmanager

app = FastAPI(title="API NEE202504")

logger = logging.getLogger(__name__)

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
opcua = OpcUaServer(endpoint_url="opc.tcp://192.168.10.10:4840")

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
        # --- Vérification et connexion OPC UA ---
        if not opcua.is_connected:
            connected = await opcua.connect()
            if not connected:
                raise HTTPException(status_code=500, detail="Impossible de se connecter au serveur OPC UA")
        else:
            # Vérifie que le client est encore vivant
            try:
                await opcua.client.get_node("ns=4;s=AutWriteOF").read_value()
            except Exception:
                connected = await opcua.connect()
                if not connected:
                    raise HTTPException(status_code=500, detail="Impossible de se reconnecter au serveur OPC UA")

        # --- Vérification de la variable AutWriteOF ---
        node_aut = opcua.client.get_node("ns=4;s=AutWriteOF")
        aut_write_of = await node_aut.read_value()

        if not isinstance(aut_write_of, bool):
            raise HTTPException(status_code=500, detail="La variable de contrôle n'est pas booléenne")
        if not aut_write_of:
            raise HTTPException(status_code=403, detail="Écriture OPC UA interdite (AutWriteOF=False)")

        # --- Écriture dans OPC UA ---
        nodes_to_write = {
            "ns=4;s=NumeroOF": of_data.OF,
            "ns=4;s=RecetteOF": of_data.Recette,
            "ns=4;s=QuantiteOF": of_data.Quantite
        }

        write_results = {}
        for node_id, value in nodes_to_write.items():
            node = opcua.client.get_node(node_id)
            try:
                await node.write_value(value)
                write_results[node_id] = True
            except Exception:
                write_results[node_id] = False

        successful = [k for k, v in write_results.items() if v]
        failed = [k for k, v in write_results.items() if not v]

        if failed:
            raise HTTPException(
                status_code=500,
                detail={"message": "Certaines écritures ont échoué", "successful": successful, "failed": failed}
            )

        # --- Lecture pour vérification ---
        vals = {}
        for node_id in nodes_to_write.keys():
            node = opcua.client.get_node(node_id)
            vals[node_id] = await node.read_value()

        return {"status": "success", "values": vals}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur : {str(e)}")

bdd = Database()

# Gestion de la session pour FastAPI (compatible avec async def)
@contextmanager
def get_db_session():
    session = bdd.get_session()
    try:
        yield session
    finally:
        session.close()

# Version asynchrone de la dépendance pour FastAPI
async def get_db_session_async():
    with get_db_session() as session:
        yield session

@app.post("/api/bdd/get_role/", response_model=TagResponse)
async def get_role(
    tag_request: TagRequest,
    session: Session = Depends(get_db_session_async)
):
    # Vérifie la connexion à la BDD
    if not bdd.check_connection():
        if not bdd.reconnect():
            raise HTTPException(status_code=500, detail="Échec de la reconnexion à la base de données")

    # Récupère le rôle (int)
    role = bdd.get_role_by_tag(session, tag_request.tag_rfid)

    if not opcua.is_connected:
        connected = await opcua.connect()
        if not connected:
            raise HTTPException(status_code=500, detail="Échec de la connexion au serveur OPC UA")

    node_id = "ns=4;s=RoleUser"  # À adapter selon ton serveur OPC UA
    opcua_result = await opcua.write_node_value(node_id, role)
    success = opcua_result.get(node_id, False)


    # Retour JSON à la webvisu
    return {"tag_rfid": tag_request.tag_rfid, "role": role, "opcua_written": success}



@app.get("/api/opcua/ping")
async def opcua_ping():
    if await opcua.ping():
        data = await opcua.get_data()
        return {"status": "ok", "data": data}
    else:
        return {"status": "error", "detail": "Impossible de se connecter au serveur OPC UA"}


# Point d'entrée pour lancer l'API
if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8888)