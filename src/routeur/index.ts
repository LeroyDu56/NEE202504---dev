import { createRouter, createWebHistory } from "vue-router";

import Login from "../views/login.vue";
import Accueil from "../views/Acceuil.vue";
import Synoptique from "../views/Synoptique.vue";
import OF from "../views/OF.vue";

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/acceuil", name: "Accueuil", component: Accueil },
  { path: "/synoptique", name: "Synoptique", component: Synoptique },
  { path: "/of", name: "OF", component: OF },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
