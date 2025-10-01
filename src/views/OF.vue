<template>
  <div class="of-page">
    <!-- ✅ En-tête avec titre, OF sélectionné et actions -->
    <div class="page-header">
      <h2>📋 Listes d'ordres de fabrication</h2>
      <div class="header-actions">
        <p class="selected-of">
          <strong>OF sélectionné :</strong>
          <span v-if="selectedOF">{{ selectedOF.of }}</span>
          <span v-else>Aucun</span>
          <span
            v-if="selectedOF"
            class="badge"
            :class="selectedOF.statut.toLowerCase()"
          >
            {{ selectedOF.statut }}
          </span>
        </p>
        <button class="primary" @click="openModal">➕ Créer un OF</button>
        <button class="success" @click="handleLaunchOF">🚀 Lancer l'OF (ERP)</button>
        <!-- ✅ Supprimer uniquement si OF opérateur -->
        <button
          class="danger"
          @click="handleDeleteSelectedOF(selectedOF!)"
          :disabled="!selectedOF || selectedOF.provenance !== 'Opérateur'"
        >
          🗑 Supprimer l'OF
        </button>
      </div>
    </div>

    <!-- ✅ Tableau OF -->
    <div class="table-container">
      <table>
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
          <tr
            v-for="(of, index) in ofList"
            :key="of.id || index"
            :class="{ selected: selectedOF === of }"
          >
            <td>
              <input type="radio" name="ofSelect" @change="selectOF(of)" />
            </td>
            <td>{{ of.provenance }}</td>
            <td>{{ of.of }}</td>
            <td>{{ of.reference }}</td>
            <td>{{ of.codeProduit }}</td>
            <td>{{ of.quantite }}</td>
            <td>{{ of.datePlanifiee }}</td>
            <td>
              <span class="badge" :class="of.statut.toLowerCase()">
                {{ of.statut }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ✅ Modal création OF -->
    <dialog ref="modal">
      <form method="dialog" class="modal-form" @submit.prevent="saveNewOF">
        <h3>➕ Créer un nouvel OF</h3>

        <label>N° OF</label>
        <input v-model="newOF.of" required />

        <label>Référence</label>
        <input v-model="newOF.reference" required />

        <label>Code produit</label>
        <input v-model="newOF.codeProduit" required />

        <label>Quantité</label>
        <input type="number" v-model.number="newOF.quantite" required />

        <label>Date planifiée</label>
        <input type="date" v-model="newOF.datePlanifiee" required />

        <div class="modal-actions">
          <button type="submit" class="primary"> Enregistrer</button>
          <button type="button" class="danger" @click="closeModal"> Annuler</button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { getOFs, createOF, launchOF } from "@/services/api";

// ✅ Typage OF
interface OF {
  id?: string;
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
const modal = ref<HTMLDialogElement | null>(null);
let refreshTimer: number | null = null;

// ✅ modèle pour un nouveau OF
const newOF = ref<OF>({
  provenance: "Opérateur",
  of: "",
  reference: "",
  codeProduit: "",
  quantite: 0,
  datePlanifiee: "",
  statut: "en_attente",
});

// ✅ Fonction pour charger les OF depuis l’ERP
async function loadOFs() {
  try {
    ofList.value = await getOFs();
  } catch (err) {
    console.error("❌ Erreur lors de la récupération des OFs:", err);
  }
}

// ✅ Récupération des OFs au montage + rafraîchissement auto
onMounted(async () => {
  await loadOFs();
  refreshTimer = window.setInterval(loadOFs, 10000); // 🔄 toutes les 10 secondes
});

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer);
});

// ✅ Sélectionner un OF
function selectOF(of: OF) {
  selectedOF.value = of;
}

// ✅ Ouvrir modal
function openModal() {
  modal.value?.showModal();
}

// ✅ Fermer modal
function closeModal() {
  modal.value?.close();
}

// ✅ Sauvegarder un OF
async function saveNewOF() {
  try {
    const payload = { ...newOF.value, statut: "en_attente" };
    const created = await createOF(payload);
    ofList.value.push(created);
    alert("OF créé avec succès !");
    closeModal();

    // reset du formulaire
    newOF.value = {
      provenance: "Opérateur",
      of: "",
      reference: "",
      codeProduit: "",
      quantite: 0,
      datePlanifiee: "",
      statut: "en_attente",
    };
  } catch (err) {
    console.error("Erreur création OF :", err);
    alert("Impossible de créer l'OF.");
  }
}

// ✅ Supprimer un OF (uniquement si opérateur)
async function handleDeleteSelectedOF(of: OF) {
  if (!of || of.provenance !== "Opérateur") {
    alert("Impossible de supprimer un OF importé depuis l'ERP.");
    return;
  }
  ofList.value = ofList.value.filter(item => item !== of);
  if (selectedOF.value === of) selectedOF.value = null;
  alert("OF supprimé (local uniquement).");
}

// ✅ Lancer un OF ERP
async function handleLaunchOF() {
  if (!selectedOF.value) {
    alert("Veuillez sélectionner un OF");
    return;
  }
  try {
    await launchOF({
      of: selectedOF.value.of,
      codeProduit: selectedOF.value.codeProduit,
      quantite: selectedOF.value.quantite,
    });
    alert("OF lancé avec succès !");
  } catch (err) {
    console.error("Erreur lancement OF :", err);
    alert("Impossible de lancer l'OF.");
  }
}

// ✅ Retour accueil
function goBack() {
  router.push("/accueil");
}
</script>

<style scoped>
/* ✅ Header aligné */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

/* ✅ OF sélectionné + boutons */
.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.selected-of {
  font-size: 15px;
  color: #2c3e50;
  background: #ecf0f1;
  padding: 6px 12px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.selected-of strong {
  margin-right: 6px;
}

/* ✅ Styles tableau */
.table-container {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}

thead {
  background: linear-gradient(135deg, #2c3e50, #34495e);
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

th, td {
  padding: 14px 12px;
  text-align: center;
}

tbody tr:nth-child(even) {
  background: #f9f9f9;
}

tbody tr:hover {
  background: #f1f7ff;
  transition: background 0.2s ease-in-out;
}

tbody tr.selected {
  background: #d6f5e3 !important;
}

/* ✅ Badges statut */
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  text-transform: capitalize;
  margin-left: 8px;
}

.badge.en_attente { background: #f39c12; }
.badge.en_cours { background: #3498db; }
.badge.termine { background: #2ecc71; }

/* ✅ Boutons */
button {
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

button.primary {
  background: #3498db;
  color: white;
}
button.primary:hover { background: #2980b9; transform: translateY(-2px); }
button.primary:active { transform: scale(0.97); }

button.success {
  background: #2ecc71;
  color: white;
}
button.success:hover { background: #27ae60; transform: translateY(-2px); }
button.success:active { transform: scale(0.97); }

button.danger {
  background: #e74c3c;
  color: white;
}
button.danger:hover { background: #c0392b; transform: translateY(-2px); }
button.danger:active { transform: scale(0.97); }

button.small {
  padding: 6px 12px;
  font-size: 13px;
}

/* ✅ Modal */
dialog {
  border: none;
  border-radius: 12px;
  padding: 24px;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.modal-form label {
  font-weight: 600;
  text-align: left;
  font-size: 14px;
  color: #2c3e50;
}

.modal-form input,
.modal-form select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
}

.modal-form input:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 4px rgba(52,152,219,0.4);
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}
</style>
