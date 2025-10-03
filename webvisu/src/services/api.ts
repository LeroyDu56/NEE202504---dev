// src/services/api.ts
import axios, { AxiosResponse } from "axios";

//======================================================================================
//---------------------------------- Configuration Axios --------------------------------
//======================================================================================
const api = axios.create({
  baseURL: "http://localhost:8000", // 🔧 adapte si ton backend change
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});


//======================================================================================
//----------------------------------- Demander OF ERP ----------------------------------
//======================================================================================
export async function getOFs(): Promise<any[]> {
  const response: AxiosResponse<any[]> = await api.get("/api/erp/ofs");

  return response.data.map((of: any) => {
    // Sépare la chaîne "25: Assemblage"
    const [codeProduit, reference] = of.bom_ref
      ? of.bom_ref.split(":").map((s: string) => s.trim())
      : ["N/A", "N/A"];

    return {
      id: String(of.id),             // ✅ ID réel de l'OF
      of: of.name,                   // N° OF (ex: "WH/MO/00034")
      reference,                     // ex: "Assemblage"
      codeProduit,                   // ex: "25"
      quantite: of.product_qty,
      datePlanifiee: of.date_planned_start?.split("T")[0] ?? "",
      statut:
        of.state === "confirmed"
          ? "en_attente"
          : of.state === "progress"
          ? "en_cours"
          : of.state === "done"
          ? "termine"
          : "inconnu",
    };
  });
}


//======================================================================================
//----------------------------- Récupérer valeurs OPC-UA -------------------------------
//======================================================================================
export async function fetchOpcuaValues() {
  const response: AxiosResponse<any> = await axios.get(
    "http://localhost:8000/opcua"
  );

  // Exemple de réponse JSON attendue :
  // {
  //   "AutWriteOF": true,
  //   "NumeroOF": "OF-2025-001",
  //   "RecetteOF": "Recette-A",
  //   "QuantiteOF": 120,
  //   "RoleUser": "OperateurA"
  // }

  return {
    AutWriteOF: response.data.AutWriteOF,
    NumeroOF: response.data.NumeroOF,
    RecetteOF: response.data.RecetteOF,
    QuantiteOF: response.data.QuantiteOF,
    RoleUser: response.data.RoleUser,
  };
}

//======================================================================================
//------------------------------- Récupérer les logs -----------------------------------
//======================================================================================
export async function fetchLogsSimu() {
  const response: AxiosResponse<any[]> = await axios.get(
    "http://localhost:8000/logs"
  );

  // Exemple de réponse JSON attendue :
  // [
  //   {
  //     "LogsId": 1,
  //     "CodeLog": 100,
  //     "Ts": "2025-09-30T09:15:00Z",
  //     "Source": "App",
  //     "RequestId": "abc-123",
  //     "Message": "Connexion réussie",
  //     "Utilisateur": "OperateurA"
  //   }
  // ]

  return response.data.map((log: any) => ({
    LogsId: log.LogsId,
    CodeLog: log.CodeLog,
    Ts: log.Ts,
    Source: log.Source,
    RequestId: log.RequestId,
    Message: log.Message,
    Utilisateur: log.Utilisateur,
  }));
}

//======================================================================================
//---------------------------- Créer un OF stocké dans MySQL ---------------------------
//======================================================================================
export async function createOF(data: {
  provenance: string;
  reference: string;
  codeProduit: string;
  quantite: number;
  datePlanifiee: string;
}): Promise<any> {
  const response: AxiosResponse<any> = await api.post("/api/of", data);
  return response.data;
}

//======================================================================================
//------------------------------------- Lancer un OF -----------------------------------
//======================================================================================
export async function launchOF(of: {
  id: string;          // ✅ ajouter id
  of: string;
  codeProduit: string;
  quantite: number;
}): Promise<any> {
  // ✅ Utiliser directement l'id comme NumeroOF
  const numeroOF = parseInt(of.id, 10);

  // ✅ Convertir le code produit en entier
  const codeProduitNum = parseInt(of.codeProduit, 10);

  // ⚡ Construction du JSON OPC-UA
  const payload = {
    writes: [
      {
        node_name:
          "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.NumeroOF",
        value: numeroOF, // 🔥 envoie bien l'id ici
        variant_type: "UInt16",
      },
      {
        node_name:
          "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.RecetteOF",
        value: codeProduitNum,
        variant_type: "UInt16",
      },
      {
        node_name:
          "ns=4;s=|var|WAGO 750-8302 PFC300 2ETH RS.Application.OPCUA.Ilot_1.QuantiteOF",
        value: Number(of.quantite),
        variant_type: "UInt16",
      },
    ],
  };

  console.log("📤 Payload envoyé au backend :", payload);

  const response: AxiosResponse<any> = await api.post(
    "/api/opcua/write-of",
    payload
  );
  return response.data;
}

//======================================================================================
//------------------------------------ Supprimer un OF ---------------------------------
//======================================================================================
export async function deleteOF(ofId: string): Promise<any> {
  const response: AxiosResponse<any> = await api.delete(`/api/of/${ofId}`);
  return response.data;
}

//======================================================================================
//--------------------------- Authentification par badge RFID --------------------------
//======================================================================================
export async function loginWithBadge(convertedBadge: string) {
  // ⚡ On construit le JSON avec le badge converti
  const payload = { badgeID: convertedBadge }; // <-- corrigé

  console.log(
    "📤 Payload JSON envoyé au backend :",
    JSON.stringify(payload, null, 2)
  );

  // Envoi vers ton API REST
  const response = await api.post("/api/bdd/get_role", payload, {
    headers: {
      "Content-Type": "application/json", // assure que c’est du JSON
    },
  });

  // On affiche aussi la réponse du backend
  console.log("🔑 Réponse du backend :", response.data);

  return response;
}
