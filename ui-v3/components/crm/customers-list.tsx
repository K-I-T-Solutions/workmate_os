"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Plus, Upload, GitMerge, Search, Trash2, ChevronLeft, ChevronRight } from "lucide-react"
import { crmService } from "@/lib/crm/service"
import type { Customer, CustomerStatus } from "@/lib/crm/types"
import { cn } from "@/lib/utils"
import { useAuth } from "@/components/providers/auth-provider"

const STATUS_LABELS: Record<CustomerStatus, string> = {
  active: "Aktiv",
  inactive: "Inaktiv",
  lead: "Lead",
  blocked: "Gesperrt",
}

const STATUS_COLORS: Record<CustomerStatus, string> = {
  active: "bg-green-500/15 text-green-400",
  inactive: "bg-slate-500/15 text-slate-400",
  lead: "bg-blue-500/15 text-blue-400",
  blocked: "bg-red-500/15 text-red-400",
}

const PAGE_SIZE = 20

export function CustomersList() {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<CustomerStatus | "">("")
  const [page, setPage] = useState(0)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await crmService.getCustomers({
        search: search || undefined,
        status: statusFilter || undefined,
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
      })
      setCustomers(data)
    } catch (e: any) {
      setError(e?.message ?? "Fehler beim Laden")
    } finally {
      setLoading(false)
    }
  }, [search, statusFilter, page])

  useEffect(() => { load() }, [load])

  async function handleDelete() {
    if (!deleteId) return
    await crmService.deleteCustomer(deleteId)
    setDeleteId(null)
    load()
  }

  return (
    <div className="px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-foreground">Kunden</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">{customers.length} Einträge</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.push("/crm/pipeline")}
            className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <GitMerge className="h-4 w-4" />
            Pipeline
          </button>
          <button className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground">
            <Upload className="h-4 w-4" />
            Importieren
          </button>
          {hasPermission("backoffice.crm.write") && (
            <button
              onClick={() => router.push("/crm/customers/new")}
              className="flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              <Plus className="h-4 w-4" />
              Neuer Kunde
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value as CustomerStatus | ""); setPage(0) }}
          className="rounded-lg border border-border bg-secondary px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="">Alle Status</option>
          {(Object.keys(STATUS_LABELS) as CustomerStatus[]).map((s) => (
            <option key={s} value={s}>{STATUS_LABELS[s]}</option>
          ))}
        </select>
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Name, E-Mail oder Kundennummer..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0) }}
            className="w-full rounded-lg border border-border bg-secondary py-2 pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border overflow-hidden">
        {error && (
          <div className="px-4 py-3 text-sm text-destructive bg-destructive/10 border-b border-border">{error}</div>
        )}
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-secondary/50">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Kunde</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground hidden md:table-cell">Kontakt</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Status</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground hidden lg:table-cell">Erstellt</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">Laden…</td>
              </tr>
            )}
            {!loading && customers.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">Keine Kunden gefunden.</td>
              </tr>
            )}
            {!loading && customers.map((c) => (
              <tr
                key={c.id}
                onClick={() => router.push(`/crm/customers/${c.id}`)}
                className="border-b border-border/50 cursor-pointer transition-colors hover:bg-secondary/50 last:border-0"
              >
                <td className="px-4 py-3">
                  <p className="font-medium text-foreground">{c.name}</p>
                  {c.customer_number && (
                    <p className="text-xs text-muted-foreground">{c.customer_number}</p>
                  )}
                </td>
                <td className="px-4 py-3 hidden md:table-cell">
                  <p className="text-muted-foreground">{c.email ?? "—"}</p>
                  <p className="text-xs text-muted-foreground">{c.phone ?? ""}</p>
                </td>
                <td className="px-4 py-3">
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", STATUS_COLORS[c.status])}>
                    {STATUS_LABELS[c.status]}
                  </span>
                </td>
                <td className="px-4 py-3 hidden lg:table-cell text-muted-foreground">
                  {new Date(c.created_at).toLocaleDateString("de-DE")}
                </td>
                <td className="px-4 py-3 text-right">
                  {hasPermission("backoffice.crm.delete") && (
                    <button
                      onClick={(e) => { e.stopPropagation(); setDeleteId(c.id) }}
                      className="rounded p-1 text-muted-foreground opacity-0 transition-opacity hover:text-destructive group-hover:opacity-100 [tr:hover_&]:opacity-100"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {customers.length > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{page * PAGE_SIZE + 1}–{page * PAGE_SIZE + customers.length}</span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="rounded-lg border border-border p-1.5 transition-colors hover:bg-secondary disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={customers.length < PAGE_SIZE}
              className="rounded-lg border border-border p-1.5 transition-colors hover:bg-secondary disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-6">
            <h2 className="font-heading text-lg font-semibold text-foreground">Kunden löschen?</h2>
            <p className="mt-1 text-sm text-muted-foreground">Diese Aktion kann nicht rückgängig gemacht werden.</p>
            <div className="mt-5 flex gap-3">
              <button
                onClick={() => setDeleteId(null)}
                className="flex-1 rounded-lg border border-border bg-secondary py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                Abbrechen
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 rounded-lg bg-destructive py-2 text-sm font-medium text-white transition-colors hover:bg-destructive/90"
              >
                Löschen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
