<template>
  <div class="log-page">
    <!-- En-tête -->
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
import { fetchLogsSimu } from '@/services/api'; // ✅ chemin corrigé

// Interface de log
interface Log {
  LogsId: number;
  CodeLog: number;
  Ts: string;
  Source: string;
  RequestId?: string | null;
  Message: string;
  Utilisateur?: string;
}

// Variables réactives
const logs = ref<Log[]>([]);
const isLoading = ref(false);
let refreshTimer: number | null = null;

// Fonction pour formater la date/heure lisiblement
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString();
}

// Fonction pour récupérer les logs via API simulée
async function fetchLogs() {
  isLoading.value = true;
  try {
    logs.value = await fetchLogsSimu(); // ✅ simulation locale
  } catch (error) {
    console.error('Erreur fetch logs:', error);
    logs.value = []; // on vide en cas d'erreur
  } finally {
    isLoading.value = false;
  }
}

// Appel initial au montage + actualisation toutes les 10 secondes
onMounted(() => {
  fetchLogs();
  refreshTimer = window.setInterval(fetchLogs, 10000);
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

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.table-container {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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
  text-align: left;
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
