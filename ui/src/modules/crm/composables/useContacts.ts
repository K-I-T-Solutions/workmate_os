/**
 * useContacts Composable
 * Verwaltet das Laden und Verarbeiten von Kontakten
 */

import { ref, computed } from 'vue';
import { crmService } from '../services/crm.service';
import type { Contact } from '../types/contact';

export interface ContactFilters {
  customerId?: string;
  isPrimary?: boolean;
  search?: string;
}

export function useContacts() {
  // ─── STATE ────────────────────────────────────────────────
  const contacts = ref<Contact[]>([]);
  const currentContact = ref<Contact | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ─── COMPUTED ─────────────────────────────────────────────
  const hasContacts = computed(() => contacts.value.length > 0);
  const isEmpty = computed(() => !loading.value && contacts.value.length === 0);
  const primaryContact = computed(() => contacts.value.find((c) => c.is_primary) || null);

  // ─── ACTIONS ──────────────────────────────────────────────

  /**
   * Kontakte laden mit Filtern
   */
  async function loadContacts(filters?: ContactFilters) {
    loading.value = true;
    error.value = null;

    try {
      // API-Call
      const response = await crmService.getContacts();

      // Client-seitige Filterung
      let filtered = response;

      // Filter nach Kunde
      if (filters?.customerId) {
        filtered = filtered.filter((c) => c.customer_id === filters.customerId);
      }

      // Filter nach Primärkontakt
      if (filters?.isPrimary !== undefined) {
        filtered = filtered.filter((c) => c.is_primary === filters.isPrimary);
      }

      // Suchfilter
      if (filters?.search) {
        const search = filters.search.toLowerCase();
        filtered = filtered.filter((c) =>
          c.firstname.toLowerCase().includes(search) ||
          c.lastname.toLowerCase().includes(search) ||
          c.email?.toLowerCase().includes(search) ||
          c.phone?.toLowerCase().includes(search) ||
          c.mobile?.toLowerCase().includes(search)
        );
      }

      contacts.value = filtered;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Kontakte';
      console.error('Error loading contacts:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Einzelnen Kontakt laden
   */
  async function loadContact(id: string) {
    loading.value = true;
    error.value = null;

    try {
      currentContact.value = await crmService.getContact(id);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden des Kontakts';
      console.error('Error loading contact:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Neuen Kontakt erstellen
   */
  async function createContact(data: Partial<Contact>): Promise<Contact | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await crmService.createContact(data);
      const contact = response.data;

      // Zur Liste hinzufügen wenn bereits geladen
      if (contacts.value.length > 0) {
        contacts.value.unshift(contact);
      }

      return contact;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Erstellen des Kontakts';
      console.error('Error creating contact:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Kontakt aktualisieren
   */
  async function updateContact(id: string, data: Partial<Contact>): Promise<Contact | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await crmService.updateContact(id, data);
      const updated = response.data;

      // In der Liste aktualisieren
      const index = contacts.value.findIndex((c) => c.id === id);
      if (index !== -1) {
        contacts.value[index] = updated;
      }

      // Current contact aktualisieren
      if (currentContact.value?.id === id) {
        currentContact.value = updated;
      }

      return updated;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren des Kontakts';
      console.error('Error updating contact:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Kontakt löschen
   */
  async function deleteContact(id: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await crmService.deleteContact(id);

      // Aus der Liste entfernen
      contacts.value = contacts.value.filter((c) => c.id !== id);

      // Current contact zurücksetzen
      if (currentContact.value?.id === id) {
        currentContact.value = null;
      }

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Löschen des Kontakts';
      console.error('Error deleting contact:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Primärkontakt setzen
   */
  async function setPrimaryContact(customerId: string, contactId: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await crmService.setPrimaryContact(customerId, contactId);

      // In der Liste alle is_primary zurücksetzen und neuen setzen
      contacts.value = contacts.value.map((c) => ({
        ...c,
        is_primary: c.id === contactId,
      }));

      // Current contact aktualisieren
      if (currentContact.value) {
        currentContact.value.is_primary = currentContact.value.id === contactId;
      }

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Setzen des Primärkontakts';
      console.error('Error setting primary contact:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Primärkontakt eines Kunden laden
   */
  async function loadPrimaryContact(customerId: string) {
    loading.value = true;
    error.value = null;

    try {
      const contact = await crmService.getPrimaryContact(customerId);
      if (contact) {
        currentContact.value = contact;
      }
      return contact;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden des Primärkontakts';
      console.error('Error loading primary contact:', e);
      return null;
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
    contacts.value = [];
    currentContact.value = null;
    loading.value = false;
    error.value = null;
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    contacts,
    currentContact,
    loading,
    error,

    // Computed
    hasContacts,
    isEmpty,
    primaryContact,

    // Actions
    loadContacts,
    loadContact,
    createContact,
    updateContact,
    deleteContact,
    setPrimaryContact,
    loadPrimaryContact,
    clearError,
    reset,
  };
}
