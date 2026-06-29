"use client"

import { useState, useEffect } from "react"
import { hrService } from "@/lib/hr/service"
import type { HeadcountStats, LeaveSummary, RecruitingFunnel } from "@/lib/hr/types"

const EMPLOYMENT_TYPE_LABELS: Record<string, string> = {
  fulltime: "Vollzeit",
  parttime: "Teilzeit",
  freelancer: "Freelancer",
  intern: "Praktikant",
  minijob: "Minijob",
}

const APPLICATION_STATUS_LABELS: Record<string, string> = {
  new: "Neu",
  reviewing: "In Prüfung",
  interview: "Interview",
  offer: "Angebot",
  hired: "Eingestellt",
  rejected: "Abgelehnt",
  withdrawn: "Zurückgezogen",
}

function KpiCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-muted-foreground">{sub}</p>}
    </div>
  )
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
      {children}
    </h2>
  )
}

function BreakdownTable({
  data,
  total,
  labelMap,
}: {
  data: Record<string, number>
  total: number
  labelMap?: Record<string, string>
}) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1])
  if (entries.length === 0) return null

  return (
    <div className="rounded-lg border overflow-hidden">
      <table className="w-full text-sm">
        <tbody className="divide-y">
          {entries.map(([key, count]) => {
            const pct = total > 0 ? Math.round((count / total) * 100) : 0
            return (
              <tr key={key} className="hover:bg-muted/30">
                <td className="px-4 py-2.5 font-medium">
                  {labelMap?.[key] ?? key}
                </td>
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground w-8 text-right">{pct}%</span>
                  </div>
                </td>
                <td className="px-4 py-2.5 text-right font-medium w-12">{count}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export function AnalyticsTab() {
  const [headcount, setHeadcount] = useState<HeadcountStats | null>(null)
  const [leaveSummary, setLeaveSummary] = useState<LeaveSummary | null>(null)
  const [recruitingFunnel, setRecruitingFunnel] = useState<RecruitingFunnel | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    Promise.all([
      hrService.getHeadcount().catch(() => null),
      hrService.getLeaveSummary().catch(() => null),
      hrService.getRecruitingFunnel().catch(() => null),
    ]).then(([h, l, r]) => {
      if (h) setHeadcount(h)
      if (l) setLeaveSummary(l)
      if (r) setRecruitingFunnel(r)
      if (!h && !l && !r) setError(true)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">Lädt…</div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
        Analytics-Daten konnten nicht geladen werden.
      </div>
    )
  }

  const activeRate = headcount && headcount.total > 0
    ? Math.round((headcount.active / headcount.total) * 100)
    : null

  return (
    <div className="space-y-8">

      {/* Belegschaft */}
      <div>
        <SectionHeader>Belegschaft</SectionHeader>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 mb-4">
          <KpiCard label="Mitarbeiter gesamt" value={headcount?.total ?? "—"} />
          <KpiCard
            label="Aktiv"
            value={headcount?.active ?? "—"}
            sub={activeRate !== null ? `${activeRate}% der Belegschaft` : undefined}
          />
          <KpiCard
            label="Inaktiv / Ausgeschieden"
            value={headcount ? headcount.total - headcount.active : "—"}
          />
          <KpiCard
            label="Abteilungen"
            value={headcount ? Object.keys(headcount.by_department).length : "—"}
          />
        </div>

        {headcount && Object.keys(headcount.by_department).length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-2">Nach Abteilung</p>
              <BreakdownTable data={headcount.by_department} total={headcount.total} />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-2">Nach Anstellungsart</p>
              <BreakdownTable
                data={headcount.by_employment_type}
                total={headcount.total}
                labelMap={EMPLOYMENT_TYPE_LABELS}
              />
            </div>
          </div>
        )}
      </div>

      {/* Abwesenheiten */}
      <div>
        <SectionHeader>Abwesenheiten</SectionHeader>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <KpiCard
            label="Offene Anträge"
            value={leaveSummary?.pending_requests ?? "—"}
            sub="warten auf Genehmigung"
          />
          <KpiCard
            label="Genehmigt diesen Monat"
            value={leaveSummary?.approved_this_month ?? "—"}
          />
          <KpiCard
            label="Urlaubstage genommen (Jahr)"
            value={leaveSummary ? `${leaveSummary.total_days_taken_this_year} Tage` : "—"}
          />
        </div>
      </div>

      {/* Recruiting */}
      <div>
        <SectionHeader>Recruiting</SectionHeader>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 mb-4">
          <KpiCard label="Offene Stellen" value={recruitingFunnel?.open_positions ?? "—"} />
          <KpiCard label="Bewerbungen gesamt" value={recruitingFunnel?.total_applications ?? "—"} />
        </div>

        {recruitingFunnel && Object.keys(recruitingFunnel.by_status).length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Bewerbungen nach Status</p>
            <BreakdownTable
              data={recruitingFunnel.by_status}
              total={recruitingFunnel.total_applications}
              labelMap={APPLICATION_STATUS_LABELS}
            />
          </div>
        )}
      </div>

    </div>
  )
}
