import { apiClient } from '@/services/api/client';
import type {
  InvoiceStatistics,
  ExpenseKpis,
  FinanceOverview,
  FinanceFilters,
} from '../types';

/**
 * Get invoice statistics (revenue, outstanding, overdue)
 */
export async function getInvoiceStatistics(
  filters?: FinanceFilters
): Promise<InvoiceStatistics> {
  const params: Record<string, any> = {};

  if (filters?.customer_id) params.customer_id = filters.customer_id;

  const response = await apiClient.get('/api/backoffice/invoices/statistics', {
    params,
  });

  return response.data;
}

/**
 * Get expense KPIs (total expenses and breakdown by category)
 */
export async function getExpenseKpis(
  filters?: FinanceFilters
): Promise<ExpenseKpis> {
  const params: Record<string, any> = {};

  if (filters?.from_date) params.from_date = filters.from_date;
  if (filters?.to_date) params.to_date = filters.to_date;
  if (filters?.project_id) params.project_id = filters.project_id;

  const response = await apiClient.get('/api/backoffice/finance/kpis/expenses', {
    params,
  });

  return response.data;
}

/**
 * Get combined finance overview (invoices + expenses)
 */
export async function getFinanceOverview(
  filters?: FinanceFilters
): Promise<FinanceOverview> {
  // Fetch both invoice stats and expense KPIs in parallel
  const [invoiceStats, expenseKpis] = await Promise.all([
    getInvoiceStatistics(filters),
    getExpenseKpis(filters),
  ]);

  // Calculate profit and profit margin
  const profit = invoiceStats.total_revenue - Number(expenseKpis.total);
  const profit_margin =
    invoiceStats.total_revenue > 0
      ? (profit / invoiceStats.total_revenue) * 100
      : 0;

  // Combine data into finance overview
  const overview: FinanceOverview = {
    // Revenue
    total_revenue: invoiceStats.total_revenue,
    outstanding_revenue: invoiceStats.outstanding_amount,
    overdue_revenue: invoiceStats.overdue_amount,

    // Expenses
    total_expenses: Number(expenseKpis.total),

    // Calculated
    profit,
    profit_margin,

    // Breakdown
    invoice_count: invoiceStats.total_count,
    invoices_by_status: invoiceStats.by_status,
    expenses_by_category: expenseKpis.by_category,
  };

  return overview;
}
