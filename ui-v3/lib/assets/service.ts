import { apiClient } from "@/lib/api/client"
import type { AssetPayload, CustomerAsset, ExpiringItem, LicensePayload, Paged, SoftwareLicense } from "./types"

const BASE = "/api/backoffice/assets"

export const assetsService = {
  async list(params?: { customer_id?: string; asset_type?: string; status?: string; search?: string; limit?: number }): Promise<Paged<CustomerAsset>> {
    const { data } = await apiClient.get(`${BASE}/`, { params })
    return data
  },

  async create(payload: AssetPayload): Promise<CustomerAsset> {
    const { data } = await apiClient.post(`${BASE}/`, payload)
    return data
  },

  async update(id: string, payload: AssetPayload): Promise<CustomerAsset> {
    const { data } = await apiClient.put(`${BASE}/${id}`, payload)
    return data
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${BASE}/${id}`)
  },

  async listLicenses(params?: { customer_id?: string; asset_id?: string; search?: string; limit?: number }): Promise<Paged<SoftwareLicense>> {
    const { data } = await apiClient.get(`${BASE}/licenses`, { params })
    return data
  },

  async createLicense(payload: LicensePayload): Promise<SoftwareLicense> {
    const { data } = await apiClient.post(`${BASE}/licenses`, payload)
    return data
  },

  async updateLicense(id: string, payload: LicensePayload): Promise<SoftwareLicense> {
    const { data } = await apiClient.put(`${BASE}/licenses/${id}`, payload)
    return data
  },

  async removeLicense(id: string): Promise<void> {
    await apiClient.delete(`${BASE}/licenses/${id}`)
  },

  async expiring(withinDays = 60): Promise<ExpiringItem[]> {
    const { data } = await apiClient.get(`${BASE}/expiring`, { params: { within_days: withinDays } })
    return data.items
  },
}
