"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Save } from "lucide-react"
import { crmService } from "@/lib/crm/service"
import type { Customer, CustomerStatus, CustomerType, PipelineStage } from "@/lib/crm/types"
import { useAuth } from "@/components/providers/auth-provider"

const TYPE_LABELS: Record<string, string> = {
  business: "Unternehmen",
  individual: "Privatperson",
  government: "Behörde",
  creator: "Creator",
}

const STATUS_LABELS: Record<CustomerStatus, string> = {
  active: "Aktiv",
  inactive: "Inaktiv",
  lead: "Lead",
  blocked: "Gesperrt",
}

const PIPELINE_LABELS: Record<PipelineStage, string> = {
  new_lead: "Neuer Lead",
  qualified: "Qualifiziert",
  proposal: "Angebot",
  negotiation: "Verhandlung",
  won: "Gewonnen",
  lost: "Verloren",
}

interface Props {
  initial?: Partial<Customer>
  customerId?: string
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}

const inputCls =
  "w-full rounded-lg border border-border bg-secondary px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"

export function CustomerForm({ initial, customerId }: Props) {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const isEdit = !!customerId

  const [form, setForm] = useState({
    name: initial?.name ?? "",
    type: initial?.type ?? "",
    status: (initial?.status ?? "active") as CustomerStatus,
    pipeline_stage: (initial?.pipeline_stage ?? "new_lead") as PipelineStage,
    email: initial?.email ?? "",
    phone: initial?.phone ?? "",
    website: initial?.website ?? "",
    tax_id: initial?.tax_id ?? "",
    street: initial?.street ?? "",
    zip_code: initial?.zip_code ?? "",
    city: initial?.city ?? "",
    country: initial?.country ?? "Deutschland",
    notes: initial?.notes ?? "",
  })

  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function set(field: keyof typeof form, value: string) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.name.trim()) { setError("Name ist ein Pflichtfeld"); return }
    setSaving(true)
    setError(null)
    try {
      const payload = {
        name: form.name.trim(),
        type: (form.type || null) as CustomerType | null,
        status: form.status,
        pipeline_stage: (form.pipeline_stage || null) as PipelineStage | null,
        email: form.email || null,
        phone: form.phone || null,
        website: form.website || null,
        tax_id: form.tax_id || null,
        street: form.street || null,
        zip_code: form.zip_code || null,
        city: form.city || null,
        country: form.country || null,
        notes: form.notes || null,
      }
      if (isEdit) {
        await crmService.updateCustomer(customerId, payload)
        router.push(`/crm/customers/${customerId}`)
      } else {
        const res = await crmService.createCustomer(payload)
        router.push(`/crm/customers/${res.data.id}`)
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message ?? "Fehler beim Speichern")
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-2xl px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={() => router.back()}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <h1 className="font-heading text-2xl font-bold text-foreground">
          {isEdit ? "Kunde bearbeiten" : "Neuer Kunde"}
        </h1>
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Stammdaten */}
      <section className="rounded-xl border border-border bg-card p-6 space-y-4">
        <h2 className="font-heading text-sm font-semibold text-foreground">Stammdaten</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Field label="Name *">
              <input
                type="text"
                className={inputCls}
                placeholder="Firmenname oder Vor- / Nachname"
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
                required
              />
            </Field>
          </div>
          <Field label="Typ">
            <select className={inputCls} value={form.type} onChange={(e) => set("type", e.target.value)}>
              <option value="">– kein Typ –</option>
              {Object.entries(TYPE_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </Field>
          <Field label="Status">
            <select className={inputCls} value={form.status} onChange={(e) => set("status", e.target.value as CustomerStatus)}>
              {(Object.keys(STATUS_LABELS) as CustomerStatus[]).map((s) => (
                <option key={s} value={s}>{STATUS_LABELS[s]}</option>
              ))}
            </select>
          </Field>
          <Field label="Pipeline-Stage">
            <select className={inputCls} value={form.pipeline_stage} onChange={(e) => set("pipeline_stage", e.target.value as PipelineStage)}>
              {(Object.keys(PIPELINE_LABELS) as PipelineStage[]).map((s) => (
                <option key={s} value={s}>{PIPELINE_LABELS[s]}</option>
              ))}
            </select>
          </Field>
          <Field label="Steuernummer / USt-IdNr">
            <input type="text" className={inputCls} placeholder="DE123456789" value={form.tax_id} onChange={(e) => set("tax_id", e.target.value)} />
          </Field>
        </div>
      </section>

      {/* Kontaktdaten */}
      <section className="rounded-xl border border-border bg-card p-6 space-y-4">
        <h2 className="font-heading text-sm font-semibold text-foreground">Kontaktdaten</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="E-Mail">
            <input type="email" className={inputCls} placeholder="info@beispiel.de" value={form.email} onChange={(e) => set("email", e.target.value)} />
          </Field>
          <Field label="Telefon">
            <input type="tel" className={inputCls} placeholder="+49 261 000000" value={form.phone} onChange={(e) => set("phone", e.target.value)} />
          </Field>
          <div className="sm:col-span-2">
            <Field label="Webseite">
              <input type="url" className={inputCls} placeholder="https://beispiel.de" value={form.website} onChange={(e) => set("website", e.target.value)} />
            </Field>
          </div>
        </div>
      </section>

      {/* Adresse */}
      <section className="rounded-xl border border-border bg-card p-6 space-y-4">
        <h2 className="font-heading text-sm font-semibold text-foreground">Adresse</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Field label="Straße & Hausnummer">
              <input type="text" className={inputCls} placeholder="Musterstraße 1" value={form.street} onChange={(e) => set("street", e.target.value)} />
            </Field>
          </div>
          <Field label="PLZ">
            <input type="text" className={inputCls} placeholder="56070" value={form.zip_code} onChange={(e) => set("zip_code", e.target.value)} />
          </Field>
          <Field label="Stadt">
            <input type="text" className={inputCls} placeholder="Koblenz" value={form.city} onChange={(e) => set("city", e.target.value)} />
          </Field>
          <div className="sm:col-span-2">
            <Field label="Land">
              <input type="text" className={inputCls} placeholder="Deutschland" value={form.country} onChange={(e) => set("country", e.target.value)} />
            </Field>
          </div>
        </div>
      </section>

      {/* Notizen */}
      <section className="rounded-xl border border-border bg-card p-6 space-y-4">
        <h2 className="font-heading text-sm font-semibold text-foreground">Interne Notizen</h2>
        <textarea
          className={inputCls + " resize-none"}
          rows={4}
          placeholder="Interne Anmerkungen zum Kunden…"
          value={form.notes}
          onChange={(e) => set("notes", e.target.value)}
        />
      </section>

      {/* Actions */}
      <div className="flex gap-3 justify-end">
        <button
          type="button"
          onClick={() => router.back()}
          className="rounded-lg border border-border bg-secondary px-4 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          Abbrechen
        </button>
        {hasPermission("backoffice.crm.write") && (
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-60"
          >
            <Save className="h-4 w-4" />
            {saving ? "Speichern…" : isEdit ? "Änderungen speichern" : "Kunde anlegen"}
          </button>
        )}
      </div>
    </form>
  )
}
