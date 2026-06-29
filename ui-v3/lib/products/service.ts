import { apiClient } from "@/lib/api/client"
import type { Product, ProductCreate } from "./types"

export const productsService = {
  async list(params?: { search?: string; product_type?: string; limit?: number; skip?: number }): Promise<Product[]> {
    const { data } = await apiClient.get<Product[] | { items: Product[] }>("/api/backoffice/products", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },

  async create(payload: ProductCreate): Promise<Product> {
    const { data } = await apiClient.post<Product>("/api/backoffice/products", payload)
    return data
  },

  async update(id: string, payload: Partial<ProductCreate>): Promise<Product> {
    const { data } = await apiClient.patch<Product>(`/api/backoffice/products/${id}`, payload)
    return data
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/products/${id}`)
  },
}
