"use client"

import { useEffect, useState } from "react"
import { financeService } from "@/lib/finance/service"
import type { BankAccount, BankTransaction, ExpenseKpi } from "@/lib/finance/types"
import { AccountsTab } from "./accounts-tab"
import { TransactionsTab } from "./transactions-tab"
import { ExpensesTab } from "./expenses-tab"

type Tab = "overview" | "transactions" | "expenses" | "accounts"

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Übersicht" },
  { id: "transactions", label: "Transaktionen" },
  { id: "expenses", label: "Ausgaben" },
  { id: "accounts", label: "Konten" },
]

function fmt(n: number) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(n)
}

function StatKachel({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-muted-foreground">{sub}</p>}
    </div>
  )
}

const CATEGORY_LABELS: Record<string, string> = {
  travel: "Reise", material: "Material", software: "Software",
  hardware: "Hardware", consulting: "Beratung", marketing: "Marketing",
  office: "Büro", training: "Training", other: "Sonstiges",
}

const MONTHS_SHORT = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

function MonthlyChart({ transactions }: { transactions: BankTransaction[] }) {
  const year = new Date().getFullYear()
  const currentMonth = new Date().getMonth()

  const monthly = Array.from({ length: currentMonth + 1 }, (_, i) => {
    const prefix = `${year}-${String(i + 1).padStart(2, "0")}`
    const inMonth = transactions.filter(t => t.transaction_date.startsWith(prefix))
    const income = inMonth
      .filter(t => t.transaction_type === "income" || t.transaction_type === "interest")
      .reduce((s, t) => s + parseFloat(t.amount || "0"), 0)
    const expense = inMonth
      .filter(t => t.transaction_type === "expense" || t.transaction_type === "fee")
      .reduce((s, t) => s + parseFloat(t.amount || "0"), 0)
    return { label: MONTHS_SHORT[i], income, expense }
  })

  const max = Math.max(...monthly.flatMap(m => [m.income, m.expense]), 1)
  const hasData = monthly.some(m => m.income > 0 || m.expense > 0)

  if (!hasData) {
    return <p className="text-sm text-muted-foreground">Keine Transaktionsdaten für {year}.</p>
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1.5"><span className="h-2 w-3 rounded-sm bg-green-500/70 inline-block" />Einnahmen</span>
        <span className="flex items-center gap-1.5"><span className="h-2 w-3 rounded-sm bg-destructive/60 inline-block" />Ausgaben</span>
      </div>
      <div className="flex items-end gap-1.5 h-28">
        {monthly.map((m) => (
          <div key={m.label} className="flex-1 flex flex-col items-center gap-0.5">
            <div className="w-full flex items-end gap-0.5 h-20">
              <div
                className="flex-1 rounded-t bg-green-500/70 min-h-[2px] transition-all"
                style={{ height: `${(m.income / max) * 100}%` }}
                title={`Einnahmen ${fmt(m.income)}`}
              />
              <div
                className="flex-1 rounded-t bg-destructive/60 min-h-[2px] transition-all"
                style={{ height: `${(m.expense / max) * 100}%` }}
                title={`Ausgaben ${fmt(m.expense)}`}
              />
            </div>
            <span className="text-[9px] text-muted-foreground">{m.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function OverviewTab({ kpis, accounts, transactions }: { kpis: ExpenseKpi | null; accounts: BankAccount[]; transactions: BankTransaction[] }) {
  const activeAccounts = accounts.filter(a => a.is_active)
  const totalBalance = activeAccounts.reduce((s, a) => s + parseFloat(a.balance || "0"), 0)
  const totalExpenses = kpis ? parseFloat(kpis.total || "0") : 0

  const topCategories = kpis
    ? Object.entries(kpis.by_category)
        .map(([cat, val]) => [cat, parseFloat(val || "0")] as [string, number])
        .filter(([, v]) => v > 0)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5)
    : []

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <StatKachel label="Gesamtguthaben" value={fmt(totalBalance)} sub={`${activeAccounts.length} aktive Konten`} />
        <StatKachel label="Gesamtausgaben" value={kpis ? fmt(totalExpenses) : "–"} />
        <StatKachel label="Konten gesamt" value={String(accounts.length)} />
      </div>

      {/* Monthly income/expense chart */}
      <div className="rounded-lg border bg-card p-5">
        <h2 className="mb-4 text-sm font-medium text-muted-foreground">Einnahmen vs. Ausgaben {new Date().getFullYear()}</h2>
        <MonthlyChart transactions={transactions} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-card p-5">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">Konten</h2>
          {activeAccounts.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Konten vorhanden.</p>
          ) : (
            <div className="space-y-3">
              {activeAccounts.map(acc => (
                <div key={acc.id} className="flex items-center justify-between text-sm">
                  <div>
                    <p className="font-medium">{acc.account_name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{acc.bank_name ?? acc.account_type}</p>
                  </div>
                  <p className={`font-semibold tabular-nums ${parseFloat(acc.balance) < 0 ? "text-destructive" : ""}`}>
                    {fmt(parseFloat(acc.balance || "0"))}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-lg border bg-card p-5">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">Ausgaben nach Kategorie</h2>
          {topCategories.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Ausgaben vorhanden.</p>
          ) : (
            <div className="space-y-3">
              {topCategories.map(([cat, val]) => {
                const max = topCategories[0][1] as number
                const pct = max > 0 ? ((val as number) / max) * 100 : 0
                return (
                  <div key={cat} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span>{CATEGORY_LABELS[cat] ?? cat}</span>
                      <span className="font-medium tabular-nums">{fmt(val as number)}</span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-muted">
                      <div className="h-1.5 rounded-full bg-primary" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export function FinanceDashboard() {
  const [tab, setTab] = useState<Tab>("overview")
  const [accounts, setAccounts] = useState<BankAccount[]>([])
  const [kpis, setKpis] = useState<ExpenseKpi | null>(null)
  const [transactions, setTransactions] = useState<BankTransaction[]>([])

  function reloadAccounts() {
    financeService.listAccounts().then(setAccounts).catch(() => {})
  }
  function reloadKpis() {
    financeService.getExpenseKpis().then(setKpis).catch(() => {})
  }

  useEffect(() => {
    reloadAccounts()
    reloadKpis()
    const year = new Date().getFullYear()
    financeService.listTransactions({ limit: 500 } as Parameters<typeof financeService.listTransactions>[0])
      .then(setTransactions)
      .catch(() => {})
  }, [])

  return (
    <div className="space-y-6 px-8 py-6">
      <h1 className="text-xl font-semibold">Finanzen</h1>

      <div className="flex gap-1 border-b">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === t.id
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "overview" && <OverviewTab kpis={kpis} accounts={accounts} transactions={transactions} />}
      {tab === "transactions" && <TransactionsTab accounts={accounts} />}
      {tab === "expenses" && <ExpensesTab onKpiRefresh={reloadKpis} />}
      {tab === "accounts" && <AccountsTab accounts={accounts} onRefresh={reloadAccounts} />}
    </div>
  )
}
