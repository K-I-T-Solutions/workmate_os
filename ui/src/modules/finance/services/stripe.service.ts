/**
 * Stripe Payment Integration Service
 *
 * API-Client für Stripe Payment Gateway Integration
 */
import type {
  StripeConfig,
  StripeConfigRequest,
  StripeConfigResponse,
  StripePaymentIntentRequest,
  StripePaymentIntentResponse,
  StripePaymentLinkRequest,
  StripePaymentLinkResponse,
} from '../types/stripe';

const API_BASE = '/api/backoffice/finance/stripe';
const TOKEN_KEY = 'auth_token';

/**
 * Check if token looks like a valid JWT
 */
function isValidJWT(token: string): boolean {
  const parts = token.split('.');
  return parts.length === 3;
}

/**
 * Authenticated fetch wrapper with JWT token
 */
async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem(TOKEN_KEY);

  console.log('💳 [Stripe API] Request:', {
    url,
    method: options.method || 'GET',
    hasToken: !!token,
    isValidJWT: token ? isValidJWT(token) : false,
  });

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token && isValidJWT(token)) {
    headers['Authorization'] = `Bearer ${token}`;
  } else if (token && !isValidJWT(token)) {
    console.error('⚠️ [Stripe API] Token is not a valid JWT!');
  } else {
    console.warn('⚠️ [Stripe API] No auth token found!');
  }

  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers,
  });

  console.log('💳 [Stripe API] Response:', {
    url,
    status: response.status,
    ok: response.ok,
  });

  return response;
}

/**
 * Stripe API
 */
export const stripeApi = {
  // ============================================================================
  // CONFIG
  // ============================================================================

  /**
   * Stripe Konfiguration abrufen
   */
  async getConfig(): Promise<StripeConfig | null> {
    console.log('💳 [stripeApi.getConfig] Starting...');
    const response = await authFetch(`${API_BASE}/config`);

    if (response.status === 404) {
      console.log('💳 [stripeApi.getConfig] No config found (404)');
      return null;
    }

    if (!response.ok) {
      console.error('❌ [stripeApi.getConfig] Response not OK');
      throw new Error('Failed to fetch Stripe config');
    }

    const data = await response.json();
    console.log('💳 [stripeApi.getConfig] Parsed JSON:', data);
    return data;
  },

  /**
   * Stripe Konfiguration speichern/aktualisieren
   */
  async saveConfig(data: StripeConfigRequest): Promise<StripeConfigResponse> {
    console.log('💳 [stripeApi.saveConfig] Saving config...');

    try {
      const response = await authFetch(`${API_BASE}/config`, {
        method: 'POST',
        body: JSON.stringify(data),
      });

      const responseClone = response.clone();

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('💳 [stripeApi.saveConfig] Non-JSON response:', text);
        throw new Error(`Server returned non-JSON response`);
      }

      // Parse response
      let responseData;
      try {
        responseData = await response.json();
        console.log('💳 [stripeApi.saveConfig] Response data:', responseData);
      } catch (parseError) {
        const text = await responseClone.text();
        console.error('💳 [stripeApi.saveConfig] JSON parse error:', parseError);
        throw new Error(`Failed to parse JSON response`);
      }

      // Check if response is OK
      if (!response.ok) {
        const errorDetail = responseData?.detail || 'Unknown error';
        console.error('💳 [stripeApi.saveConfig] Error:', errorDetail);
        throw new Error(`Failed to save Stripe config: ${errorDetail}`);
      }

      return responseData;
    } catch (error) {
      console.error('💳 [stripeApi.saveConfig] Exception:', error);
      throw error;
    }
  },

  /**
   * Stripe Konfiguration deaktivieren
   */
  async deactivateConfig(): Promise<void> {
    console.log('💳 [stripeApi.deactivateConfig] Deactivating...');
    const response = await authFetch(`${API_BASE}/config`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to deactivate Stripe config');
    }

    console.log('💳 [stripeApi.deactivateConfig] Success');
  },

  // ============================================================================
  // PAYMENT INTENT
  // ============================================================================

  /**
   * Payment Intent für Invoice erstellen
   * Für Custom Checkout Flow (Stripe Elements)
   */
  async createPaymentIntent(
    invoiceId: string
  ): Promise<StripePaymentIntentResponse> {
    console.log('💳 [stripeApi.createPaymentIntent] Creating for invoice:', invoiceId);

    const response = await authFetch(`${API_BASE}/payment-intent`, {
      method: 'POST',
      body: JSON.stringify({ invoice_id: invoiceId } as StripePaymentIntentRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ [stripeApi.createPaymentIntent] Error:', error);
      throw new Error(error.detail || 'Failed to create Payment Intent');
    }

    const data = await response.json();
    console.log('💳 [stripeApi.createPaymentIntent] Success:', data);
    return data;
  },

  // ============================================================================
  // PAYMENT LINK
  // ============================================================================

  /**
   * Payment Link für Invoice erstellen
   * Für Hosted Checkout (Stripe Checkout Page)
   */
  async createPaymentLink(invoiceId: string): Promise<StripePaymentLinkResponse> {
    console.log('💳 [stripeApi.createPaymentLink] Creating for invoice:', invoiceId);

    const response = await authFetch(`${API_BASE}/payment-link`, {
      method: 'POST',
      body: JSON.stringify({ invoice_id: invoiceId } as StripePaymentLinkRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ [stripeApi.createPaymentLink] Error:', error);
      throw new Error(error.detail || 'Failed to create Payment Link');
    }

    const data = await response.json();
    console.log('💳 [stripeApi.createPaymentLink] Success:', data);
    return data;
  },
};
