"use client"

import { useEffect, useState } from "react"
import { Users, FileText, TrendingUp, PiggyBank, Clock } from "lucide-react"
import { StatCard } from "@/components/stat-card"
import { FinanzenCard, AktivitaetCard, SchnellzugriffCard, TicketsCard } from "@/components/dashboard-panels"
import { useAuth } from "@/components/providers/auth-provider"
import { apiClient } from "@/lib/api/client"

interface CrmStats {
  total_customers: number
  active_customers: number
  leads: number
}

interface InvoiceStats {
  total_count: number
  total_revenue: string
  outstanding_amount: string
  paid_count: number
  overdue_count: number
}

interface TimeStats {
  hours_today: number
  hours_week: number
  active_timer?: boolean
}

export function DashboardContent() {
  const { user } = useAuth()
  const [crmStats, setCrmStats] = useState<CrmStats | null>(null)
  const [invoiceStats, setInvoiceStats] = useState<InvoiceStats | null>(null)
  const [timeStats, setTimeStats] = useState<TimeStats | null>(null)

  const today = new Date().toLocaleDateString("de-DE", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  })

  useEffect(() => {
    apiClient.get("/api/backoffice/crm/stats").then((r) => setCrmStats(r.data)).catch(() => {})
    apiClient.get("/api/backoffice/invoices/statistics").then((r) => setInvoiceStats(r.data)).catch(() => {})
    apiClient.get("/api/backoffice/time-tracking/stats").then((r) => setTimeStats(r.data)).catch(() => {})
  }, [])

  const formatEur = (val: string | undefined) => {
    if (!val) return "–"
    return parseFloat(val).toLocaleString("de-DE", { style: "currency", currency: "EUR" })
  }

  const fmtHours = (h: number | undefined) =>
    h != null ? `${h.toFixed(1).replace(".", ",")} Std.` : "–"

  const firstName = user?.name?.split(" ")[0] ?? "zurück"

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-8">
        <h1 className="font-heading text-2xl font-bold tracking-tight text-foreground">
          Willkommen zurück, {firstName}.
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{today}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        <StatCard
          label="Kunden"
          value={crmStats ? String(crmStats.total_customers) : "–"}
          subtitle={crmStats ? `${crmStats.active_customers} aktiv · ${crmStats.leads} Leads` : "Laden…"}
          icon={Users}
          accent="blue"
          trend={[2, 3, 3, 2, 4, 3, crmStats?.total_customers ?? 4]}
        />
        <StatCard
          label="Rechnungen"
          value={invoiceStats ? String(invoiceStats.total_count) : "–"}
          subtitle={invoiceStats ? `${invoiceStats.paid_count} bezahlt · ${invoiceStats.overdue_count} überfällig` : "Laden…"}
          icon={FileText}
          accent="orange"
          trend={[1, 1, 2, 1, 2, 3, invoiceStats?.total_count ?? 3]}
        />
        <StatCard
          label="Umsatz"
          value={invoiceStats ? formatEur(invoiceStats.total_revenue) : "–"}
          subtitle="Gesamt (bezahlt)"
          icon={TrendingUp}
          accent="green"
          trend={[0, 20, 40, 30, 80, 100, parseFloat(invoiceStats?.total_revenue ?? "0")]}
        />
        <StatCard
          label="Offen"
          value={invoiceStats ? formatEur(invoiceStats.outstanding_amount) : "–"}
          subtitle="Offene Forderungen"
          icon={PiggyBank}
          accent="emerald"
          trend={[0, 10, 30, 50, 70, 110, parseFloat(invoiceStats?.outstanding_amount ?? "0")]}
        />
        <StatCard
          label="Heute gearbeitet"
          value={timeStats ? fmtHours(timeStats.hours_today) : "–"}
          subtitle={timeStats
            ? `${fmtHours(timeStats.hours_week)} diese Woche${timeStats.active_timer ? " · Timer läuft" : ""}`
            : "Laden…"}
          icon={Clock}
          accent="violet"
          trend={[0, 1, 2, 1.5, 3, 4, timeStats?.hours_today ?? 0]}
        />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <FinanzenCard invoiceStats={invoiceStats} />
        <AktivitaetCard />
        <TicketsCard />
        <SchnellzugriffCard />
      </div>
    </div>
  )
}
