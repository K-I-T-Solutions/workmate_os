/**
 * Stripe Composable
 *
 * State-Management und Business-Logic für Stripe Payment Integration
 */
import { ref, computed } from 'vue';
import { stripeApi } from '../services/stripe.service';
import type {
  StripeConfig,
  StripeConfigRequest,
  StripePaymentIntentResponse,
  StripePaymentLinkResponse,
} from '../types/stripe';

export function useStripe() {
  // State
  const config = ref<StripeConfig | null>(null);
  const loading = ref(false);
  const processing = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const isConfigured = computed(() => {
    return config.value !== null && config.value.configured && config.value.is_active;
  });

  const isTestMode = computed(() => {
    return config.value?.test_mode || false;
  });

  // Config Actions
  async function fetchConfig() {
    loading.value = true;
    error.value = null;
    try {
      config.value = await stripeApi.getConfig();
      return config.value;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to fetch Stripe config:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function saveConfig(data: StripeConfigRequest) {
    loading.value = true;
    error.value = null;
    try {
      const response = await stripeApi.saveConfig(data);
      // Refresh config after save
      await fetchConfig();
      return response;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to save Stripe config:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function deactivateConfig() {
    loading.value = true;
    error.value = null;
    try {
      await stripeApi.deactivateConfig();
      config.value = null;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to deactivate Stripe config:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  // Payment Actions

  /**
   * Payment Intent für Custom Checkout erstellen
   * Gibt client_secret zurück, der für Stripe Elements benötigt wird
   */
  async function createPaymentIntent(
    invoiceId: string
  ): Promise<StripePaymentIntentResponse> {
    processing.value = true;
    error.value = null;
    try {
      const result = await stripeApi.createPaymentIntent(invoiceId);
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to create Payment Intent:', e);
      throw e;
    } finally {
      processing.value = false;
    }
  }

  /**
   * Payment Link für Hosted Checkout erstellen
   * Gibt payment_url zurück, zu der der Kunde weitergeleitet werden kann
   */
  async function createPaymentLink(invoiceId: string): Promise<StripePaymentLinkResponse> {
    processing.value = true;
    error.value = null;
    try {
      const result = await stripeApi.createPaymentLink(invoiceId);
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to create Payment Link:', e);
      throw e;
    } finally {
      processing.value = false;
    }
  }

  return {
    // State
    config,
    loading,
    processing,
    error,

    // Computed
    isConfigured,
    isTestMode,

    // Actions
    fetchConfig,
    saveConfig,
    deactivateConfig,
    createPaymentIntent,
    createPaymentLink,
  };
}
