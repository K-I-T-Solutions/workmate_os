/**
 * Stripe Payment Integration Types
 */

// ============================================================================
// CONFIG
// ============================================================================

export interface StripeConfigRequest {
  publishable_key: string;
  secret_key: string;
  webhook_secret?: string;
  test_mode: boolean;
}

export interface StripeConfigResponse {
  id: string;
  configured: boolean;
  test_mode: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StripeConfig extends StripeConfigResponse {
  // Additional frontend-only fields if needed
}

// ============================================================================
// PAYMENT INTENT
// ============================================================================

export interface StripePaymentIntentRequest {
  invoice_id: string;
}

export interface StripePaymentIntentResponse {
  success: boolean;
  payment_intent_id: string;
  client_secret: string;
  amount: number;
  currency: string;
  invoice_id: string;
  invoice_number: string;
}

// ============================================================================
// PAYMENT LINK
// ============================================================================

export interface StripePaymentLinkRequest {
  invoice_id: string;
}

export interface StripePaymentLinkResponse {
  success: boolean;
  payment_link_id: string;
  payment_url: string;
  amount: number;
  currency: string;
  invoice_id: string;
  invoice_number: string;
}

// ============================================================================
// WEBHOOK (for reference, not used in frontend directly)
// ============================================================================

export interface StripeWebhookEvent {
  type: string;
  data: {
    object: any;
  };
}
