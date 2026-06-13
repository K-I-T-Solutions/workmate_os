import { apiClient } from "@/lib/api/client"
import type { DocumentRecord, DocumentListResponse, DocumentUpdate } from "./types"

interface ListParams {
  skip?: number
  limit?: number
  search?: string
  category?: string
  linked_module?: string
  owner_id?: string
  customer_id?: string
  is_confidential?: boolean
}

export const documentService = {
  async list(params?: ListParams): Promise<DocumentListResponse> {
    const { data } = await apiClient.get<DocumentListResponse>("/api/documents", { params })
    return data
  },

  async get(id: string): Promise<DocumentRecord> {
    const { data } = await apiClient.get<DocumentRecord>(`/api/documents/${id}`)
    return data
  },

  async upload(
    file: File,
    meta?: {
      owner_id?: string
      customer_id?: string
      title?: string
      category?: string
      linked_module?: string
      is_confidential?: boolean
    }
  ): Promise<DocumentRecord> {
    const form = new FormData()
    form.append("file", file)
    if (meta?.owner_id) form.append("owner_id", meta.owner_id)
    if (meta?.customer_id) form.append("customer_id", meta.customer_id)
    if (meta?.title) form.append("title", meta.title)
    if (meta?.category) form.append("category", meta.category)
    if (meta?.linked_module) form.append("linked_module", meta.linked_module)
    form.append("is_confidential", String(meta?.is_confidential ?? false))
    const { data } = await apiClient.post<DocumentRecord>("/api/documents", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    return data
  },

  async update(id: string, update: DocumentUpdate): Promise<DocumentRecord> {
    const { data } = await apiClient.put<DocumentRecord>(`/api/documents/${id}`, update)
    return data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/documents/${id}`)
  },

  downloadUrl(id: string): string {
    return `/api/documents/${id}/download`
  },

  async download(id: string, filename?: string): Promise<void> {
    const { data } = await apiClient.get(`/api/documents/${id}/download`, {
      responseType: "blob",
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement("a")
    a.href = url
    a.download = filename ?? `dokument-${id}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  },
}
