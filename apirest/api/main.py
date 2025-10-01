import os
import traceback
from typing import List, Dict
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from asyncua import ua
from dotenv import load_dotenv

# 👉 Charger les variables d'environnement
load_dotenv()

# 👉 Imports internes
from apirest.api.config.log_config import setup_logging
from apirest.api.schemas.schema import (
    WriteMultipleData,
    ReadResponse,
    ReadMultipleResponse,
)
from apirest.api.schemas.user_schema import TagRequest, TagResponse
from apirest.api.services.service_opcua import OPCUAClient, OPCUAClientError
from apirest.api.services.odoo_service import ERP
from apirest.api.services.bdd_service import Database

# =======================
# Initialisation FastAPI
# =======================
app = FastAPI(title="API NEE202504")

# =======================
# Loggers
# =======================
logger = setup_logging("APIREST", logfile="logs/apirest.log", use_mysql=True)

api_logger = setup_logging("api", logfile="logs/api.log", use_mysql=True)
opcua_logger = setup_logging("opcua", logfile="logs/opcua.log", use_mysql=True)
erp_logger = setup_logging("erp", logfile="logs/erp.log", use_mysql=True)
mqtt_logger = setup_logging("mqtt", logfile="logs/mqtt.log", use_mysql=True)

# =======================
# Configurer CORS
# =======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# Services
# =======================
odoo = ERP(
    url=os.getenv("ODOO_URL", "http://localhost:8069"),
    database=os.getenv("ODOO_DB", "mydb"),
    username=os.getenv("ODOO_USER", "OperateurA@nee.com"),
    password=os.getenv("ODOO_PASSWORD", "ton_mot_de_passe"),
)

bdd = Database()

SERVER_URL = os.getenv("OPCUA_SERVER", "opc.tcp://192.168.10.10:4840")
opc = OPCUAClient(SERVER_URL)

# =======================
# Liste de nœuds OPC UA
# =======================
NODES_TO_READ = [
    "ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL.OPCUA.Ilot_1.AutWriteOF",
    "ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL.OPCUA.Ilot_1.NumeroOF",
    "ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL.OPCUA.Ilot_1.RecetteOF",
    "ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL.OPCUA.Ilot_1.QuantiteOF",
    "ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL.OPCUA.Ilot_1.RoleUser",
]

# =======================
# Events FastAPI
# =======================
@app.on_event("startup")
async def startup_event():
    try:
        await opc.connect()
        logger.info("Client OPC UA connecté à l’API")
    except Exception as e:
        logger.error(f"Erreur connexion au startup : {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await opc.disconnect()
        logger.info("Client OPC UA déconnecté à l’API")
    except Exception as e:
        logger.error(f"Erreur déconnexion : {e}")

# =======================
# Routes API
# =======================

@app.on_event("startup")
async def startup_event():
    try:
        await opc.connect()
        logger.info("Client OPC UA connecté à l’API")
    except Exception as e:
        logger.error(f"Erreur connexion au startup : {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await opc.disconnect()
        logger.info("Client OPC UA déconnecté à l’API")
    except Exception as e:
        logger.error(f"Erreur déconnexion : {e}")


@app.get("/api/opcua/read-all-values", response_model=ReadMultipleResponse)
async def read_all_values():
    if not opc.is_connected():
        raise HTTPException(status_code=500, detail="Client OPC UA non connecté")
    results: List[ReadResponse] = []
    for nid in NODES_TO_READ:
        try:
            val = await opc.read(nid)
            results.append(ReadResponse(node_id=nid, value=val))
        except OPCUAClientError as e:
            logger.warning(f"Impossible de lire {nid}: {e}")
            results.append(ReadResponse(node_id=nid, value=None, error=str(e)))
        except Exception as e:
            logger.error(f"Erreur inattendue lecture {nid}: {e}")
            traceback.print_exc()
            results.append(ReadResponse(node_id=nid, value=None, error="Erreur interne"))
    return ReadMultipleResponse(results=results)

@app.post("/api/opcua/write-of")
async def write_of(data: WriteMultipleData):
    if not opc.is_connected():
        raise HTTPException(status_code=500, detail="Client OPC UA non connecté")

    # Lire la valeur de AutWriteOF
    aut_write_value = await opc.read("ns=4;s=|var|WAGO 751-9301 Compact Controller 100.Application.GVL.OPCUA.Ilot_1.AutWriteOF")
    if not aut_write_value:
        raise HTTPException(status_code=400, detail="AutWriteOF est à False, écriture non autorisée")

    # Construire un mapping node_id → valeur
    mapping = {}
    variant_types = {}
    for w in data.writes:
        nid = next((nid for nid in NODES_TO_READ if w.node_name in nid), None)
        if not nid:
            # on continue sans écriture pour celui-ci
            continue
        mapping[nid] = w.value
        if w.variant_type:
            try:
                variant_types[nid] = getattr(ua.VariantType, w.variant_type)
            except Exception:
                # type non reconnu : on ne met pas dans variant_types
                pass

    # Effectuer l'écriture multiple
    try:
        result = await opc.write_multiple(mapping, variant_types)
        return {"status": "success", "result": result}
    except OPCUAClientError as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture : {str(e)}")

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

    if not opc.is_connected:
        connected = await opc.connect()
        if not connected:
            raise HTTPException(status_code=500, detail="Échec de la connexion au serveur OPC UA")

    node_id = "ns=4;s=RoleUser"  # À adapter selon ton serveur OPC UA
    opcua_result = await opc.write_node_value(node_id, role)
    success = opcua_result.get(node_id, False)


    # Retour JSON à la webvisu
    return {"tag_rfid": tag_request.tag_rfid, "role": role, "opcua_written": success}

    

@app.post("/api/opcua/subscribe")
async def subscribe_to_nodes(node_ids: List[str]):
    """
    S'abonne aux changements de données des nœuds spécifiés.

    :param node_ids: Liste des identifiants des nœuds à surveiller.
    :return: Message de confirmation.
    """
    if not opc.is_connected():
        raise HTTPException(status_code=500, detail="Client OPC UA non connecté")

    def callback(node_id, value):
        print(f"Changement détecté sur {node_id}: {value}")

    try:
        await opc.subscribe(node_ids, callback)
        return {"message": "Subscription réussie"}
    except OPCUAClientError as e:
        raise HTTPException(status_code=500, detail=str(e))





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