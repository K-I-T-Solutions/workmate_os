"use client"

import { useState, useEffect } from "react"
import { hrService } from "@/lib/hr/service"
import type { OnboardingTemplate } from "@/lib/hr/types"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

function StartOnboardingDialog({
  open,
  templates,
  onClose,
  onStarted,
}: {
  open: boolean
  templates: OnboardingTemplate[]
  onClose: () => void
  onStarted: () => void
}) {
  const [employeeId, setEmployeeId] = useState("")
  const [templateId, setTemplateId] = useState("")
  const [startDate, setStartDate] = useState("")
  const [saving, setSaving] = useState(false)

  function reset() {
    setEmployeeId(""); setTemplateId(""); setStartDate("")
  }

  useEffect(() => {
    if (templates.length > 0 && !templateId) {
      setTemplateId(templates[0].id)
    }
  }, [templates, templateId])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!employeeId.trim() || !templateId || !startDate) return
    setSaving(true)
    await hrService.startOnboarding({
      employee_id: employeeId.trim(),
      template_id: templateId,
      start_date: startDate,
    }).catch(() => {})
    setSaving(false)
    onStarted()
    reset()
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Onboarding starten</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label htmlFor="ob-emp">Mitarbeiter-ID *</Label>
            <Input
              id="ob-emp"
              placeholder="UUID des Mitarbeiters"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="ob-tpl">Vorlage *</Label>
            <select
              id="ob-tpl"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              required
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="">Vorlage wählen…</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="ob-date">Startdatum *</Label>
            <Input id="ob-date" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !employeeId.trim() || !templateId || !startDate}>
              {saving ? "Starten…" : "Onboarding starten"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export function OnboardingTab() {
  const [templates, setTemplates] = useState<OnboardingTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)

  useEffect(() => {
    hrService.listOnboardingTemplates().then(setTemplates).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setDialogOpen(true)}>Onboarding starten</Button>
      </div>

      {loading && <p className="text-sm text-muted-foreground">Lädt...</p>}

      {!loading && templates.length === 0 && (
        <p className="py-8 text-center text-sm text-muted-foreground">Keine Onboarding-Vorlagen vorhanden.</p>
      )}

      {!loading && templates.length > 0 && (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Beschreibung</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {templates.map((t) => (
                <tr key={t.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-medium">{t.name}</td>
                  <td className="px-4 py-3 text-muted-foreground">{t.description ?? "—"}</td>
                  <td className="px-4 py-3">
                    {t.is_active ? (
                      <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Aktiv</span>
                    ) : (
                      <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">Inaktiv</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <StartOnboardingDialog
        open={dialogOpen}
        templates={templates}
        onClose={() => setDialogOpen(false)}
        onStarted={() => {}}
      />
    </div>
  )
}
