<template>
  <div>
    <h2>Listes d'ordres de fabrication</h2>

    <table border="1">
      <thead>
        <tr>
          <th>Sélection</th>
          <th>Provenance</th>
          <th>OF</th>
          <th>Références</th>
          <th>Code produit</th>
          <th>Quantité</th>
          <th>Date planifiée</th>
          <th>Statut</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(of, index) in ofList" :key="of.id || index">
          <td>
            <input
              type="radio"
              name="ofSelect"
              @change="selectOF(of)"
            />
          </td>
          <td>{{ of.provenance }}</td>
          <td>{{ of.of }}</td>
          <td>{{ of.reference }}</td>
          <td>{{ of.codeProduit }}</td>
          <td>{{ of.quantite }}</td>
          <td>{{ of.datePlanifiee }}</td>
          <td>{{ of.statut }}</td>
        </tr>
      </tbody>
    </table>

    <div>
      <p>OF sélectionné : {{ selectedOF?.of || "Aucun" }}</p>
      <button @click="handleCreateOF">Créer un OF</button>
      <button @click="handleLaunchOF">Lancer un OF</button>
      <button @click="handleDeleteOF">Supprimer un OF</button>
    </div>

    <div style="margin-top: 20px;">
      <button @click="goBack">Retour à l'accueil</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getOFs, createOF, launchOF, deleteOF } from "@/services/api";

interface OF {
  id: string;
  provenance: string;
  of: string;
  reference: string;
  codeProduit: string;
  quantite: number;
  datePlanifiee: string;
  statut: string;
}

const router = useRouter();
const ofList = ref<OF[]>([]);
const selectedOF = ref<OF | null>(null);

onMounted(async () => {
  try {
    const response = await getOFs();
    ofList.value = response.data;
  } catch (err) {
    console.error("Erreur API :", err);
  }
});

function selectOF(of: OF) {
  selectedOF.value = of;
}

async function handleCreateOF() {
  try {
    const response = await createOF({
      provenance: "Atelier A",
      reference: "REF_NEW",
      codeProduit: "CP_NEW",
      quantite: 50,
      datePlanifiee: "2025-09-30",
    });
    ofList.value.push(response.data);
  } catch (err) {
    console.error("Erreur création OF :", err);
  }
}

async function handleLaunchOF() {
  if (!selectedOF.value) {
    alert("Veuillez sélectionner un OF");
    return;
  }
  try {
    await launchOF(selectedOF.value.id);
    alert("OF lancé !");
  } catch (err) {
    console.error("Erreur lancement OF :", err);
  }
}

async function handleDeleteOF() {
  if (!selectedOF.value) {
    alert("Veuillez sélectionner un OF local");
    return;
  }
  try {
    await deleteOF(selectedOF.value.id);
    ofList.value = ofList.value.filter(of => of.id !== selectedOF.value!.id);
    selectedOF.value = null;
  } catch (err) {
    console.error("Erreur suppression OF :", err);
  }
}

function goBack() {
  router.push("/acceuil");
}
</script>
