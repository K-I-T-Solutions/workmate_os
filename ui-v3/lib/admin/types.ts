export interface SystemSettings {
  id: string
  company_name: string | null
  company_legal: string | null
  tax_number: string | null
  registration_number: string | null
  address_street: string | null
  address_zip: string | null
  address_city: string | null
  address_country: string | null
  company_email: string | null
  company_phone: string | null
  company_website: string | null
  default_timezone: string | null
  default_language: string | null
  default_currency: string | null
  date_format: string | null
  working_hours_per_day: number | null
  working_days_per_week: number | null
  vacation_days_per_year: number | null
  weekend_saturday: boolean
  weekend_sunday: boolean
  maintenance_mode: boolean
  allow_registration: boolean
  require_email_verification: boolean
  email_enabled: boolean
  smtp_host: string | null
  smtp_port: number | null
  smtp_username: string | null
  smtp_password: string | null
  smtp_from_email: string | null
  smtp_from_name: string | null
  smtp_use_tls: boolean
  smtp_use_ssl: boolean
  created_at: string
  updated_at: string
}

export type SystemSettingsUpdate = Partial<Omit<SystemSettings, "id" | "created_at" | "updated_at">>

export interface Department {
  id: string
  name: string
  code: string
  description: string | null
  manager_id: string | null
  created_at: string
}

export interface DepartmentCreate {
  name: string
  code: string
  description?: string | null
}

export interface Role {
  id: string
  name: string
  description: string | null
  permissions_json: string | null
  keycloak_id: string | null
}

export interface RoleCreate {
  name: string
  description?: string | null
  permissions_json?: string | null
}

export interface AuditLog {
  id: string
  entity_type: string
  entity_id: string | null
  action: string
  old_values: Record<string, unknown> | null
  new_values: Record<string, unknown> | null
  user_id: string | null
  timestamp: string
  ip_address: string | null
}
