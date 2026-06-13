"use client"

import { useState } from "react"
import { TimeTracker } from "./time-tracker"
import { TimeReports } from "./time-reports"
import { TimeApprovals } from "./time-approvals"

type Tab = "tracker" | "reports" | "approvals"

const TABS: { id: Tab; label: string }[] = [
  { id: "tracker",   label: "Erfassung" },
  { id: "reports",   label: "Berichte" },
  { id: "approvals", label: "Freigaben" },
]

export function TimePage() {
  const [tab, setTab] = useState<Tab>("tracker")

  return (
    <div>
      <div className="flex items-center justify-between border-b px-8 py-4">
        <h1 className="text-xl font-semibold">Zeiterfassung</h1>
        <div className="flex gap-1 rounded-lg border bg-muted p-1">
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                tab === t.id
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === "tracker" ? <TimeTracker /> : tab === "reports" ? <TimeReports /> : <TimeApprovals />}
    </div>
  )
}
