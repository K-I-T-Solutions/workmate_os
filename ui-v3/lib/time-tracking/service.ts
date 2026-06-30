import { apiClient } from "@/lib/api/client"
import type { TimeEntry, TimeEntryCreate, TimeEntryUpdate, TimeTrackingStats, TimeListParams, BillableUninvoicedResponse } from "./types"

export const timeTrackingService = {
  async list(params?: TimeListParams): Promise<TimeEntry[]> {
    const { data } = await apiClient.get("/api/backoffice/time-tracking", { params })
    return data
  },

  async get(id: string): Promise<TimeEntry> {
    const { data } = await apiClient.get(`/api/backoffice/time-tracking/${id}`)
    return data
  },

  async create(payload: TimeEntryCreate): Promise<TimeEntry> {
    const { data } = await apiClient.post("/api/backoffice/time-tracking", payload)
    return data
  },

  async update(id: string, payload: TimeEntryUpdate): Promise<TimeEntry> {
    const { data } = await apiClient.put(`/api/backoffice/time-tracking/${id}`, payload)
    return data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/time-tracking/${id}`)
  },

  async approve(id: string): Promise<TimeEntry> {
    const { data } = await apiClient.put(`/api/backoffice/time-tracking/${id}/approve`)
    return data
  },

  async reject(id: string): Promise<TimeEntry> {
    const { data } = await apiClient.put(`/api/backoffice/time-tracking/${id}/reject`)
    return data
  },

  async getStats(): Promise<TimeTrackingStats> {
    const { data } = await apiClient.get("/api/backoffice/time-tracking/stats")
    return data
  },

  async getBillableUninvoiced(params?: { customer_id?: string; project_id?: string; employee_id?: string }): Promise<BillableUninvoicedResponse> {
    const { data } = await apiClient.get("/api/backoffice/time_tracking/billable-uninvoiced", { params })
    return data
  },

  async createInvoiceFromEntries(payload: {
    time_entry_ids: string[]
    customer_id: string
    project_id?: string
    hourly_rate: number
    group_by_task_type: boolean
    notes?: string
  }): Promise<{ id: string; invoice_number: string }> {
    const { data } = await apiClient.post("/api/backoffice/time_tracking/create-invoice", payload)
    return data
  },
}
