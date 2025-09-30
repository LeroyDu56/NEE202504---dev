import { createRouter, createWebHistory } from "vue-router";

import login from "../views/login.vue";
import Synoptique from "../views/Synoptique.vue";
import OF from "../views/OF.vue";
import Log from "../views/Log.vue";

const routes = [
  { path: "/", name: "login", component: login },
  { path: "/synoptique", name: "Synoptique", component: Synoptique },
  { path: "/of", name: "OF", component: OF },
  { path: "/log", name: "Log", component: Log },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
