import { createApp } from "vue";
import App from "./App.vue";
import router from "./routeur";
import './assets/style.css';

const app = createApp(App);
app.use(router);
app.mount("#app");
