import { markRaw } from "vue";
import { icons } from "lucide-vue-next";
import CrmApp from "@/modules/crm/CrmApp.vue";

export const apps = [
  {
    id: "crm",
    title: "CRM",
    icons: markRaw(icons.Users),
    component:markRaw(CrmApp),
    window:{
      width: 1100,
      height: 700
    }
  },
  // Weitere Apps können hier hinzugefügt werden
];
