"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { supportService } from "@/lib/support/service"
import { crmService } from "@/lib/crm/service"
import type { Customer } from "@/lib/crm/types"
import { CustomerSelect } from "@/components/crm/customer-select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeftIcon } from "lucide-react"
import { useAuth } from "@/components/providers/auth-provider"

const TYPES = ["bug", "feature", "question", "complaint", "other"]
const PRIORITIES = [
  { value: "low", label: "Niedrig" },
  { value: "medium", label: "Mittel" },
  { value: "high", label: "Hoch" },
  { value: "urgent", label: "Dringend" },
]
const CATEGORIES = ["Allgemein", "Abrechnung", "Technik", "Vertrag", "Sonstiges"]
const CHANNELS = ["email", "phone", "chat", "portal", "internal"]

export function TicketForm() {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [type, setType] = useState("bug")
  const [priority, setPriority] = useState("medium")
  const [category, setCategory] = useState("Allgemein")
  const [channel, setChannel] = useState("portal")
  const [customerId, setCustomerId] = useState("none")
  const [reporterEmail, setReporterEmail] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    crmService.getCustomers({ limit: 500 }).then(setCustomers)
  }, [])

  async function handleSave() {
    if (!title.trim()) return
    setSaving(true)
    try {
      const ticket = await supportService.create({
        title: title.trim(),
        description: description || null,
        type,
        priority,
        category,
        channel,
        customer_id: customerId === "none" ? null : customerId,
        reporter_email: reporterEmail || null,
      })
      router.push(`/support/${ticket.id}`)
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
        <h1 className="text-xl font-semibold">Neues Ticket</h1>
      </div>

      <div className="max-w-2xl space-y-6">
        <div className="rounded-lg border bg-card p-5 space-y-4">
          <h2 className="text-sm font-medium text-muted-foreground">Ticket</h2>
          <div className="grid gap-1.5">
            <Label>Titel *</Label>
            <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Kurze Problembeschreibung" />
          </div>
          <div className="grid gap-1.5">
            <Label>Beschreibung</Label>
            <Textarea value={description} onChange={e => setDescription(e.target.value)} rows={5} placeholder="Detaillierte Beschreibung…" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-1.5">
              <Label>Typ</Label>
              <Select value={type} onValueChange={v => v && setType(v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Priorität</Label>
              <Select value={priority} onValueChange={v => v && setPriority(v)}>
                <SelectTrigger>
                  <span data-slot="select-value">
                    {PRIORITIES.find(p => p.value === priority)?.label ?? priority}
                  </span>
                </SelectTrigger>
                <SelectContent>{PRIORITIES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Kategorie</Label>
              <Select value={category} onValueChange={v => v && setCategory(v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Kanal</Label>
              <Select value={channel} onValueChange={v => v && setChannel(v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{CHANNELS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-5 space-y-4">
          <h2 className="text-sm font-medium text-muted-foreground">Melder</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-1.5">
              <Label>Kunde</Label>
              <CustomerSelect
                customers={customers}
                value={customerId === "none" ? "" : customerId}
                onChange={v => setCustomerId(v || "none")}
                placeholder="Kein Kunde"
              />
            </div>
            <div className="grid gap-1.5">
              <Label>E-Mail Melder</Label>
              <Input type="email" value={reporterEmail} onChange={e => setReporterEmail(e.target.value)} placeholder="melder@beispiel.de" />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={() => router.back()}>Abbrechen</Button>
          {hasPermission("support.create") && (
            <Button onClick={handleSave} disabled={saving || !title.trim()}>
              {saving ? "Erstellen…" : "Ticket erstellen"}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
