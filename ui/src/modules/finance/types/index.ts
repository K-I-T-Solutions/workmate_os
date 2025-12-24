// Finance Module Types

export interface InvoiceStatistics {
  total_count: number;
  total_revenue: number;
  outstanding_amount: number;
  overdue_amount: number;
  by_status: Record<string, number>;
}

export interface ExpenseKpis {
  total: number;
  by_category: Record<string, number>;
}

export interface FinanceOverview {
  // Revenue (from invoices)
  total_revenue: number;
  outstanding_revenue: number;
  overdue_revenue: number;

  // Expenses
  total_expenses: number;

  // Calculated
  profit: number;
  profit_margin: number;

  // Invoices breakdown
  invoice_count: number;
  invoices_by_status: Record<string, number>;

  // Expenses breakdown
  expenses_by_category: Record<string, number>;
}

export interface TimeBasedMetrics {
  month: string;
  revenue: number;
  expenses: number;
  profit: number;
}

export interface FinanceFilters {
  from_date?: string;
  to_date?: string;
  customer_id?: string;
  project_id?: string;
}
