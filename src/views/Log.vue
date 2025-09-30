<template>
  <div class="log-page">
    <!-- Section OPC-UA -->
    <div class="opcua-container">
      <h3>⚙️ Valeurs OPC-UA (Simulation)</h3>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>AutWriteOF</th>
              <th>NumeroOF</th>
              <th>RecetteOF</th>
              <th>QuantiteOF</th>
              <th>RoleUser</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ opcua?.AutWriteOF ?? '-' }}</td>
              <td>{{ opcua?.NumeroOF ?? '-' }}</td>
              <td>{{ opcua?.RecetteOF ?? '-' }}</td>
              <td>{{ opcua?.QuantiteOF ?? '-' }}</td>
              <td>{{ opcua?.RoleUser ?? '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- En-tête des journaux -->
    <div class="page-header">
      <h2>📄 Journaux d'activité (Logs)</h2>
    </div>

    <!-- Tableau des logs -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Code Log</th>
            <th>Date / Heure</th>
            <th>Source</th>
            <th>Request ID</th>
            <th>Message</th>
            <th>Utilisateur</th>
          </tr>
        </thead>
        <tbody>
          <!-- Affichage des logs -->
          <tr v-for="log in logs" :key="log.LogsId">
            <td>{{ log.LogsId }}</td>
            <td><span class="badge code">{{ log.CodeLog }}</span></td>
            <td>{{ formatDate(log.Ts) }}</td>
            <td>{{ log.Source }}</td>
            <td>{{ log.RequestId || '-' }}</td>
            <td>{{ log.Message }}</td>
            <td>{{ log.Utilisateur || 'N/A' }}</td>
          </tr>

          <!-- Message de chargement -->
          <tr v-if="isLoading">
            <td colspan="7" class="loading-msg">Chargement des logs...</td>
          </tr>

          <!-- Message si aucun log -->
          <tr v-else-if="!isLoading && logs.length === 0">
            <td colspan="7" class="loading-msg">Aucun log trouvé.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { fetchLogsSimu, fetchOpcuaValues } from '@/services/api'; // ✅ route API

// Interfaces
interface Log {
  LogsId: number;
  CodeLog: number;
  Ts: string;
  Source: string;
  RequestId?: string | null;
  Message: string;
  Utilisateur?: string;
}

interface OpcuaValues {
  AutWriteOF: boolean;
  NumeroOF: string;
  RecetteOF: string;
  QuantiteOF: number;
  RoleUser: string;
}

// Variables réactives
const logs = ref<Log[]>([]);
const isLoading = ref(false);
const opcua = ref<OpcuaValues | null>(null);
let refreshTimer: number | null = null;

// Fonction pour formater la date/heure lisiblement
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString();
}

// Fonction pour récupérer les logs + OPC-UA
async function fetchData() {
  isLoading.value = true;
  try {
    logs.value = await fetchLogsSimu();
    opcua.value = await fetchOpcuaValues();
  } catch (error) {
    console.error('Erreur fetch logs/opcua:', error);
    logs.value = [];
    opcua.value = null;
  } finally {
    isLoading.value = false;
  }
}

// Appel initial au montage + actualisation toutes les 10 secondes
onMounted(() => {
  fetchData();
  refreshTimer = window.setInterval(fetchData, 10000);
});

// Nettoyage à la destruction du composant
onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer);
});
</script>

<style scoped>
.log-page {
  padding: 20px;
}

/* Section OPC-UA */
.opcua-container {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 12px;
  background: #f5f9ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.opcua-container h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

/* Styles des tableaux (logs et OPC-UA) */
.table-container {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}

thead {
  background: linear-gradient(135deg, #2c3e50, #34495e);
  color: white;
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

/* Badge pour Code Log */
.badge.code {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: bold;
  background-color: #3498db;
  color: white;
}

.loading-msg {
  text-align: center;
  color: #888;
  font-style: italic;
}
</style>
