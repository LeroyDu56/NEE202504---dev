<template>
  <div>
    <h2>Vue synoptique de la ligne</h2>
    <img src="/ligne3sf.png" alt="Synoptique" width="500" />

    <div style="margin-top: 20px;">
      <button @click="goBack">Retour à l'accueil</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();

function goBack() {
  router.push("/acceuil");
}
</script>
