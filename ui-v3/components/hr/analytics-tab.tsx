"use client"

import { useState, useEffect } from "react"
import { hrService } from "@/lib/hr/service"
import type { HeadcountStats, LeaveSummary, RecruitingFunnel } from "@/lib/hr/types"

function KpiCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  )
}

export function AnalyticsTab() {
  const [headcount, setHeadcount] = useState<HeadcountStats | null>(null)
  const [leaveSummary, setLeaveSummary] = useState<LeaveSummary | null>(null)
  const [recruitingFunnel, setRecruitingFunnel] = useState<RecruitingFunnel | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      hrService.getHeadcount().catch(() => null),
      hrService.getLeaveSummary().catch(() => null),
      hrService.getRecruitingFunnel().catch(() => null),
    ]).then(([h, l, r]) => {
      if (h) setHeadcount(h)
      if (l) setLeaveSummary(l)
      if (r) setRecruitingFunnel(r)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-sm text-muted-foreground">Lädt...</p>

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">Belegschaft</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <KpiCard label="Mitarbeiter gesamt" value={headcount?.total ?? "—"} />
          <KpiCard label="Aktiv" value={headcount?.active ?? "—"} />
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">Abwesenheiten</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <KpiCard label="Offene Urlaubsanträge" value={leaveSummary?.pending_requests ?? "—"} />
          <KpiCard label="Genehmigt (diesen Monat)" value={leaveSummary?.approved_this_month ?? "—"} />
          <KpiCard label="Tage genommen (Jahr)" value={leaveSummary?.total_days_taken_this_year ?? "—"} />
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">Recruiting</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <KpiCard label="Offene Stellen" value={recruitingFunnel?.open_positions ?? "—"} />
          <KpiCard label="Bewerbungen gesamt" value={recruitingFunnel?.total_applications ?? "—"} />
        </div>

        {recruitingFunnel && Object.keys(recruitingFunnel.by_status).length > 0 && (
          <div className="mt-4 rounded-lg border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-right px-4 py-3 font-medium text-muted-foreground">Anzahl</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {Object.entries(recruitingFunnel.by_status).map(([status, count]) => (
                  <tr key={status} className="hover:bg-muted/30">
                    <td className="px-4 py-3">{status}</td>
                    <td className="px-4 py-3 text-right">{count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
