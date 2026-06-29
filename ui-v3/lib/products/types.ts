export type ProductCategory = "software" | "hardware" | "service" | "consulting" | "license" | "subscription" | "other"
export type PriceType = "fixed" | "hourly" | "daily" | "monthly" | "yearly" | "custom"

export interface Product {
  id: string
  name: string
  description: string | null
  short_description: string | null
  sku: string | null
  category: ProductCategory
  is_active: boolean
  is_service: boolean
  price_type: PriceType
  unit_price: number | string
  unit: string
  default_tax_rate: number | string
  min_quantity: number | string | null
  max_quantity: number | string | null
  internal_notes: string | null
  created_at: string
  updated_at: string
}

export interface ProductCreate {
  name: string
  description?: string
  short_description?: string
  sku?: string
  category?: ProductCategory
  is_active?: boolean
  is_service?: boolean
  price_type?: PriceType
  unit_price: number
  unit?: string
  default_tax_rate?: number
}
