import { apiClient } from "@/lib/api/client"
import type {
  KBCategory, KBCategoryCreate,
  KBArticle, KBArticleDetail, KBArticleCreate, KBArticleUpdate,
  ArticleListParams,
} from "./types"

export const knowledgeService = {
  // Categories
  async listCategories(): Promise<KBCategory[]> {
    const { data } = await apiClient.get("/api/kb/categories")
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async createCategory(payload: KBCategoryCreate): Promise<KBCategory> {
    const { data } = await apiClient.post("/api/kb/categories", payload)
    return data
  },
  async updateCategory(id: string, payload: Partial<KBCategoryCreate>): Promise<KBCategory> {
    const { data } = await apiClient.patch(`/api/kb/categories/${id}`, payload)
    return data
  },
  async deleteCategory(id: string): Promise<void> {
    await apiClient.delete(`/api/kb/categories/${id}`)
  },

  // Articles
  async listArticles(params?: ArticleListParams): Promise<KBArticle[]> {
    const { data } = await apiClient.get("/api/kb/articles", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async getArticle(id: string): Promise<KBArticleDetail> {
    const { data } = await apiClient.get(`/api/kb/articles/${id}`)
    return data
  },
  async createArticle(payload: KBArticleCreate): Promise<KBArticleDetail> {
    const { data } = await apiClient.post("/api/kb/articles", payload)
    return data
  },
  async updateArticle(id: string, payload: KBArticleUpdate): Promise<KBArticleDetail> {
    const { data } = await apiClient.patch(`/api/kb/articles/${id}`, payload)
    return data
  },
  async deleteArticle(id: string): Promise<void> {
    await apiClient.delete(`/api/kb/articles/${id}`)
  },
  async vote(id: string, helpful: boolean): Promise<void> {
    await apiClient.post(`/api/kb/articles/${id}/vote`, null, { params: { helpful } })
  },
}
