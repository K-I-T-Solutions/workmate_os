// Core Types
export interface Employee {
  id: string;
  employee_code: string;
  first_name: string | null;
  last_name: string | null;
  email: string;
  phone: string | null;
  status: string;
  department_id: string | null;
  role_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: string;
  name: string;
  type: string | null;
  email: string | null;
  phone: string | null;
  city: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  title: string;
  description: string | null;
  status: string;
  customer_id: string;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  total: string;
  subtotal: string;
  tax_amount: string;
  status: string;
  issued_date: string | null;
  due_date: string | null;
  paid_amount: string;
  outstanding_amount: string;
  is_paid: boolean;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface Reminder {
  id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: string;
  status: string;
  owner_id: string;
  is_overdue: boolean | null;
  days_until_due: number | null;
  created_at: string;
}

// Statistics
export interface DashboardStats {
  employees_count: number;
  customers_count: number;
  projects_count: number;
  invoices_count: number;
  reminders_count: number;
}
