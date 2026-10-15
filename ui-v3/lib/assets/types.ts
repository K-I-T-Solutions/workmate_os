export type AssetType =
  | "workstation" | "laptop" | "server" | "network" | "storage"
  | "printer" | "phone" | "mobile" | "peripheral" | "other"
export type AssetStatus = "active" | "in_repair" | "in_stock" | "retired"
export type LicenseType = "subscription" | "perpetual" | "volume" | "oem"

export interface CustomerAsset {
  id: string
  asset_tag: string
  name: string
  asset_type: AssetType
  status: AssetStatus
  customer_id: string
  customer_name: string | null
  contact_id: string | null
  contract_id: string | null
  contract_number: string | null
  manufacturer: string | null
  model: string | null
  serial_number: string | null
  hostname: string | null
  ip_address: string | null
  mac_address: string | null
  operating_system: string | null
  location: string | null
  purchase_date: string | null
  purchase_price: number | string | null
  warranty_until: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export type AssetPayload = Partial<Omit<CustomerAsset, "id" | "asset_tag" | "customer_name" | "contract_number" | "created_at" | "updated_at">>

export interface SoftwareLicense {
  id: string
  product_name: string
  vendor: string | null
  license_type: LicenseType
  customer_id: string
  customer_name: string | null
  asset_id: string | null
  asset_name: string | null
  contract_id: string | null
  license_key: string | null
  seats: number
  seats_used: number | null
  valid_from: string | null
  valid_until: string | null
  auto_renew: boolean
  cost_price: number | string | null
  sale_price: number | string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export type LicensePayload = Partial<Omit<SoftwareLicense, "id" | "customer_name" | "asset_name" | "created_at" | "updated_at">>

export interface Paged<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

export interface ExpiringItem {
  kind: "warranty" | "license"
  id: string
  name: string
  customer_id: string
  customer_name: string | null
  expires_on: string
  days_left: number
  auto_renew: boolean
}
