<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Poste de contrôle ligne PCB</h1>
      <p class="subtitle">Veuillez scanner votre badge RFID</p>

      <!-- ✅ Image illustrant le scan -->
      <img src="/scan.png" alt="Scanner badge" class="scan-img" />

      <!-- ✅ Zone de saisie décalée hors écran -->
      <input
        type="text"
        v-model="badgeId"
        ref="badgeInput"
        @keydown.enter="onEnter"
        placeholder="Passez votre badge"
        class="hidden-input"
      />

      <!-- Message de connexion -->
      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { loginWithBadge } from "@/services/api"; // 👈 appel backend

const router = useRouter();
const badgeId = ref("");
const badgeInput = ref<HTMLInputElement | null>(null);
const message = ref("");

// ✅ Dès que Entrée est pressé → connexion via API
async function onEnter() {
  if (!badgeId.value.trim()) return;

  message.value = "Vérification en cours...";
  console.log("Badge scanné :", badgeId.value);

  try {
    const res = await loginWithBadge(badgeId.value);

    // si backend renvoie un user (ex: { username: "Paul" })
    if (res.data && res.data.username) {
      message.value = `Bienvenue ${res.data.username} !`;
      setTimeout(() => {
        router.push("/OF"); // redirection page OF
      }, 800);
    } else {
      message.value = "Badge non reconnu ❌";
    }
  } catch (err) {
    console.error("Erreur auth badge:", err);
    message.value = "Échec de l’authentification ❌";
  } finally {
    badgeId.value = ""; // reset
  }
}

// ✅ Focus automatique au montage et maintien du focus
const keepFocus = () => badgeInput.value?.focus();

onMounted(() => {
  keepFocus();
  window.addEventListener("click", keepFocus);
});

onBeforeUnmount(() => {
  window.removeEventListener("click", keepFocus);
});
</script>

<style scoped>
/* ✅ Styles identiques */
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #ecf0f3;
  font-family: "Segoe UI", sans-serif;
}

.login-card {
  background: #fff;
  padding: 30px 35px;
  border-radius: 14px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  text-align: center;
  width: 100%;
  max-width: 420px;
  animation: fadeIn 0.6s ease-in-out;
}

.login-card h1 {
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 26px;
}

.scan-img {
  width: 200px;
  margin-bottom: 25px;
  animation: pulse 1.5s infinite;
}

.subtitle {
  font-size: 15px;
  color: #444;
  margin-bottom: 20px;
}

.hidden-input {
  position: absolute;
  left: -9999px;
  top: 0;
  height: 1px;
  width: 1px;
  border: none;
  outline: none;
}

.message {
  margin-top: 15px;
  color: #42b983;
  font-weight: 600;
  font-size: 14px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
