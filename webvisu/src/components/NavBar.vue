<template>
  <!-- ✅ Navbar affichée uniquement si on n’est pas sur la page login -->
  <nav v-if="route.path !== '/'" class="navbar">
    <h1>Ligne PCB</h1>
    <div class="nav-links">
      <RouterLink to="/synoptique">Synoptique</RouterLink>
      <RouterLink to="/of">Ordres de fabrication</RouterLink>
      <RouterLink to="/log">Log</RouterLink> <!-- Bouton ajouté -->
      <RouterLink to="/">Déconnexion</RouterLink>
    </div>
  </nav>
</template>


<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f4f4f4;
  padding: 10px 20px; /* ✅ plus d’espace autour */
}

.navbar h1 {
  font-size: 26px; /* ✅ titre plus grand */
  margin: 0;
  color: #000; /* noir bien lisible */
  font-weight: 800; /* ✅ encore plus marqué */
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 15px; /* ✅ espace plus large entre les liens */
  font-size: 16px; /* ✅ texte des liens plus grand */
}

.nav-links a {
  text-decoration: none;
  color: #333;
  padding: 6px 10px; /* ✅ plus de surface cliquable */
  border-radius: 5px;
  font-weight: 600; /* ✅ un peu plus visible */
}

.nav-links a:hover {
  background: #ddd;
}
</style>
