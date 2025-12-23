/**
 * Invoices Navigation Composable
 * Verwaltet die interne Navigation innerhalb des Invoices-Moduls
 */

import { ref } from 'vue';

export type InvoicesView =
  | 'dashboard'      // Dashboard mit KPIs und Übersicht
  | 'list'           // Rechnungsliste
  | 'detail'         // Rechnungsdetail
  | 'create'         // Rechnung erstellen
  | 'edit';          // Rechnung bearbeiten

export function useInvoicesNavigation() {
  // ─── STATE ────────────────────────────────────────────────
  const view = ref<InvoicesView>('dashboard');
  const activeInvoiceId = ref<string | null>(null);

  // ─── NAVIGATION ACTIONS ───────────────────────────────────

  /**
   * Zum Dashboard navigieren
   */
  function goDashboard() {
    view.value = 'dashboard';
    activeInvoiceId.value = null;
  }

  /**
   * Zur Rechnungsliste navigieren
   */
  function goList() {
    view.value = 'list';
    activeInvoiceId.value = null;
  }

  /**
   * Zu Rechnungsdetail navigieren
   */
  function goDetail(invoiceId: string) {
    activeInvoiceId.value = invoiceId;
    view.value = 'detail';
  }

  /**
   * Rechnungserstellung öffnen
   */
  function goCreate() {
    view.value = 'create';
    activeInvoiceId.value = null;
  }

  /**
   * Rechnungsbearbeitung öffnen
   */
  function goEdit(invoiceId: string) {
    activeInvoiceId.value = invoiceId;
    view.value = 'edit';
  }

  /**
   * Zurück zur Liste
   */
  function goBack() {
    if (view.value === 'detail' || view.value === 'edit') {
      goList();
    } else if (view.value === 'create') {
      goList();
    } else {
      goDashboard();
    }
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    view,
    activeInvoiceId,

    // Actions
    goDashboard,
    goList,
    goDetail,
    goCreate,
    goEdit,
    goBack,
  };
}
