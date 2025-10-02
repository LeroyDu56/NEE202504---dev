import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.config.log_config import setup_logging
from api.schemas.schema import WriteData, WriteMultipleData, ReadResponse, ReadMultipleResponse, OF
from api.services.service_opcua import OPCUAClient, OPCUAClientError
from api.services.odoo_service import ERP
from api.services.bdd_service import Database
from api.schemas.user_schema import TagRequest, TagResponse
from sqlalchemy.orm import Session
from asyncua import ua
from dotenv import load_dotenv
import traceback
from typing import List, Dict
from contextlib import contextmanager
from config.log_config import setup_logging

load_dotenv()

app = FastAPI(title="API NEE202504")

logger = setup_logging("APIREST")

# --- Configuration MySQL ---
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),           # 'mysql' pour Docker, 127.0.0.1 hors Docker
    "user": os.getenv("MYSQL_USER", "admin"),
    "password": os.getenv("MYSQL_PASSWORD", "admin"),
    "database": os.getenv("MYSQL_DATABASE", "mydb"),
    "port": int(os.getenv("MYSQL_PORT", 3306))          # port par défaut 3306
}

# --- Configuration API ---
API_PORT = int(os.getenv("API_PORT", 3000))

# --- Configuration PostgreSQL (Odoo) ---
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "db"),
    "database": os.getenv("POSTGRES_DB", "postgres"),
    "user": os.getenv("POSTGRES_USER", "odoo"),
    "password": os.getenv("POSTGRES_PASSWORD", "odoo"),
    "port": int(os.getenv("POSTGRES_PORT", 5432))       # port par défaut 5432
}

# --- Initialisation des loggers ---
api_logger = setup_logging("api", logfile="logs/api.log", mysql_conf=MYSQL_CONFIG)
api_logger.info("API REST démarrée")

opcua_logger = setup_logging("opcua", logfile="logs/opcua.log", mysql_conf=MYSQL_CONFIG)
opcua_logger.info("Client OPCUA initialisé")

erp_logger = setup_logging("erp", logfile="logs/erp.log", mysql_conf=MYSQL_CONFIG)
erp_logger.info("ERP connecté")

mqtt_logger = setup_logging("mqtt", logfile="logs/mqtt.log", mysql_conf=MYSQL_CONFIG)
mqtt_logger.info("Client MQTT démarré")

# --- Middleware CORS pour FastAPI ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # À restreindre en production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

odoo = ERP(
    url=os.getenv("ODOO_URL", "http://10.10.0.10:9060"),
    database=os.getenv("ODOO_DB", "NEE"),
    username=os.getenv("ODOO_USER", "OperateurA@nee.com"),
    password=os.getenv("ODOO_PASSWORD", "nee25Aodoo!"),
)

# --- Base de données locale ---
bdd = Database()

# --- Client OPCUA ---
SERVER_URL = os.getenv("OPCUA_SERVER_URL", "opc.tcp://172.30.30.1:4840")
opc = OPCUAClient(SERVER_URL)
# Ta liste de nœuds comme tu avais
NODES_TO_READ = [
    "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.AutWriteOF",
    "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.NumeroOF",
    "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.RecetteOF",
    "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.QuantiteOF",
    "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.RoleUser"
]

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

@app.get("/opcua/opcuaconnect")
async def opcuaconnect():
    try:
        await opc.connect()
        logger.info("Client OPC UA connecté à l’API")
    except Exception as e:
        logger.error(f"Erreur connexion au startup : {e}")



@app.get("/odoo/connect")
def connect_odoo():
    """Teste la connexion avec l'ERP Odoo"""
    try:
        if odoo.connect():
            return {"status": "success", "uid": odoo.uid}
        else:
            raise HTTPException(status_code=401, detail="Échec de connexion à Odoo. Vérifie les identifiants ou la base.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/erp/ofs", response_model=List[OF], tags=["Ordre de Fabrication"])
async def get_ofs_endpoint():
    """
    Récupère la liste des ordres de fabrication depuis Odoo.
    Retourne :
    - Liste des OFs (avec leurs champs principaux)
    - Code 200 si succès
    - Code 500 si erreur
    """
    try:
        # Connexion à Odoo si nécessaire
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
    aut_write_value = await opc.read("ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.AutWriteOF")
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

@app.post("/api/bdd/get_role")
async def get_role(
    tag_request: TagRequest,
    session: Session = Depends(get_db_session_async)
):
    logger.info(f"Tag envoyé : {tag_request}")

    # 1️⃣ Vérifie la connexion à la BDD
    if not bdd.check_connection():
        if not bdd.reconnect():
            raise HTTPException(status_code=500, detail="Échec de la reconnexion à la base de données")

    # 2️⃣ Récupère le rôle depuis la BDD
    role = bdd.get_role_by_tag(session, tag_request.badgeID)
    logger.info(f"Rôle récupéré depuis BDD : {role}")

    # 3️⃣ Vérifie connexion OPC UA
    try:
        if opc.is_connected:
            try:
                await opc.client.nodes.server_state.read_value()
            except Exception:
                logger.warning("Session OPC UA cassée, on se déconnecte et on retente...")
                await opc.disconnect()
                connected = await opc.connect()
                if not connected:
                    raise HTTPException(status_code=500, detail="Échec de reconnexion OPC UA")
        else:
            connected = await opc.connect()
            if not connected:
                raise HTTPException(status_code=500, detail="Échec de la connexion au serveur OPC UA")
    except Exception as e:
        logger.error(f"Erreur OPC UA: {e}")
        raise HTTPException(status_code=500, detail="Problème de communication OPC UA")

    # 4️⃣ Écriture sur le serveur OPC UA
    node_id = "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.RoleUser"
    try:
        await opc.write(node_id, role, ua.VariantType.UInt16)
    except Exception as e:
        logger.error(f"Erreur écriture OPC UA: {e}")
        raise HTTPException(status_code=500, detail="Échec de l’écriture OPC UA")

    # 5️⃣ Retour JSON formaté comme demandé
    return {
        "success": True,
        "username": "utilisateurs",   # tu peux remplacer par le vrai nom si tu l’as
        "badgeId": tag_request.badgeID
    }

    

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