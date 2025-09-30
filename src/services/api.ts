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
//------------------------------- Récupérer les logs -----------------------------------
//======================================================================================
export async function fetchLogsSimu() {
  await new Promise(resolve => setTimeout(resolve, 500)); // simulation délai
  return [
    {
      LogsId: 1,
      CodeLog: 100,
      Ts: "2025-09-30T09:15:00Z",
      Source: "App",
      RequestId: "abc-123",
      Message: "Connexion réussie",
      Utilisateur: "OperateurA",
    },
    {
      LogsId: 2,
      CodeLog: 200,
      Ts: "2025-09-30T09:20:00Z",
      Source: "Serveur API",
      RequestId: "def-456",
      Message: "Création OF",
      Utilisateur: "OperateurB",
    },
    {
      LogsId: 3,
      CodeLog: 300,
      Ts: "2025-09-30T09:30:00Z",
      Source: "Machine X",
      RequestId: null,
      Message: "OF terminé",
      Utilisateur: "OperateurC",
    },
  ];
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
