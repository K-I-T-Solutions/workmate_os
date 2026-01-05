export type PriceType = 'hourly' | 'fixed' | 'monthly' | 'project' | 'per_unit';

export type ProductCategory =
  | 'private_customer'
  | 'small_business'
  | 'enterprise'
  | 'hardware'
  | 'software'
  | 'consulting'
  | 'support'
  | 'development'
  | 'other';

export interface Product {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  description: string | null;
  short_description: string | null;
  sku: string | null;
  category: ProductCategory;
  is_active: boolean;
  is_service: boolean;
  price_type: PriceType;
  unit_price: number;
  unit: string;
  default_tax_rate: number;
  min_quantity: number | null;
  max_quantity: number | null;
  internal_notes: string | null;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  skip: number;
  limit: number;
}
