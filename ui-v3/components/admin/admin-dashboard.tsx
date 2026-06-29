"use client"

import { useState } from "react"
import { SettingsTab } from "./settings-tab"
import { DepartmentsTab } from "./departments-tab"
import { RolesTab } from "./roles-tab"
import { AuditTab } from "./audit-tab"
import { StripeTab } from "./stripe-tab"

type Tab = "settings" | "departments" | "roles" | "audit" | "stripe"

const TABS: { id: Tab; label: string }[] = [
  { id: "settings", label: "Einstellungen" },
  { id: "departments", label: "Abteilungen" },
  { id: "roles", label: "Rollen" },
  { id: "audit", label: "Audit-Log" },
  { id: "stripe", label: "Stripe" },
]

export function AdminDashboard() {
  const [tab, setTab] = useState<Tab>("settings")

  return (
    <div className="space-y-6 px-8 py-6">
      <h1 className="text-xl font-semibold">Administration</h1>

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

      {tab === "settings" && <SettingsTab />}
      {tab === "departments" && <DepartmentsTab />}
      {tab === "roles" && <RolesTab />}
      {tab === "audit" && <AuditTab />}
      {tab === "stripe" && <StripeTab />}
    </div>
  )
}
