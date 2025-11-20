import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import { router } from "./router/index.ts";
import { WorkmateAssets } from "./services/assets.ts";
import "./styles/tokens.css";
import "./style.css";

document
  .querySelector("link[rel='icon']")
  ?.setAttribute("href", WorkmateAssets.workmateFavicon);

createApp(App).use(router).mount("#app");
