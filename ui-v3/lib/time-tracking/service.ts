import { apiClient } from "@/lib/api/client"
import type { TimeEntry, TimeEntryCreate, TimeEntryUpdate, TimeTrackingStats, TimeListParams } from "./types"

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
}
