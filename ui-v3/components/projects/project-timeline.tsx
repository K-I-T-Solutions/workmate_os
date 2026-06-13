"use client"

import { useRouter } from "next/navigation"
import type { Project } from "@/lib/projects/types"

const STATUS_COLOR_BAR: Record<string, string> = {
  planning: "bg-blue-500",
  active: "bg-green-500",
  on_hold: "bg-amber-500",
  completed: "bg-muted-foreground",
  cancelled: "bg-red-400 opacity-50",
}

const STATUS_LABELS: Record<string, string> = {
  planning: "Planung", active: "Aktiv", on_hold: "Pausiert",
  completed: "Abgeschlossen", cancelled: "Abgebrochen",
}

function fmtD(d: string | null) {
  if (!d) return "–"
  return new Date(d).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "2-digit" })
}

export function ProjectTimeline({ projects }: { projects: Project[] }) {
  const router = useRouter()
  const now = new Date()
  const year = now.getFullYear()
  const viewStart = new Date(year, 0, 1)
  const viewEnd = new Date(year, 11, 31, 23, 59, 59)
  const totalMs = viewEnd.getTime() - viewStart.getTime()

  const months = Array.from({ length: 12 }, (_, i) =>
    new Date(year, i, 1).toLocaleDateString("de-DE", { month: "short" })
  )
  const monthOffsets = Array.from({ length: 12 }, (_, i) =>
    (new Date(year, i, 1).getTime() - viewStart.getTime()) / totalMs * 100
  )

  const today = Math.min(
    Math.max((now.getTime() - viewStart.getTime()) / totalMs * 100, 0),
    100
  )

  const withDates = projects.filter(p => p.start_date || p.end_date)
  const withoutDates = projects.filter(p => !p.start_date && !p.end_date)

  function getBar(p: Project): { left: number; width: number } | null {
    const start = p.start_date ? new Date(p.start_date) : viewStart
    const end = p.end_date ? new Date(p.end_date) : viewEnd
    const clampS = Math.max(start.getTime(), viewStart.getTime())
    const clampE = Math.min(end.getTime(), viewEnd.getTime())
    if (clampS > clampE) return null
    const left = (clampS - viewStart.getTime()) / totalMs * 100
    const width = (clampE - clampS) / totalMs * 100
    return { left, width: Math.max(width, 0.5) }
  }

  if (projects.length === 0) {
    return (
      <div className="py-16 text-center text-sm text-muted-foreground">
        Keine Projekte vorhanden.
      </div>
    )
  }

  return (
    <div className="rounded-xl border overflow-hidden">
      {/* Month header */}
      <div className="flex border-b bg-muted/40">
        <div className="w-48 shrink-0 border-r px-3 py-2">
          <span className="text-xs font-medium text-muted-foreground">{year}</span>
        </div>
        <div className="relative flex-1 h-8">
          {months.map((m, i) => (
            <div
              key={m}
              className="absolute top-0 flex h-full items-center border-r border-border/50 px-1.5"
              style={{ left: `${monthOffsets[i]}%`, width: `${100 / 12}%` }}
            >
              <span className="text-[10px] text-muted-foreground">{m}</span>
            </div>
          ))}
          {/* Today marker */}
          <div
            className="absolute top-0 bottom-0 z-10 w-px bg-primary/60"
            style={{ left: `${today}%` }}
          />
        </div>
      </div>

      {/* Project rows */}
      {withDates.map(p => {
        const bar = getBar(p)
        return (
          <div
            key={p.id}
            className="flex items-center border-b last:border-0 hover:bg-muted/20 transition-colors cursor-pointer"
            onClick={() => router.push(`/projects/${p.id}`)}
          >
            <div className="w-48 shrink-0 border-r px-3 py-3">
              <p className="truncate text-sm font-medium">{p.title}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {STATUS_LABELS[p.status] ?? p.status}
              </p>
            </div>
            <div className="relative flex-1 h-11">
              {/* Month grid lines */}
              {monthOffsets.slice(1).map((offset, i) => (
                <div
                  key={i}
                  className="absolute top-0 bottom-0 w-px bg-border/30"
                  style={{ left: `${offset}%` }}
                />
              ))}
              {/* Today marker */}
              <div
                className="absolute top-0 bottom-0 w-px bg-primary/30 z-10"
                style={{ left: `${today}%` }}
              />
              {/* Project bar */}
              {bar && (
                <div
                  className={`absolute top-3 h-5 rounded-full ${STATUS_COLOR_BAR[p.status] ?? "bg-primary"} opacity-80 hover:opacity-100 transition-opacity`}
                  style={{ left: `${bar.left}%`, width: `${bar.width}%` }}
                  title={`${p.title}\n${fmtD(p.start_date)} – ${fmtD(p.end_date)}`}
                />
              )}
            </div>
            <div className="w-40 shrink-0 border-l px-3 py-3 text-right">
              <p className="text-xs text-muted-foreground tabular-nums">
                {fmtD(p.start_date)} – {fmtD(p.end_date)}
              </p>
            </div>
          </div>
        )
      })}

      {/* Projects without dates */}
      {withoutDates.length > 0 && (
        <div className="border-t bg-muted/20 px-3 py-2">
          <p className="mb-1.5 text-xs text-muted-foreground">Ohne Datum ({withoutDates.length})</p>
          <div className="flex flex-wrap gap-2">
            {withoutDates.map(p => (
              <button
                key={p.id}
                onClick={() => router.push(`/projects/${p.id}`)}
                className="rounded-full bg-muted px-2.5 py-1 text-xs hover:bg-secondary transition-colors"
              >
                {p.title}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
