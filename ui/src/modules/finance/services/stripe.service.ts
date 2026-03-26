/**
 * Stripe Payment Integration Service
 */
import { apiClient } from '@/services/api/client';
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

export const stripeApi = {
  async getConfig(): Promise<StripeConfig | null> {
    try {
      const { data } = await apiClient.get(`${API_BASE}/config`);
      return data;
    } catch (e: any) {
      if (e.response?.status === 404) return null;
      throw e;
    }
  },

  async saveConfig(data: StripeConfigRequest): Promise<StripeConfigResponse> {
    const response = await apiClient.post(`${API_BASE}/config`, data);
    return response.data;
  },

  async deactivateConfig(): Promise<void> {
    await apiClient.delete(`${API_BASE}/config`);
  },

  async createPaymentIntent(invoiceId: string): Promise<StripePaymentIntentResponse> {
    const { data } = await apiClient.post(`${API_BASE}/payment-intent`, {
      invoice_id: invoiceId,
    } as StripePaymentIntentRequest);
    return data;
  },

  async createPaymentLink(invoiceId: string): Promise<StripePaymentLinkResponse> {
    const { data } = await apiClient.post(`${API_BASE}/payment-link`, {
      invoice_id: invoiceId,
    } as StripePaymentLinkRequest);
    return data;
  },
};
