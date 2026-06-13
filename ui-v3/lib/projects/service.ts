import { apiClient } from "@/lib/api/client"
import type { Project, CreateProjectPayload, UpdateProjectPayload } from "./types"

export const projectService = {
  async list(params?: { customer_id?: string }): Promise<Project[]> {
    const { data } = await apiClient.get("/api/backoffice/projects/", { params })
    return data
  },

  async get(id: string): Promise<Project> {
    const { data } = await apiClient.get(`/api/backoffice/projects/${id}`)
    return data
  },

  async create(payload: CreateProjectPayload): Promise<Project> {
    const { data } = await apiClient.post("/api/backoffice/projects/", payload)
    return data
  },

  async update(id: string, payload: UpdateProjectPayload): Promise<Project> {
    const { data } = await apiClient.put(`/api/backoffice/projects/${id}`, payload)
    return data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/projects/${id}`)
  },
}
