import { ref } from 'vue';

// Stub: SevDesk-Integration wurde entfernt (b4b47e2).
// Diese Datei stellt leere Stubs bereit damit bestehende Imports nicht brechen.

export function useSevDesk() {
  const isConfigured = ref(false);
  const syncing = ref(false);
  const lastSyncTime = ref<string | undefined>(undefined);

  async function fetchConfig() {
    return null;
  }

  async function syncPayments() {
    return { success: false, payments_created: 0, invoices_status_updated: 0 };
  }

  async function syncInvoice(_invoiceId: string) {
    return { success: false, message: 'SevDesk nicht konfiguriert' };
  }

  return { isConfigured, syncing, lastSyncTime, fetchConfig, syncPayments, syncInvoice };
}
