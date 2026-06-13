export type CustomerType = "creator" | "individual" | "business" | "government"
export type CustomerStatus = "active" | "inactive" | "lead" | "blocked"
export type PipelineStage = "new_lead" | "qualified" | "proposal" | "negotiation" | "won" | "lost"
export type ActivityType = "call" | "email" | "onsite" | "remote" | "note" | "system"

export interface Customer {
  id: string
  customer_number: string | null
  name: string
  type: CustomerType | null
  email: string | null
  phone: string | null
  tax_id: string | null
  website: string | null
  notes: string | null
  status: CustomerStatus
  pipeline_stage: PipelineStage | null
  street: string | null
  zip_code: string | null
  city: string | null
  country: string | null
  created_at: string
  updated_at: string
  contacts?: Contact[]
}

export interface Contact {
  id: string
  customer_id: string
  firstname: string
  lastname: string
  email: string | null
  phone: string | null
  mobile: string | null
  position: string | null
  department: string | null
  is_primary: boolean
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CrmActivity {
  id: string
  customer_id: string
  contact_id?: string | null
  type: ActivityType
  description: string
  occurred_at: string
  created_at: string
}

export interface CreateCrmActivity {
  customer_id: string
  contact_id?: string | null
  type: ActivityType
  description: string
  occurred_at?: string
}

export interface CrmStats {
  total_customers: number
  active_customers: number
  leads: number
}

export interface ContactWithCustomer extends Contact {
  customer_name?: string
}

export interface CsvImportResult {
  imported: number
  skipped: number
  errors: string[]
  preview?: Record<string, string>[] | null
}
