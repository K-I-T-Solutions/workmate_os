import { ref } from 'vue';

// Stub: Stripe-Integration wurde entfernt (b4b47e2).
// Diese Datei stellt leere Stubs bereit damit bestehende Imports nicht brechen.

export function useStripe() {
  const isConfigured = ref(false);
  const processing = ref(false);

  async function fetchConfig() {
    return null;
  }

  async function createPaymentLink(_invoiceId: string) {
    return { success: false, payment_url: '', amount: 0 };
  }

  return { isConfigured, processing, fetchConfig, createPaymentLink };
}
