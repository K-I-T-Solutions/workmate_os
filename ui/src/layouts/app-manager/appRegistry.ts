import { markRaw } from "vue";
import { icons } from "lucide-vue-next";
import CrmApp from "@/modules/crm/CrmApp.vue";
import InvoicesApp from "@/modules/invoices/InvoicesApp.vue";
import ProjectsApp from "@/modules/projects/ProjectsApp.vue";
import TimeTrackingApp from "@/modules/time-tracking/TimeTrackingApp.vue";
import ExpensesApp from "@/modules/expenses/ExpensesApp.vue";
import FinanceApp from "@/modules/finance/FinanceApp.vue";
import AdminApp from "@/modules/admin/AdminApp.vue";

export const apps = [
  {
    id: "crm",
    title: "Kunden",
    icon: markRaw(icons.Users),
    component: markRaw(CrmApp),
    requiredPermission: "backoffice.crm",
    showInDock: true,
    dockOrder: 1,
    window: {
      width: 1100,
      height: 700
    }
  },
  {
    id: "projects",
    title: "Projekte",
    icon: markRaw(icons.Briefcase),
    component: markRaw(ProjectsApp),
    requiredPermission: "backoffice.projects",
    showInDock: true,
    dockOrder: 2,
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "time-tracking",
    title: "Zeiterfassung",
    icon: markRaw(icons.Clock),
    component: markRaw(TimeTrackingApp),
    requiredPermission: "backoffice.time_tracking",
    showInDock: true,
    dockOrder: 3,
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "invoices",
    title: "Rechnungen",
    icon: markRaw(icons.FileText),
    component: markRaw(InvoicesApp),
    requiredPermission: "backoffice.invoices",
    showInDock: true,
    dockOrder: 4,
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "expenses",
    title: "Ausgaben",
    icon: markRaw(icons.DollarSign),
    component: markRaw(ExpensesApp),
    requiredPermission: "backoffice.expenses",
    showInDock: true,
    dockOrder: 5,
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "finance",
    title: "Finanzen",
    icon: markRaw(icons.Wallet),
    component: markRaw(FinanceApp),
    requiredPermission: "backoffice.finance",
    showInDock: true,
    dockOrder: 6,
    window: {
      width: 1200,
      height: 800
    }
  },
  {
    id: "admin",
    title: "Administration",
    icon: markRaw(icons.Settings),
    component: markRaw(AdminApp),
    requiredPermission: "admin",
    showInDock: true,
    dockOrder: 99, // Last in dock
    window: {
      width: 1400,
      height: 900
    }
  },
  // Weitere Apps können hier hinzugefügt werden
];
