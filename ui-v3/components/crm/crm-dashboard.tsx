"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { crmService } from "@/lib/crm/service"
import type { CrmStats, CrmActivity } from "@/lib/crm/types"
import { Button } from "@/components/ui/button"
import {
  Users, KanbanSquare, Contact2, PlusIcon, ArrowRight,
  PhoneIcon, MailIcon, MapPinIcon, CalendarIcon, StickyNoteIcon,
} from "lucide-react"

const STAGE_CONFIG = [
  { id: "new_lead",    label: "Neuer Lead",  color: "bg-slate-400" },
  { id: "qualified",  label: "Qualifiziert", color: "bg-blue-500" },
  { id: "proposal",   label: "Angebot",      color: "bg-violet-500" },
  { id: "negotiation",label: "Verhandlung",  color: "bg-amber-500" },
  { id: "won",        label: "Gewonnen",     color: "bg-green-500" },
  { id: "lost",       label: "Verloren",     color: "bg-red-500" },
]

const ACTIVITY_ICONS: Record<string, React.ElementType> = {
  call: PhoneIcon,
  email: MailIcon,
  onsite: MapPinIcon,
  remote: CalendarIcon,
  note: StickyNoteIcon,
  system: StickyNoteIcon,
}

const ACTIVITY_LABELS: Record<string, string> = {
  call: "Anruf", email: "E-Mail", onsite: "Vor-Ort", remote: "Remote", note: "Notiz", system: "System",
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return "gerade eben"
  if (m < 60) return `vor ${m} Min.`
  const h = Math.floor(m / 60)
  if (h < 24) return `vor ${h} Std.`
  const d = Math.floor(h / 24)
  if (d === 1) return "gestern"
  return `vor ${d} Tagen`
}

export function CrmDashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<CrmStats | null>(null)
  const [pipeline, setPipeline] = useState<Record<string, unknown[]>>({})
  const [activities, setActivities] = useState<(CrmActivity & { customer_name?: string })[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const [s, p, a] = await Promise.all([
        crmService.getStats().catch(() => null),
        crmService.getPipeline().catch(() => ({})),
        crmService.getLatestActivities(8).catch(() => []),
      ])
      setStats(s)
      setPipeline(p)
      setActivities(a)
      setLoading(false)
    }
    load()
  }, [])

  const pipelineTotal = Object.values(pipeline).reduce((s, c) => s + c.length, 0)

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">CRM</h1>
        <Button size="sm" onClick={() => router.push("/crm/customers/new")}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Neuer Kunde
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: "Kunden gesamt", value: stats?.total_customers ?? "–", sub: "Alle Einträge" },
          { label: "Aktive Kunden", value: stats?.active_customers ?? "–", sub: "Status: aktiv" },
          { label: "Leads", value: stats?.leads ?? "–", sub: "In Akquise" },
        ].map(s => (
          <div key={s.label} className="rounded-xl border bg-card p-5">
            <p className="text-sm text-muted-foreground">{s.label}</p>
            <p className="mt-2 text-3xl font-bold">{loading ? "–" : s.value}</p>
            <p className="mt-1 text-xs text-muted-foreground">{s.sub}</p>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="grid gap-3 sm:grid-cols-3">
        {[
          { label: "Kundenliste", icon: Users, href: "/crm/customers", desc: "Alle Kunden verwalten" },
          { label: "Pipeline", icon: KanbanSquare, href: "/crm/pipeline", desc: `${pipelineTotal} Kontakte in der Pipeline` },
          { label: "Kontakte", icon: Contact2, href: "/crm/contacts", desc: "Globale Kontaktübersicht" },
        ].map(a => {
          const Icon = a.icon
          return (
            <Link
              key={a.label}
              href={a.href}
              className="group flex items-center gap-4 rounded-xl border bg-card p-5 transition-colors hover:border-primary/40 hover:bg-card/80"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <p className="font-medium text-sm">{a.label}</p>
                <p className="text-xs text-muted-foreground truncate">{a.desc}</p>
              </div>
              <ArrowRight className="ml-auto h-4 w-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
            </Link>
          )
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Pipeline-Übersicht */}
        <div className="rounded-xl border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold">Pipeline-Übersicht</h3>
            <Link href="/crm/pipeline" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              Öffnen →
            </Link>
          </div>
          {loading ? (
            <div className="space-y-2">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="flex items-center gap-3 animate-pulse">
                  <div className="h-2.5 w-2.5 rounded-full bg-border shrink-0" />
                  <div className="h-2.5 flex-1 rounded bg-border" />
                  <div className="h-2.5 w-6 rounded bg-border shrink-0" />
                </div>
              ))}
            </div>
          ) : pipelineTotal === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Kontakte in der Pipeline.</p>
          ) : (
            <div className="space-y-3">
              {STAGE_CONFIG.map(stage => {
                const count = (pipeline[stage.id] ?? []).length
                const pct = pipelineTotal ? Math.round((count / pipelineTotal) * 100) : 0
                return (
                  <div key={stage.id} className="flex items-center gap-3">
                    <span className={`h-2.5 w-2.5 rounded-full shrink-0 ${stage.color}`} />
                    <span className="text-xs text-muted-foreground w-24 shrink-0">{stage.label}</span>
                    <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className={`h-full rounded-full ${stage.color}`} style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-xs font-medium tabular-nums w-6 text-right shrink-0">{count}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Letzte Aktivitäten */}
        <div className="rounded-xl border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold">Letzte Aktivitäten</h3>
            <Link href="/crm/customers" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              CRM →
            </Link>
          </div>
          {loading ? (
            <div className="space-y-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex gap-3 animate-pulse">
                  <div className="mt-0.5 h-7 w-7 rounded-lg bg-border shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <div className="h-3 w-3/4 rounded bg-border" />
                    <div className="h-2.5 w-1/2 rounded bg-border" />
                  </div>
                </div>
              ))}
            </div>
          ) : activities.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Aktivitäten vorhanden.</p>
          ) : (
            <ul className="space-y-3">
              {activities.map(act => {
                const Icon = ACTIVITY_ICONS[act.type] ?? StickyNoteIcon
                return (
                  <li key={act.id} className="flex items-start gap-3">
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-muted">
                      <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm leading-tight">
                        <span className="font-medium">{ACTIVITY_LABELS[act.type] ?? act.type}</span>
                        {act.customer_name && (
                          <span className="text-muted-foreground"> – {act.customer_name}</span>
                        )}
                      </p>
                      {act.description && (
                        <p className="mt-0.5 truncate text-xs text-muted-foreground">{act.description}</p>
                      )}
                    </div>
                    <span className="shrink-0 text-xs text-muted-foreground/60">
                      {timeAgo(act.occurred_at ?? act.created_at)}
                    </span>
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
