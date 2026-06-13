"use client"

import { useEffect, useState, useRef, useCallback, useMemo } from "react"
import { useRouter } from "next/navigation"
import { crmService } from "@/lib/crm/service"
import { invoiceService } from "@/lib/invoices/service"
import { projectService } from "@/lib/projects/service"
import { supportService } from "@/lib/support/service"
import type { Customer, ContactWithCustomer } from "@/lib/crm/types"
import type { Invoice } from "@/lib/invoices/types"
import type { Project } from "@/lib/projects/types"
import type { Ticket } from "@/lib/support/types"
import { Search, Users, UserCircle, FileText, FolderKanban, MessageSquare, ArrowRight, X, Loader2 } from "lucide-react"

interface SearchResult {
  type: "customer" | "contact" | "invoice" | "project" | "ticket"
  id: string
  title: string
  subtitle: string
  href: string
}

const TYPE_META: Record<SearchResult["type"], { label: string; icon: React.ReactNode; color: string }> = {
  customer: { label: "Kunden",     icon: <Users       className="h-3.5 w-3.5" />, color: "text-blue-500" },
  contact:  { label: "Kontakte",   icon: <UserCircle  className="h-3.5 w-3.5" />, color: "text-cyan-500" },
  invoice:  { label: "Rechnungen", icon: <FileText    className="h-3.5 w-3.5" />, color: "text-emerald-500" },
  project:  { label: "Projekte",   icon: <FolderKanban className="h-3.5 w-3.5" />, color: "text-violet-500" },
  ticket:   { label: "Tickets",    icon: <MessageSquare className="h-3.5 w-3.5" />, color: "text-orange-500" },
}

interface LocalCache {
  invoices: Invoice[]
  projects: Project[]
  tickets: Ticket[]
}

function normalize(s: string) {
  return s.toLowerCase().replace(/\s+/g, " ").trim()
}

function match(q: string, ...fields: (string | null | undefined)[]) {
  const n = normalize(q)
  return fields.some(f => f && normalize(f).includes(n))
}

function toArr<T>(data: T | { items?: T } | { customers?: T }): T {
  if (Array.isArray(data)) return data as T
  const d = data as Record<string, unknown>
  return (d.items ?? d.customers ?? d) as T
}

export function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [query, setQuery] = useState("")
  const [localCache, setLocalCache] = useState<LocalCache | null>(null)
  const [apiResults, setApiResults] = useState<{ customers: Customer[]; contacts: ContactWithCustomer[] }>({ customers: [], contacts: [] })
  const [loadingLocal, setLoadingLocal] = useState(false)
  const [loadingApi, setLoadingApi] = useState(false)
  const [selected, setSelected] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  // Prefetch local data (invoices, projects, tickets) when palette opens
  useEffect(() => {
    if (!open) return
    setQuery("")
    setApiResults({ customers: [], contacts: [] })
    setSelected(0)
    setTimeout(() => inputRef.current?.focus(), 10)
    if (localCache) return
    setLoadingLocal(true)
    Promise.all([
      invoiceService.list({ limit: 200 }).then(r => toArr<Invoice[]>(r as unknown as Invoice[] | { items?: Invoice[] })).catch(() => [] as Invoice[]),
      projectService.list().catch(() => [] as Project[]),
      supportService.list({ limit: 100 }).then(r => (r as unknown as { items?: Ticket[] }).items ?? []).catch(() => [] as Ticket[]),
    ]).then(([invoices, projects, tickets]) => {
      setLocalCache({ invoices, projects, tickets })
    }).finally(() => setLoadingLocal(false))
  }, [open]) // eslint-disable-line react-hooks/exhaustive-deps

  // Server-side search for customers + contacts (debounced 300ms)
  useEffect(() => {
    const q = query.trim()
    if (q.length < 1) {
      setApiResults({ customers: [], contacts: [] })
      return
    }
    setLoadingApi(true)
    const t = setTimeout(async () => {
      try {
        const [rawCustomers, rawContacts] = await Promise.all([
          crmService.getCustomers({ search: q, limit: 8 }).catch(() => [] as Customer[]),
          crmService.getAllContacts({ search: q, limit: 5 }).catch(() => [] as ContactWithCustomer[]),
        ])
        setApiResults({
          customers: toArr<Customer[]>(rawCustomers as unknown as Customer[] | { items?: Customer[] }),
          contacts: toArr<ContactWithCustomer[]>(rawContacts as unknown as ContactWithCustomer[] | { items?: ContactWithCustomer[] }),
        })
      } finally {
        setLoadingApi(false)
      }
    }, 300)
    return () => { clearTimeout(t); setLoadingApi(false) }
  }, [query])

  // Close on Escape
  useEffect(() => {
    if (!open) return
    function onKey(e: KeyboardEvent) { if (e.key === "Escape") onClose() }
    document.addEventListener("keydown", onKey)
    return () => document.removeEventListener("keydown", onKey)
  }, [open, onClose])

  // Build flat result list
  const items = useMemo((): SearchResult[] => {
    const q = query.trim()
    if (!q) return []
    const out: SearchResult[] = []

    // --- server-side: customers ---
    for (const c of apiResults.customers) {
      out.push({
        type: "customer",
        id: c.id,
        title: c.name,
        subtitle: [c.customer_number, c.city, c.email].filter(Boolean).join(" · "),
        href: `/crm/customers/${c.id}`,
      })
    }

    // --- server-side: contacts ---
    for (const ct of apiResults.contacts) {
      const fullName = `${ct.firstname} ${ct.lastname}`.trim()
      out.push({
        type: "contact",
        id: ct.id,
        title: fullName,
        subtitle: [ct.position, (ct as ContactWithCustomer & { customer_name?: string }).customer_name].filter(Boolean).join(" · "),
        href: `/crm/customers/${ct.customer_id}`,
      })
    }

    // --- client-side: invoices ---
    if (localCache) {
      localCache.invoices
        .filter(i => match(q, i.invoice_number, i.customer?.name))
        .slice(0, 5)
        .forEach(i => out.push({
          type: "invoice",
          id: i.id,
          title: i.invoice_number,
          subtitle: [i.customer?.name, i.total ? parseFloat(i.total).toLocaleString("de-DE", { style: "currency", currency: "EUR" }) : undefined].filter(Boolean).join(" · "),
          href: `/invoices/${i.id}`,
        }))

      localCache.projects
        .filter(p => match(q, p.title, p.description))
        .slice(0, 5)
        .forEach(p => out.push({
          type: "project",
          id: p.id,
          title: p.title,
          subtitle: p.description?.slice(0, 60) ?? "",
          href: `/projects/${p.id}`,
        }))

      localCache.tickets
        .filter(t => match(q, t.title, t.ticket_number, t.description))
        .slice(0, 5)
        .forEach(t => out.push({
          type: "ticket",
          id: t.id,
          title: t.title,
          subtitle: [t.ticket_number, t.category].filter(Boolean).join(" · "),
          href: `/support/${t.id}`,
        }))
    }

    return out
  }, [query, apiResults, localCache])

  // Keyboard navigation
  useEffect(() => {
    if (!open) return
    function onKey(e: KeyboardEvent) {
      if (e.key === "ArrowDown") { e.preventDefault(); setSelected(s => Math.min(s + 1, items.length - 1)) }
      else if (e.key === "ArrowUp") { e.preventDefault(); setSelected(s => Math.max(s - 1, 0)) }
      else if (e.key === "Enter" && items[selected]) navigate(items[selected].href)
    }
    document.addEventListener("keydown", onKey)
    return () => document.removeEventListener("keydown", onKey)
  }, [open, items, selected]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { setSelected(0) }, [query])

  function navigate(href: string) { onClose(); router.push(href) }

  if (!open) return null

  const grouped: Partial<Record<SearchResult["type"], SearchResult[]>> = {}
  for (const r of items) {
    if (!grouped[r.type]) grouped[r.type] = []
    grouped[r.type]!.push(r)
  }
  const types = Object.keys(grouped) as SearchResult["type"][]

  const isLoading = loadingApi || (loadingLocal && !localCache)
  let cursor = 0

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]" onClick={onClose}>
      <div className="absolute inset-0 bg-black/50" />

      <div
        className="relative z-10 w-full max-w-xl rounded-2xl border border-border bg-card shadow-2xl overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* Input */}
        <div className="flex items-center gap-3 border-b border-border px-4 py-3.5">
          {isLoading
            ? <Loader2 className="h-4 w-4 shrink-0 text-muted-foreground animate-spin" />
            : <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
          }
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Kunden, Kontakte, Rechnungen, Projekte…"
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          {query && (
            <button onClick={() => setQuery("")} className="shrink-0 text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          )}
          <kbd className="hidden shrink-0 rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground sm:block">Esc</kbd>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto">
          {query.trim().length === 0 ? (
            <div className="py-10 text-center text-sm text-muted-foreground">Tippe um zu suchen</div>
          ) : items.length === 0 && !isLoading ? (
            <div className="py-10 text-center text-sm text-muted-foreground">Keine Ergebnisse für „{query}"</div>
          ) : (
            <div className="py-2">
              {types.map(type => {
                const meta = TYPE_META[type]
                const typeItems = grouped[type]!
                return (
                  <div key={type}>
                    <div className="flex items-center gap-2 px-4 py-1.5">
                      <span className={meta.color}>{meta.icon}</span>
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{meta.label}</span>
                    </div>
                    {typeItems.map(item => {
                      const idx = cursor++
                      const isSelected = idx === selected
                      return (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => navigate(item.href)}
                          onMouseEnter={() => setSelected(idx)}
                          className={`flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors ${isSelected ? "bg-muted" : "hover:bg-muted/50"}`}
                        >
                          <div className="flex-1 min-w-0">
                            <p className="truncate text-sm font-medium text-foreground">{item.title}</p>
                            {item.subtitle && <p className="truncate text-xs text-muted-foreground">{item.subtitle}</p>}
                          </div>
                          <ArrowRight className={`h-3.5 w-3.5 shrink-0 transition-opacity ${isSelected ? "opacity-60" : "opacity-0"}`} />
                        </button>
                      )
                    })}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="flex items-center gap-4 border-t border-border px-4 py-2.5 text-[10px] text-muted-foreground">
            <span>↑↓ Navigieren</span>
            <span>↵ Öffnen</span>
            <span>Esc Schließen</span>
          </div>
        )}
      </div>
    </div>
  )
}
