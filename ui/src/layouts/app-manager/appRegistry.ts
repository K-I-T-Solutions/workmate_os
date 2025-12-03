import { icons } from "lucide-vue-next";

export const apps = [
  {
    id: "crm",
    title: "CRM",
    icons: {
      default: icons.Users,
    },
    startRoute: "/app/crm/customers/",
    window:{
      width: 1100,
      height: 700
    }
  },
  // Weitere Apps können hier hinzugefügt werden
];
