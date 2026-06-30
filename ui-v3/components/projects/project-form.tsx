"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { projectService } from "@/lib/projects/service"
import { crmService } from "@/lib/crm/service"
import type { Project } from "@/lib/projects/types"
import type { Customer } from "@/lib/crm/types"
import { CustomerSelect } from "@/components/crm/customer-select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeftIcon } from "lucide-react"

const STATUS_OPTIONS = [
  { value: "planning", label: "Planung" },
  { value: "active", label: "Aktiv" },
  { value: "on_hold", label: "Pausiert" },
  { value: "completed", label: "Abgeschlossen" },
  { value: "cancelled", label: "Abgebrochen" },
]

interface Props {
  initial?: Project
  projectId?: string
}

export function ProjectForm({ initial, projectId }: Props) {
  const router = useRouter()
  const isEdit = !!projectId
  const [customers, setCustomers] = useState<Customer[]>([])

  const [title, setTitle] = useState(initial?.title ?? "")
  const [description, setDescription] = useState(initial?.description ?? "")
  const [status, setStatus] = useState(initial?.status ?? "planning")
  const [startDate, setStartDate] = useState(initial?.start_date?.substring(0, 10) ?? "")
  const [endDate, setEndDate] = useState(initial?.end_date?.substring(0, 10) ?? "")
  const [customerId, setCustomerId] = useState(initial?.customer_id ?? "")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    crmService.getCustomers({ limit: 500 }).then(setCustomers)
  }, [])

  async function handleSave() {
    if (!title.trim()) return
    setSaving(true)
    try {
      const payload = {
        title: title.trim(),
        description: description || null,
        status,
        start_date: startDate || null,
        end_date: endDate || null,
        customer_id: customerId || null,
      }
      let saved: Project
      if (isEdit && projectId) {
        saved = await projectService.update(projectId, payload)
      } else {
        saved = await projectService.create(payload)
      }
      router.push(`/projects/${saved.id}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeftIcon className="h-4 w-4" />
        </Button>
        <h1 className="text-xl font-semibold">
          {isEdit ? "Projekt bearbeiten" : "Neues Projekt"}
        </h1>
      </div>

      <div className="max-w-2xl space-y-6">
        {/* Basis */}
        <div className="rounded-lg border bg-card p-5">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">Allgemein</h2>
          <div className="space-y-4">
            <div className="grid gap-1.5">
              <Label>Titel *</Label>
              <Input
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="Projektname"
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Beschreibung</Label>
              <Textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                rows={4}
                placeholder="Kurze Projektbeschreibung…"
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="grid gap-1.5">
                <Label>Status</Label>
                <Select value={status} onValueChange={v => v && setStatus(v)}>
                  <SelectTrigger>
                    <span data-slot="select-value">
                      {STATUS_OPTIONS.find(o => o.value === status)?.label ?? status}
                    </span>
                  </SelectTrigger>
                  <SelectContent>
                    {STATUS_OPTIONS.map(o => (
                      <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-1.5">
                <Label>Kunde</Label>
                <CustomerSelect
                  customers={customers}
                  value={customerId}
                  onChange={setCustomerId}
                  placeholder="Kein Kunde"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Zeitraum */}
        <div className="rounded-lg border bg-card p-5">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">Zeitraum</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-1.5">
              <Label>Startdatum</Label>
              <Input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
            </div>
            <div className="grid gap-1.5">
              <Label>Enddatum</Label>
              <Input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={() => router.back()}>Abbrechen</Button>
          <Button onClick={handleSave} disabled={saving || !title.trim()}>
            {saving ? "Speichern…" : isEdit ? "Änderungen speichern" : "Projekt erstellen"}
          </Button>
        </div>
      </div>
    </div>
  )
}
