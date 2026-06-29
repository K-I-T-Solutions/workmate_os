"use client"

import { useEffect, useState } from "react"
import { hrService } from "@/lib/hr/service"
import type { EmployeeStatistics, LeaveStatistics } from "@/lib/hr/types"
import { EmployeesTab } from "./employees-tab"
import { LeaveTab } from "./leave-tab"
import { RecruitingTab } from "./recruiting-tab"
import { TrainingTab } from "./training-tab"
import { OnboardingTab } from "./onboarding-tab"
import { AnalyticsTab } from "./analytics-tab"
import { CompensationTab } from "./compensation-tab"
import { HrDocumentsTab } from "./hr-documents-tab"

type Tab = "employees" | "leave" | "recruiting" | "training" | "onboarding" | "compensation" | "documents" | "analytics"

const TABS: { id: Tab; label: string }[] = [
  { id: "employees", label: "Mitarbeiter" },
  { id: "leave", label: "Abwesenheiten" },
  { id: "recruiting", label: "Recruiting" },
  { id: "training", label: "Schulungen" },
  { id: "onboarding", label: "Onboarding" },
  { id: "compensation", label: "Vergütung" },
  { id: "documents", label: "Dokumente" },
  { id: "analytics", label: "Analytics" },
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

      <div className="flex gap-1 border-b overflow-x-auto">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`shrink-0 px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
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
      {tab === "training" && <TrainingTab />}
      {tab === "onboarding" && <OnboardingTab />}
      {tab === "compensation" && <CompensationTab />}
      {tab === "documents" && <HrDocumentsTab />}
      {tab === "analytics" && <AnalyticsTab />}
    </div>
  )
}
