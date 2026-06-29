import { apiClient } from "@/lib/api/client"
import type { Reminder, ReminderCreate } from "./types"

export const remindersService = {
  async list(): Promise<Reminder[]> {
    const { data } = await apiClient.get<{ items: Reminder[]; total: number }>("/api/reminders")
    return data.items ?? []
  },

  async create(payload: ReminderCreate): Promise<Reminder> {
    const { data } = await apiClient.post<Reminder>("/api/reminders", payload)
    return data
  },

  async markDone(id: string): Promise<Reminder> {
    const { data } = await apiClient.post<Reminder>(`/api/reminders/${id}/mark-done`)
    return data
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/api/reminders/${id}`)
  },
}
