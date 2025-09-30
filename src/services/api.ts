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
  const response: AxiosResponse<any[]> = await api.get("/of");

  return response.data.map((of: any) => ({
    id: String(of.id),
    provenance: "ERP",
    of: of.name,
    reference: of.origin,
    codeProduit: of.product_id?.[1] ?? "N/A",
    quantite: of.product_qty,
    datePlanifiee: of.date_planned_start?.split(" ")[0] ?? "",
    statut:
      of.state === "confirmed"
        ? "en_attente"
        : of.state === "progress"
        ? "en_cours"
        : of.state === "done"
        ? "termine"
        : "inconnu",
  }));
}

//======================================================================================
//----------------------------- Récupérer valeurs OPC-UA -------------------------------
//======================================================================================
export async function fetchOpcuaValues() {
  const response: AxiosResponse<any> = await axios.get("http://localhost:8000/opcua");

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
  const response: AxiosResponse<any[]> = await axios.get("http://localhost:8000/logs");

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
  const response: AxiosResponse<any> = await api.post("/of", data);
  return response.data;
}

//======================================================================================
//------------------------------------- Lancer un OF -----------------------------------
//======================================================================================
export async function launchOF(ofId: string): Promise<any> {
  const response: AxiosResponse<any> = await api.post(`/of/${ofId}/launch`);
  return response.data;
}

//======================================================================================
//------------------------------------ Supprimer un OF ---------------------------------
//======================================================================================
export async function deleteOF(ofId: string): Promise<any> {
  const response: AxiosResponse<any> = await api.delete(`/of/${ofId}`);
  return response.data;
}

//======================================================================================
//--------------------------- Authentification par badge RFID --------------------------
//======================================================================================
export async function loginWithBadge(badgeId: string) {
  console.log("💳 Envoi du badge au backend :", badgeId);

  // 🔧 décommente quand ton backend sera prêt
  // const response = await api.post("/login/rfid", { badgeId });
  // return response;

  // Simulation locale
  return Promise.resolve({
    data: {
      success: true,
      username: "Utilisateur Test",
      badgeId,
    },
  });
}

//======================================================================================
//------------------------------------ Export par défaut -------------------------------
//======================================================================================
export default api;
