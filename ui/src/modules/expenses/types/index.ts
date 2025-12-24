/**
 * Expenses Module Types
 * Generated from backend/app/modules/backoffice/finance/schemas.py
 */

export enum ExpenseCategory {
  TRAVEL = "travel",
  MATERIAL = "material",
  SOFTWARE = "software",
  HARDWARE = "hardware",
  CONSULTING = "consulting",
  MARKETING = "marketing",
  OFFICE = "office",
  TRAINING = "training",
  OTHER = "other",
}

export const ExpenseCategoryLabels: Record<ExpenseCategory, string> = {
  [ExpenseCategory.TRAVEL]: "Reisekosten",
  [ExpenseCategory.MATERIAL]: "Material",
  [ExpenseCategory.SOFTWARE]: "Software",
  [ExpenseCategory.HARDWARE]: "Hardware",
  [ExpenseCategory.CONSULTING]: "Beratung",
  [ExpenseCategory.MARKETING]: "Marketing",
  [ExpenseCategory.OFFICE]: "Büro",
  [ExpenseCategory.TRAINING]: "Schulung",
  [ExpenseCategory.OTHER]: "Sonstiges",
};

export interface ExpenseBase {
  title: string;
  category: ExpenseCategory;
  amount: number;
  description: string;
  receipt_path?: string | null;
  note?: string | null;
  is_billable: boolean;
  project_id?: string | null;
  invoice_id?: string | null;
}

export interface ExpenseCreate extends ExpenseBase {}

export interface ExpenseUpdate extends Partial<ExpenseBase> {}

export interface ExpenseRead extends ExpenseBase {
  id: string;
  created_at: string;
  updated_at: string;
  is_invoiced: boolean;
}

export interface ExpenseListResponse {
  items: ExpenseRead[];
  total: number;
}

export interface ExpenseKpiResponse {
  total: number;
  by_category: Record<ExpenseCategory, number>;
}

export interface ExpenseFilters {
  title?: string;
  category?: ExpenseCategory;
  project_id?: string;
  invoice_id?: string;
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
}
