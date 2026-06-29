export type ProductType = "service" | "product" | "license" | "subscription"

export interface Product {
  id: string
  name: string
  sku: string | null
  description: string | null
  product_type: ProductType
  unit_price: number | string
  currency: string
  unit: string | null
  tax_rate: number | string
  is_active: boolean
  created_at: string
}

export interface ProductCreate {
  name: string
  sku?: string
  description?: string
  product_type: ProductType
  unit_price: number
  currency?: string
  unit?: string
  tax_rate?: number
}
