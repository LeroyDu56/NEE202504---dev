<template>
  <div>
    <h2>Logs</h2>
    <table v-if="logs.length">
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
        <tr v-for="log in logs" :key="log.LogsId">
          <td>{{ log.LogsId }}</td>
          <td>{{ log.CodeLog }}</td>
          <td>{{ formatDate(log.Ts) }}</td>
          <td>{{ log.Source }}</td>
          <td>{{ log.RequestId || '-' }}</td>
          <td>{{ log.Message }}</td>
          <td>{{ log.Utilisateur || 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>Chargement des logs...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const logs = ref([])

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString()
}

async function fetchLogs() {
  try {
    const res = await fetch('/api/logs')  // adapte l'URL selon ton API
    if (!res.ok) throw new Error('Erreur lors du chargement des logs')
    logs.value = await res.json()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
}
th {
  background-color: #f4f4f4;
  text-align: left;
}
</style>
