<template>
  <div>
    <h1>Ligne de production PCB</h1>
    <img src="/ligne2sf.png" alt="Ligne de production" width="400" />

    <div>
      <button @click="goSynoptique">Synoptique</button>
      <button @click="goOF">Ordres de fabrication</button>
    </div>

    <!-- ✅ Bouton de déconnexion -->
    <div style="margin-top: 20px;">
      <button @click="logout">Déconnexion</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();

function goSynoptique() {
  router.push("/synoptique");
}

function goOF() {
  router.push("/of");
}

function logout() {
  router.push("/"); // renvoie vers la page login
}
</script>
