export interface Contact {
  id: string;
  customer_id: string;
  firstname: string;
  lastname: string;
  email: string | null;
  phone: string | null;
  mobile: string | null;
  position: string | null;
  department: string | null;
  is_primary: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
