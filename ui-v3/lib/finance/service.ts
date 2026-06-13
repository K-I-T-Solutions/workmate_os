import { apiClient } from "@/lib/api/client"
import type {
  BankAccount, BankAccountCreate, BankAccountUpdate,
  BankTransaction, BankTransactionCreate, BankTransactionUpdate,
  Expense, ExpenseCreate, ExpenseUpdate, ExpenseKpi,
  TransactionListParams, ExpenseListParams,
} from "./types"

export const financeService = {
  // Bank Accounts
  async listAccounts(): Promise<BankAccount[]> {
    const { data } = await apiClient.get("/api/backoffice/finance/bank-accounts")
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async getAccount(id: string): Promise<BankAccount> {
    const { data } = await apiClient.get(`/api/backoffice/finance/bank-accounts/${id}`)
    return data
  },
  async createAccount(payload: BankAccountCreate): Promise<BankAccount> {
    const { data } = await apiClient.post("/api/backoffice/finance/bank-accounts", payload)
    return data
  },
  async updateAccount(id: string, payload: BankAccountUpdate): Promise<BankAccount> {
    const { data } = await apiClient.patch(`/api/backoffice/finance/bank-accounts/${id}`, payload)
    return data
  },
  async deleteAccount(id: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/finance/bank-accounts/${id}`)
  },

  // Bank Transactions
  async listTransactions(params?: TransactionListParams): Promise<BankTransaction[]> {
    const { data } = await apiClient.get("/api/backoffice/finance/bank-transactions", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async getTransaction(id: string): Promise<BankTransaction> {
    const { data } = await apiClient.get(`/api/backoffice/finance/bank-transactions/${id}`)
    return data
  },
  async createTransaction(payload: BankTransactionCreate): Promise<BankTransaction> {
    const { data } = await apiClient.post("/api/backoffice/finance/bank-transactions", payload)
    return data
  },
  async updateTransaction(id: string, payload: BankTransactionUpdate): Promise<BankTransaction> {
    const { data } = await apiClient.patch(`/api/backoffice/finance/bank-transactions/${id}`, payload)
    return data
  },
  async deleteTransaction(id: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/finance/bank-transactions/${id}`)
  },

  // Expenses
  async listExpenses(params?: ExpenseListParams): Promise<Expense[]> {
    const { data } = await apiClient.get("/api/backoffice/finance/expenses", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async getExpense(id: string): Promise<Expense> {
    const { data } = await apiClient.get(`/api/backoffice/finance/expenses/${id}`)
    return data
  },
  async createExpense(payload: ExpenseCreate): Promise<Expense> {
    const { data } = await apiClient.post("/api/backoffice/finance/expenses", payload)
    return data
  },
  async updateExpense(id: string, payload: ExpenseUpdate): Promise<Expense> {
    const { data } = await apiClient.patch(`/api/backoffice/finance/expenses/${id}`, payload)
    return data
  },
  async deleteExpense(id: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/finance/expenses/${id}`)
  },

  // KPIs
  async getExpenseKpis(): Promise<ExpenseKpi> {
    const { data } = await apiClient.get("/api/backoffice/finance/kpis/expenses")
    return data
  },
}
