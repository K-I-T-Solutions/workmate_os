import { ref } from "vue";

export type CrmView =
  | "dashboard"
  | "customers"
  | "customer-detail"
  | "contacts"
  | "contact-detail";

export function useCrmNavigation() {
  // ─── STATE ────────────────────────────────────────────────
  const view = ref<CrmView>("dashboard");
  const activeCustomerId = ref<string | null>(null);
  const activeContactId = ref<string | null>(null);

  // ─── NAVIGATION ACTIONS ───────────────────────────────────
  function goDashboard() {
    view.value = "dashboard";
    activeCustomerId.value = null;
    activeContactId.value = null;
  }

  function goCustomers() {
    view.value = "customers";
    activeCustomerId.value = null;
    activeContactId.value = null;
  }

  function goCustomerDetail(customerId: string) {
    activeCustomerId.value = customerId;
    activeContactId.value = null;
    view.value = "customer-detail";
  }

  function goContacts(customerId?: string) {
    if (customerId) {
      activeCustomerId.value = customerId;
    }
    activeContactId.value = null;
    view.value = "contacts";
  }

  function goContactDetail(contactId: string) {
    activeContactId.value = contactId;
    view.value = "contact-detail";
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    view,
    activeCustomerId,
    activeContactId,

    goDashboard,
    goCustomers,
    goCustomerDetail,
    goContacts,
    goContactDetail,
  };
}
