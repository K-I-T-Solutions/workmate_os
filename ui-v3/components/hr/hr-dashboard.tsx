"use client"

import { useEffect, useState } from "react"
import { hrService } from "@/lib/hr/service"
import type { EmployeeStatistics, LeaveStatistics } from "@/lib/hr/types"
import { EmployeesTab } from "./employees-tab"
import { LeaveTab } from "./leave-tab"
import { RecruitingTab } from "./recruiting-tab"

type Tab = "employees" | "leave" | "recruiting"

const TABS: { id: Tab; label: string }[] = [
  { id: "employees", label: "Mitarbeiter" },
  { id: "leave", label: "Abwesenheiten" },
  { id: "recruiting", label: "Recruiting" },
]

export function HrDashboard() {
  const [tab, setTab] = useState<Tab>("employees")
  const [empStats, setEmpStats] = useState<EmployeeStatistics | null>(null)
  const [leaveStats, setLeaveStats] = useState<LeaveStatistics | null>(null)

  useEffect(() => {
    hrService.getStatistics().then(setEmpStats).catch(() => {})
    hrService.getLeaveStatistics().then(setLeaveStats).catch(() => {})
  }, [])

  return (
    <div className="space-y-6 px-8 py-6">
      <h1 className="text-xl font-semibold">HR</h1>

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

      {tab === "employees" && <EmployeesTab stats={empStats} />}
      {tab === "leave" && <LeaveTab stats={leaveStats} />}
      {tab === "recruiting" && <RecruitingTab />}
    </div>
  )
}
