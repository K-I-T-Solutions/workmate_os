"use client"

import { useState } from "react"
import { TimeTracker } from "./time-tracker"
import { TimeReports } from "./time-reports"
import { TimeApprovals } from "./time-approvals"
import { TimeBilling } from "./time-billing"
import { ReceiptIcon } from "lucide-react"

type Tab = "tracker" | "reports" | "approvals" | "billing"

const TABS: { id: Tab; label: string; icon?: React.ReactNode }[] = [
  { id: "tracker",   label: "Erfassung" },
  { id: "reports",   label: "Berichte" },
  { id: "approvals", label: "Freigaben" },
  { id: "billing",   label: "Abrechnen", icon: <ReceiptIcon className="h-3.5 w-3.5" /> },
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
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                tab === t.id
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === "tracker" ? (
        <TimeTracker />
      ) : tab === "reports" ? (
        <TimeReports />
      ) : tab === "approvals" ? (
        <TimeApprovals />
      ) : (
        <TimeBilling />
      )}
    </div>
  )
}
