import { apiClient } from "@/lib/api/client"
import type {
  BillingRunResult,
  Contract,
  ContractCreate,
  ContractInvoiceBrief,
  ContractListResponse,
  ContractStats,
  ContractUpdate,
} from "./types"

const BASE = "/api/backoffice/contracts"

export const contractsService = {
  async list(params?: { status?: string; customer_id?: string; search?: string; skip?: number; limit?: number }): Promise<ContractListResponse> {
    const { data } = await apiClient.get(`${BASE}/`, { params })
    return data
  },

  async get(id: string): Promise<Contract> {
    const { data } = await apiClient.get(`${BASE}/${id}`)
    return data
  },

  async create(payload: ContractCreate): Promise<Contract> {
    const { data } = await apiClient.post(`${BASE}/`, payload)
    return data
  },

  async update(id: string, payload: ContractUpdate): Promise<Contract> {
    const { data } = await apiClient.put(`${BASE}/${id}`, payload)
    return data
  },

  async cancel(id: string, endDate: string, reason?: string): Promise<Contract> {
    const { data } = await apiClient.post(`${BASE}/${id}/cancel`, { end_date: endDate, reason })
    return data
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${BASE}/${id}`)
  },

  async stats(): Promise<ContractStats> {
    const { data } = await apiClient.get(`${BASE}/stats`)
    return data
  },

  async invoices(id: string): Promise<ContractInvoiceBrief[]> {
    const { data } = await apiClient.get(`${BASE}/${id}/invoices`)
    return data
  },

  async runBilling(): Promise<BillingRunResult> {
    const { data } = await apiClient.post(`${BASE}/billing/run`, {})
    return data
  },

  async billNow(id: string): Promise<BillingRunResult> {
    const { data } = await apiClient.post(`${BASE}/${id}/bill`, {})
    return data
  },
}
