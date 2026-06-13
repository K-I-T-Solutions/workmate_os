import { apiClient } from "@/lib/api/client"
import type { Ticket, TicketDetail, TicketListResponse, TicketComment, CreateTicketPayload, UpdateTicketPayload } from "./types"

export const supportService = {
  async list(params?: {
    skip?: number; limit?: number; status?: string; priority?: string
    category?: string; type?: string; customer_id?: string; search?: string
  }): Promise<TicketListResponse> {
    const { data } = await apiClient.get("/api/support/tickets", { params })
    return data
  },

  async get(id: string): Promise<TicketDetail> {
    const { data } = await apiClient.get(`/api/support/tickets/${id}`)
    return data
  },

  async create(payload: CreateTicketPayload): Promise<Ticket> {
    const { data } = await apiClient.post("/api/support/tickets", payload)
    return data
  },

  async update(id: string, payload: UpdateTicketPayload): Promise<Ticket> {
    const { data } = await apiClient.put(`/api/support/tickets/${id}`, payload)
    return data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/support/tickets/${id}`)
  },

  async addComment(id: string, content: string, isInternal = false): Promise<TicketComment> {
    const { data } = await apiClient.post(`/api/support/tickets/${id}/comments`, {
      content,
      is_internal: isInternal,
    })
    return data
  },

  async deleteComment(ticketId: string, commentId: string): Promise<void> {
    await apiClient.delete(`/api/support/tickets/${ticketId}/comments/${commentId}`)
  },
}
