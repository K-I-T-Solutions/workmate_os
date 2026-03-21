export type CustomerType = 'creator' | 'individual' | 'business' | 'government';
export type CustomerStatus = 'active' | 'inactive' | 'lead' | 'blocked';
export type PipelineStage = 'new_lead' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';

export interface Customer {
  id: string;
  customer_number: string | null;
  name: string;
  type: CustomerType | null;
  email: string | null;
  phone: string | null;
  tax_id: string | null;
  website: string | null;
  notes: string | null;
  status: CustomerStatus;
  pipeline_stage: PipelineStage | null;

  // Address fields
  street: string | null;
  zip_code: string | null;
  city: string | null;
  country: string | null;

  created_at: string;
  updated_at: string;
}

export interface CsvImportResult {
  imported: number;
  skipped: number;
  errors: string[];
  preview?: Record<string, string>[] | null;
}
