<template>
  <div>
    <h1>Authentification utilisateurs</h1>
    <input 
      v-model="username" 
      type="text" 
      placeholder="Badge RFID" 
      autofocus
    />
    <br />
    <button @click="handleLogin">Connexion</button>
    <button @click="goAccueil">Shunt Authentification</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { login } from "@/services/api";

const router = useRouter();
const username = ref("");

// Fonction login
async function handleLogin() {
  try {
    const response = await login(username.value);
    if (response.data.success) {
      // Authentification OK → on va à l’accueil
      router.push("/accueil");
    } else {
      alert("Authentification échouée !");
    }
  } catch (err) {
    console.error("Erreur API:", err);
    alert("Erreur lors de l'authentification.");
  }
}

// Shunt
function goAccueil() {
  router.push("/accueil");
}
</script>