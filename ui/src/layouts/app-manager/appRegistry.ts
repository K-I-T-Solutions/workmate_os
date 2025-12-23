import { markRaw } from "vue";
import { icons } from "lucide-vue-next";
import CrmApp from "@/modules/crm/CrmApp.vue";
import InvoicesApp from "@/modules/invoices/InvoicesApp.vue";

export const apps = [
  {
    id: "crm",
    title: "Kunden",
    icons: markRaw(icons.Users),
    component:markRaw(CrmApp),
    window:{
      width: 1100,
      height: 700
    }
  },
  {
    id: "invoices",
    title: "Rechnungen",
    icons: markRaw(icons.FileText),
    component: markRaw(InvoicesApp),
    window: {
      width: 1200,
      height: 800
    }
  },
  // Weitere Apps können hier hinzugefügt werden
];
