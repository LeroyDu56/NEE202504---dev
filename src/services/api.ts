import axios, { AxiosResponse } from "axios";

//======================================================================================
//---------------------------------- Configuration Axios --------------------------------
//======================================================================================
const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});



//======================================================================================
//----------------------------------- Demander OF ERP ----------------------------------
//======================================================================================
export async function getOFs(): Promise<any[]> {
  /*
  // 🔹 Appel réel API (backend)
  const response: AxiosResponse<any[]> = await api.get("/of");
  return response.data;
  */

  // 🔹 Simulation brute d'une réponse Odoo (mock)
  const odooResponse = [
    {
      id: 101,
      name: "OF2025-001", // Numéro OF
      origin: "REF-12345", // Référence
      product_id: [1, "PCB-001"], // [id, code produit]
      product_qty: 150, // Quantité
      date_planned_start: "2025-09-30 08:00:00",
      state: "confirmed", // en_attente
    },
    {
      id: 102,
      name: "OF2025-002",
      origin: "REF-98765",
      product_id: [2, "PCB-002"],
      product_qty: 300,
      date_planned_start: "2025-10-05 14:00:00",
      state: "progress", // en_cours
    },
    {
      id: 103,
      name: "OF2025-003",
      origin: "REF-56789",
      product_id: [3, "PCB-003"],
      product_qty: 500,
      date_planned_start: "2025-10-15 09:30:00",
      state: "done", // terminé
    },
  ];

  // 🔹 Conversion → format attendu par ton template Vue
  const mapped = odooResponse.map(of => ({
    id: String(of.id),
    provenance: "ERP",
    of: of.name,
    reference: of.origin,
    codeProduit: of.product_id[1],
    quantite: of.product_qty,
    datePlanifiee: of.date_planned_start.split(" ")[0], // on garde que la date
    statut:
      of.state === "confirmed"
        ? "en_attente"
        : of.state === "progress"
        ? "en_cours"
        : of.state === "done"
        ? "termine"
        : "inconnu",
  }));

  return Promise.resolve(mapped);
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

  // return api.post("/login/rfid", { badgeId });


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
