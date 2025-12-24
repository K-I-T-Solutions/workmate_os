import { markRaw } from "vue";
import { icons } from "lucide-vue-next";
import CrmApp from "@/modules/crm/CrmApp.vue";
import InvoicesApp from "@/modules/invoices/InvoicesApp.vue";
import ProjectsApp from "@/modules/projects/ProjectsApp.vue";
import TimeTrackingApp from "@/modules/time-tracking/TimeTrackingApp.vue";
import ExpensesApp from "@/modules/expenses/ExpensesApp.vue";
import FinanceApp from "@/modules/finance/FinanceApp.vue";

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
  {
    id: "projects",
    title: "Projekte",
    icons: markRaw(icons.Briefcase),
    component: markRaw(ProjectsApp),
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "time-tracking",
    title: "Zeiterfassung",
    icons: markRaw(icons.Clock),
    component: markRaw(TimeTrackingApp),
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "expenses",
    title: "Ausgaben",
    icons: markRaw(icons.Receipt),
    component: markRaw(ExpensesApp),
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "finance",
    title: "Finanzen",
    icons: markRaw(icons.Wallet),
    component: markRaw(FinanceApp),
    window: {
      width: 1400,
      height: 900
    }
  },
  // Weitere Apps können hier hinzugefügt werden
];
