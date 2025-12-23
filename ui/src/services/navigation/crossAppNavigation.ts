/**
 * Cross-App Navigation Service
 * Ermöglicht Navigation zwischen verschiedenen Apps (CRM, Invoices, Projects, etc.)
 */

import { appManager } from '@/layouts/app-manager/useAppManager';

/**
 * Öffnet die CRM-App und navigiert zu einem bestimmten Kunden
 */
export function navigateToCustomer(customerId: string) {
  appManager.openWindow('crm', {
    initialView: 'detail',
    initialCustomerId: customerId,
  });
}

/**
 * Öffnet die CRM-App und navigiert zu einem bestimmten Kontakt
 */
export function navigateToContact(customerId: string, contactId: string) {
  appManager.openWindow('crm', {
    initialView: 'contact-detail',
    initialCustomerId: customerId,
    initialContactId: contactId,
  });
}

/**
 * Öffnet die Invoice-App und navigiert zu einer bestimmten Rechnung
 */
export function navigateToInvoice(invoiceId: string) {
  appManager.openWindow('invoices', {
    initialView: 'detail',
    initialInvoiceId: invoiceId,
  });
}

/**
 * Öffnet die Invoice-App in der Erstellungsansicht für einen Kunden
 */
export function createInvoiceForCustomer(customerId: string) {
  appManager.openWindow('invoices', {
    initialView: 'create',
    prefilledCustomerId: customerId,
  });
}

/**
 * Öffnet die Projects-App und navigiert zu einem bestimmten Projekt
 */
export function navigateToProject(projectId: string) {
  appManager.openWindow('projects', {
    initialView: 'detail',
    initialProjectId: projectId,
  });
}

/**
 * Generische Funktion zum Öffnen einer App mit Context
 */
export function navigateToApp(appId: string, context?: Record<string, any>) {
  appManager.openWindow(appId, context);
}
