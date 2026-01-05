import { createApp } from "vue";
import { createPinia } from "pinia";
import "./style.css";
import App from "./App.vue";
import { router } from "./router/index.ts";
import { WorkmateAssets } from "./services/assets.ts";
import "./styles/tokens.css";
import "./styles/mobile-utilities.css";


// Set Favicon
const faviconLink = document.querySelector("link[rel='icon']") || document.createElement('link');
faviconLink.setAttribute('rel', 'icon');
faviconLink.setAttribute('href', WorkmateAssets.workmateFavicon);
if (!document.querySelector("link[rel='icon']")) {
  document.head.appendChild(faviconLink);
}

const pinia = createPinia();

createApp(App)
  .use(pinia)
  .use(router)
  .mount("#app");
