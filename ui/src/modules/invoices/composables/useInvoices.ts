/**
 * useInvoices Composable
 * Verwaltet das Laden und Verarbeiten von Rechnungen
 */

import { ref, computed } from 'vue';
import { invoicesService } from '../services/invoices.service';
import type {
  Invoice,
  InvoiceListResponse,
  InvoiceFilterParams,
  InvoiceCreateRequest,
  InvoiceUpdateRequest,
} from '../types';

export function useInvoices() {
  // ─── STATE ────────────────────────────────────────────────
  const invoices = ref<Invoice[]>([]);
  const currentInvoice = ref<Invoice | null>(null);
  const total = ref(0);
  const page = ref(1);
  const pages = ref(1);
  const limit = ref(20);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ─── COMPUTED ─────────────────────────────────────────────
  const hasInvoices = computed(() => invoices.value.length > 0);
  const isEmpty = computed(() => !loading.value && invoices.value.length === 0);

  // ─── ACTIONS ──────────────────────────────────────────────

  /**
   * Rechnungen laden mit Filtern
   */
  async function loadInvoices(filters?: InvoiceFilterParams) {
    loading.value = true;
    error.value = null;

    try {
      const response: InvoiceListResponse = await invoicesService.list(filters);
      invoices.value = response.items;
      total.value = response.total;
      page.value = response.page;
      pages.value = response.pages;
      limit.value = response.limit;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Rechnungen';
      console.error('Error loading invoices:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Einzelne Rechnung laden
   */
  async function loadInvoice(id: string) {
    loading.value = true;
    error.value = null;

    try {
      currentInvoice.value = await invoicesService.getById(id);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Rechnung';
      console.error('Error loading invoice:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Rechnung nach Nummer laden
   */
  async function loadInvoiceByNumber(invoiceNumber: string) {
    loading.value = true;
    error.value = null;

    try {
      currentInvoice.value = await invoicesService.getByNumber(invoiceNumber);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Rechnung';
      console.error('Error loading invoice by number:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Neue Rechnung erstellen
   */
  async function createInvoice(data: InvoiceCreateRequest): Promise<Invoice | null> {
    loading.value = true;
    error.value = null;

    try {
      const invoice = await invoicesService.create(data);
      // Zur Liste hinzufügen wenn bereits geladen
      if (invoices.value.length > 0) {
        invoices.value.unshift(invoice);
      }
      return invoice;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Erstellen der Rechnung';
      console.error('Error creating invoice:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Rechnung aktualisieren
   */
  async function updateInvoice(id: string, data: InvoiceUpdateRequest): Promise<Invoice | null> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await invoicesService.update(id, data);

      // In der Liste aktualisieren
      const index = invoices.value.findIndex((inv) => inv.id === id);
      if (index !== -1) {
        invoices.value[index] = updated;
      }

      // Current invoice aktualisieren
      if (currentInvoice.value?.id === id) {
        currentInvoice.value = updated;
      }

      return updated;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren der Rechnung';
      console.error('Error updating invoice:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Rechnungsstatus aktualisieren
   */
  async function updateInvoiceStatus(id: string, status: string): Promise<Invoice | null> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await invoicesService.updateStatus(id, status);

      // In der Liste aktualisieren
      const index = invoices.value.findIndex((inv) => inv.id === id);
      if (index !== -1) {
        invoices.value[index] = updated;
      }

      // Current invoice aktualisieren
      if (currentInvoice.value?.id === id) {
        currentInvoice.value = updated;
      }

      return updated;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren des Status';
      console.error('Error updating invoice status:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Rechnung löschen
   */
  async function deleteInvoice(id: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await invoicesService.delete(id);

      // Aus der Liste entfernen
      invoices.value = invoices.value.filter((inv) => inv.id !== id);

      // Current invoice zurücksetzen
      if (currentInvoice.value?.id === id) {
        currentInvoice.value = null;
      }

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Löschen der Rechnung';
      console.error('Error deleting invoice:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * PDF herunterladen
   */
  async function downloadPdf(id: string, invoiceNumber: string) {
    loading.value = true;
    error.value = null;

    try {
      const blob = await invoicesService.downloadPdf(id);
      invoicesService.triggerPdfDownload(blob, `${invoiceNumber}.pdf`);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Herunterladen des PDFs';
      console.error('Error downloading PDF:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * PDF in neuem Tab öffnen
   */
  async function openPdf(id: string, invoiceNumber: string) {
    loading.value = true;
    error.value = null;

    try {
      const blob = await invoicesService.downloadPdf(id);
      invoicesService.openPdfInNewTab(blob, `${invoiceNumber}.pdf`);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Öffnen des PDFs';
      console.error('Error opening PDF:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fehler zurücksetzen
   */
  function clearError() {
    error.value = null;
  }

  /**
   * State zurücksetzen
   */
  function reset() {
    invoices.value = [];
    currentInvoice.value = null;
    total.value = 0;
    page.value = 1;
    pages.value = 1;
    loading.value = false;
    error.value = null;
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    invoices,
    currentInvoice,
    total,
    page,
    pages,
    limit,
    loading,
    error,

    // Computed
    hasInvoices,
    isEmpty,

    // Actions
    loadInvoices,
    loadInvoice,
    loadInvoiceByNumber,
    createInvoice,
    updateInvoice,
    updateInvoiceStatus,
    deleteInvoice,
    downloadPdf,
    openPdf,
    clearError,
    reset,
  };
}
