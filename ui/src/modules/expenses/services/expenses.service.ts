/**
 * Expenses API Service
 */
import axios from "axios";
import type {
  ExpenseCreate,
  ExpenseUpdate,
  ExpenseRead,
  ExpenseListResponse,
  ExpenseKpiResponse,
  ExpenseFilters,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const BASE_URL = `${API_BASE}/api/backoffice/finance`;

/**
 * Create a new expense
 */
export async function createExpense(
  data: ExpenseCreate
): Promise<ExpenseRead> {
  const response = await axios.post<ExpenseRead>(`${BASE_URL}/expenses`, data);
  return response.data;
}

/**
 * Get list of expenses with optional filters
 */
export async function listExpenses(
  filters?: ExpenseFilters
): Promise<ExpenseListResponse> {
  const params = new URLSearchParams();

  if (filters?.title) params.append("title", filters.title);
  if (filters?.category) params.append("category", filters.category);
  if (filters?.project_id) params.append("project_id", filters.project_id);
  if (filters?.invoice_id) params.append("invoice_id", filters.invoice_id);
  if (filters?.from_date) params.append("from_date", filters.from_date);
  if (filters?.to_date) params.append("to_date", filters.to_date);
  if (filters?.limit) params.append("limit", filters.limit.toString());
  if (filters?.offset) params.append("offset", filters.offset.toString());

  const response = await axios.get<ExpenseListResponse>(
    `${BASE_URL}/expenses?${params.toString()}`
  );
  return response.data;
}

/**
 * Get a single expense by ID
 */
export async function getExpense(id: string): Promise<ExpenseRead> {
  const response = await axios.get<ExpenseRead>(`${BASE_URL}/expenses/${id}`);
  return response.data;
}

/**
 * Update an expense
 */
export async function updateExpense(
  id: string,
  data: ExpenseUpdate
): Promise<ExpenseRead> {
  const response = await axios.patch<ExpenseRead>(
    `${BASE_URL}/expenses/${id}`,
    data
  );
  return response.data;
}

/**
 * Delete an expense
 */
export async function deleteExpense(id: string): Promise<void> {
  await axios.delete(`${BASE_URL}/expenses/${id}`);
}

/**
 * Get expense KPIs
 */
export async function getExpenseKpis(
  filters?: Omit<ExpenseFilters, "limit" | "offset">
): Promise<ExpenseKpiResponse> {
  const params = new URLSearchParams();

  if (filters?.title) params.append("title", filters.title);
  if (filters?.category) params.append("category", filters.category);
  if (filters?.project_id) params.append("project_id", filters.project_id);
  if (filters?.from_date) params.append("from_date", filters.from_date);
  if (filters?.to_date) params.append("to_date", filters.to_date);

  const response = await axios.get<ExpenseKpiResponse>(
    `${BASE_URL}/kpis/expenses?${params.toString()}`
  );
  return response.data;
}
