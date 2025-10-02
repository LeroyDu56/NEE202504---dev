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

      <!-- ✅ Affichage du badge scanné brut -->
      <p v-if="lastBadge" class="badge-display">
        Badge scanné (brut) : {{ lastBadge }}
      </p>

      <!-- ✅ Message de connexion -->
      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { loginWithBadge } from "@/services/api"; // 👈 appel backend
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const badgeId = ref("");
const lastBadge = ref(""); // garde la valeur brute scannée
const badgeInput = ref<HTMLInputElement | null>(null);
const message = ref("");

// ✅ Fonction de conversion ASCII → Hex
function asciiToHex(str: string): string {
  const encoder = new TextEncoder(); // encode en UTF-8
  const bytes = encoder.encode(str); // Uint8Array des octets
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();
}

// ✅ Dès que Entrée est pressé → connexion via API
async function onEnter() {
  if (!badgeId.value.trim()) return;

  lastBadge.value = badgeId.value; // garde le brut pour affichage
  const convertedBadge = asciiToHex(badgeId.value); // conversion avant envoi

  message.value = "Vérification en cours...";
  console.log("Badge scanné brut :", badgeId.value);
  console.log("Badge converti (hex) :", convertedBadge);

  try {
    const res = await loginWithBadge(convertedBadge);

    if (res.data && res.data.username) {
      message.value = `Bienvenue ${res.data.username} ! (Badge ${convertedBadge})`;
      setTimeout(() => {
        router.push("/OF");
      }, 800);
    } else {
      message.value = `Badge ${convertedBadge} non reconnu ❌`;
      console.warn("Badge rejeté :", convertedBadge);
    }
  } catch (err) {
    console.error("Erreur auth badge:", err);
    message.value = `Échec de l’authentification pour le badge ${convertedBadge} ❌`;
  } finally {
    badgeId.value = ""; // reset du champ de saisie
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
/* ✅ Styles généraux */
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

/* ✅ Nouveau style pour afficher le badge */
.badge-display {
  margin-top: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #e67e22;
}

.message {
  margin-top: 15px;
  color: #42b983;
  font-weight: 600;
  font-size: 14px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
