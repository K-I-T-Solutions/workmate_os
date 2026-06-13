import { apiClient } from "@/lib/api/client"
import type { Customer, Contact, CrmActivity, CreateCrmActivity, CsvImportResult, CrmStats, ContactWithCustomer } from "./types"

export const crmService = {
  // Customers
  async getCustomers(params?: { status?: string; search?: string; skip?: number; limit?: number }): Promise<Customer[]> {
    const { data } = await apiClient.get("/api/backoffice/crm/customers", { params })
    return data
  },
  async getCustomer(id: string): Promise<Customer> {
    const { data } = await apiClient.get(`/api/backoffice/crm/customers/${id}`)
    return data
  },
  async createCustomer(payload: Partial<Customer>) {
    return apiClient.post("/api/backoffice/crm/customers", payload)
  },
  async updateCustomer(id: string, payload: Partial<Customer>) {
    return apiClient.put(`/api/backoffice/crm/customers/${id}`, payload)
  },
  async deleteCustomer(id: string) {
    return apiClient.delete(`/api/backoffice/crm/customers/${id}`)
  },

  // Contacts
  async getCustomerContacts(customerId: string): Promise<Contact[]> {
    const { data } = await apiClient.get(`/api/backoffice/crm/customers/${customerId}/contacts`)
    return data
  },
  async createContact(payload: Partial<Contact>) {
    return apiClient.post("/api/backoffice/crm/contacts", payload)
  },
  async updateContact(id: string, payload: Partial<Contact>) {
    return apiClient.put(`/api/backoffice/crm/contacts/${id}`, payload)
  },
  async deleteContact(id: string) {
    return apiClient.delete(`/api/backoffice/crm/contacts/${id}`)
  },
  async setPrimaryContact(customerId: string, contactId: string) {
    return apiClient.put(`/api/backoffice/crm/customers/${customerId}/contacts/${contactId}/set-primary`)
  },

  // Activities
  async getCustomerActivities(customerId: string, opts?: { limit?: number }): Promise<CrmActivity[]> {
    const { data } = await apiClient.get(`/api/backoffice/crm/customers/${customerId}/activities`, { params: opts })
    return data
  },
  async createActivity(payload: CreateCrmActivity): Promise<CrmActivity> {
    const { data } = await apiClient.post("/api/backoffice/crm/activities", payload)
    return data
  },

  // Pipeline
  async getPipeline(): Promise<Record<string, Customer[]>> {
    const { data } = await apiClient.get("/api/backoffice/crm/pipeline")
    return data
  },
  async updatePipelineStage(customerId: string, stage: string): Promise<Customer> {
    const { data } = await apiClient.patch(`/api/backoffice/crm/customers/${customerId}/pipeline-stage`, { stage })
    return data
  },

  // Stats & Activities
  async getStats(): Promise<CrmStats> {
    const { data } = await apiClient.get("/api/backoffice/crm/stats")
    return data
  },
  async getLatestActivities(limit = 10): Promise<(CrmActivity & { customer_name?: string })[]> {
    const { data } = await apiClient.get(`/api/backoffice/crm/activities/latest?limit=${limit}`)
    return Array.isArray(data) ? data : (data.items ?? [])
  },

  // Global contacts
  async getAllContacts(params?: { search?: string; skip?: number; limit?: number }): Promise<ContactWithCustomer[]> {
    const { data } = await apiClient.get("/api/backoffice/crm/contacts", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },

  // CSV Import
  async importCsvDryRun(file: File): Promise<CsvImportResult> {
    const formData = new FormData()
    formData.append("file", file)
    const { data } = await apiClient.post("/api/backoffice/crm/customers/import-csv?dry_run=true", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    return data
  },
  async importCsv(file: File, skipDuplicates = true): Promise<CsvImportResult> {
    const formData = new FormData()
    formData.append("file", file)
    const { data } = await apiClient.post(
      `/api/backoffice/crm/customers/import-csv?skip_duplicates=${skipDuplicates}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    )
    return data
  },
}
