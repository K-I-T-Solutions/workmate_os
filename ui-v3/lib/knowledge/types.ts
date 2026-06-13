export type ArticleStatus = "draft" | "published" | "archived"

export interface KBCategory {
  id: string
  name: string
  description: string | null
  slug: string
  icon: string | null
  color: string | null
  order: number
  article_count: number
  created_at: string
}

export interface KBCategoryCreate {
  name: string
  description?: string | null
  slug?: string
  icon?: string | null
  color?: string | null
  order?: number
}

export interface KBArticle {
  id: string
  title: string
  slug: string
  excerpt: string | null
  category_id: string | null
  tags: string[]
  status: ArticleStatus
  author_id: string | null
  view_count: number
  helpful_count: number
  not_helpful_count: number
  pinned: boolean
  created_at: string
  updated_at: string
  published_at: string | null
}

export interface KBArticleDetail extends KBArticle {
  content: string
}

export interface KBArticleCreate {
  title: string
  content: string
  excerpt?: string | null
  category_id?: string | null
  tags?: string[]
  status?: ArticleStatus
  pinned?: boolean
}

export interface KBArticleUpdate extends Partial<KBArticleCreate> {}

export interface ArticleListParams {
  search?: string
  category_id?: string
  status?: ArticleStatus
  skip?: number
  limit?: number
}
