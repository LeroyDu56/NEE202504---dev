<template>
  <div class="synoptique-page">
    <h2>Vue synoptique de la ligne</h2>

    <div class="synoptique-container">
      <!-- ✅ Zone info gauche -->
      <div class="info-card card-left">
        <h3>OF en cours</h3>
        <p><strong>N° :</strong> —</p>
        <p><strong>Code produit :</strong> —</p>
        <p><strong>Statut :</strong> —</p>
      </div>

      <!-- ✅ Zone info milieu -->
      <div class="info-card card-middle">
        <h3>OF en cours</h3>
        <p><strong>N° :</strong> —</p>
        <p><strong>Code produit :</strong> —</p>
        <p><strong>Statut :</strong> —</p>
      </div>

      <!-- ✅ Zone info droite -->
      <div class="info-card card-right">
        <h3>OF en cours</h3>
        <p><strong>N° :</strong> —</p>
        <p><strong>Code produit :</strong> —</p>
        <p><strong>Statut :</strong> —</p>
      </div>

      <!-- ✅ Image grande -->
      <img src="/ligne3sf.png" alt="Synoptique" class="synoptique-image" />
    </div>
  </div>
</template>

<script setup lang="ts">
// aucune donnée encore → on laisse vide
</script>

<style scoped>
.synoptique-page {
  text-align: center;
  padding: 20px;
}

/* Titre */
.synoptique-page h2 {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 20px;
}

/* Conteneur */
.synoptique-container {
  position: relative;
  display: inline-block;
  max-width: 95%;
}

/* Image grande */
.synoptique-image {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}

/* Cartes infos intégrées */
.info-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.9);
  padding: 12px 16px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  width: 200px;
  text-align: left;
  font-size: 14px;
  backdrop-filter: blur(4px);
}

.info-card h3 {
  margin: 0 0 6px;
  font-size: 16px;
  color: #2c3e50;
}

.info-card p {
  margin: 4px 0;
  font-size: 13px;
}

/* Placement ajusté */
.card-left {
  top: 40%;   /* ⬆ un peu plus haut */
  left: 3%;  /* ⬅ plus à gauche */
}

.card-middle {
  top: 15%;   /* ⬆ un peu plus haut */
  left: 50%;
  transform: translateX(-50%);
}

.card-right {
  bottom: 42%; /* ⬆ plus haut */
  right: 6.5%;  /* ➡ plus à droite */
}
</style>
