"use client"

import { useEffect, useState } from "react"
import { adminService } from "@/lib/admin/service"
import type { SystemSettings, SystemSettingsUpdate } from "@/lib/admin/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { CheckCircle2Icon, CircleIcon } from "lucide-react"
import { useAuth } from "@/components/providers/auth-provider"

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-card p-5 space-y-4">
      <h2 className="text-sm font-medium text-muted-foreground">{title}</h2>
      {children}
    </div>
  )
}

function Field({ label, value, onChange, type = "text", placeholder }: {
  label: string
  value: string
  onChange: (v: string) => void
  type?: string
  placeholder?: string
}) {
  return (
    <div className="grid gap-1.5">
      <Label>{label}</Label>
      <Input type={type} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
    </div>
  )
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
    >
      {checked ? <CheckCircle2Icon className="h-4 w-4 text-primary" /> : <CircleIcon className="h-4 w-4" />}
      {label}
    </button>
  )
}

export function SettingsTab() {
  const { hasPermission } = useAuth()
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  const [form, setForm] = useState<SystemSettingsUpdate>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    adminService.getSettings().then(s => {
      setSettings(s)
      setForm({
        company_name: s.company_name ?? "",
        company_legal: s.company_legal ?? "",
        tax_number: s.tax_number ?? "",
        registration_number: s.registration_number ?? "",
        address_street: s.address_street ?? "",
        address_zip: s.address_zip ?? "",
        address_city: s.address_city ?? "",
        address_country: s.address_country ?? "",
        company_email: s.company_email ?? "",
        company_phone: s.company_phone ?? "",
        company_website: s.company_website ?? "",
        default_timezone: s.default_timezone ?? "",
        default_language: s.default_language ?? "",
        default_currency: s.default_currency ?? "",
        working_hours_per_day: s.working_hours_per_day ?? 8,
        working_days_per_week: s.working_days_per_week ?? 5,
        vacation_days_per_year: s.vacation_days_per_year ?? 30,
        weekend_saturday: s.weekend_saturday,
        weekend_sunday: s.weekend_sunday,
        maintenance_mode: s.maintenance_mode,
        allow_registration: s.allow_registration,
        require_email_verification: s.require_email_verification,
        email_enabled: s.email_enabled,
        smtp_host: s.smtp_host ?? "",
        smtp_port: s.smtp_port ?? 587,
        smtp_username: s.smtp_username ?? "",
        smtp_from_email: s.smtp_from_email ?? "",
        smtp_from_name: s.smtp_from_name ?? "",
        smtp_use_tls: s.smtp_use_tls,
        smtp_use_ssl: s.smtp_use_ssl,
      })
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  function set(key: keyof SystemSettingsUpdate, value: unknown) {
    setForm(f => ({ ...f, [key]: value }))
  }

  async function handleSave() {
    setSaving(true)
    try {
      await adminService.updateSettings(form)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>

  return (
    <div className="space-y-6 max-w-2xl">
      <Section title="Unternehmen">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Firmenname" value={String(form.company_name ?? "")} onChange={v => set("company_name", v)} placeholder="K.I.T. Solutions" />
          <Field label="Rechtsform" value={String(form.company_legal ?? "")} onChange={v => set("company_legal", v)} placeholder="GmbH, GbR…" />
          <Field label="Steuernummer" value={String(form.tax_number ?? "")} onChange={v => set("tax_number", v)} />
          <Field label="Registernummer" value={String(form.registration_number ?? "")} onChange={v => set("registration_number", v)} />
          <Field label="E-Mail" type="email" value={String(form.company_email ?? "")} onChange={v => set("company_email", v)} />
          <Field label="Telefon" value={String(form.company_phone ?? "")} onChange={v => set("company_phone", v)} />
          <div className="sm:col-span-2">
            <Field label="Website" value={String(form.company_website ?? "")} onChange={v => set("company_website", v)} placeholder="https://…" />
          </div>
        </div>
      </Section>

      <Section title="Adresse">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Field label="Straße" value={String(form.address_street ?? "")} onChange={v => set("address_street", v)} />
          </div>
          <Field label="PLZ" value={String(form.address_zip ?? "")} onChange={v => set("address_zip", v)} />
          <Field label="Stadt" value={String(form.address_city ?? "")} onChange={v => set("address_city", v)} />
          <div className="sm:col-span-2">
            <Field label="Land" value={String(form.address_country ?? "")} onChange={v => set("address_country", v)} placeholder="DE" />
          </div>
        </div>
      </Section>

      <Section title="Regionaleinstellungen">
        <div className="grid gap-4 sm:grid-cols-3">
          <Field label="Zeitzone" value={String(form.default_timezone ?? "")} onChange={v => set("default_timezone", v)} placeholder="Europe/Berlin" />
          <Field label="Sprache" value={String(form.default_language ?? "")} onChange={v => set("default_language", v)} placeholder="de" />
          <Field label="Währung" value={String(form.default_currency ?? "")} onChange={v => set("default_currency", v)} placeholder="EUR" />
        </div>
      </Section>

      <Section title="Arbeitszeiten">
        <div className="grid gap-4 sm:grid-cols-3">
          <Field label="Stunden / Tag" type="number" value={String(form.working_hours_per_day ?? "")} onChange={v => set("working_hours_per_day", parseFloat(v) || 0)} />
          <Field label="Arbeitstage / Woche" type="number" value={String(form.working_days_per_week ?? "")} onChange={v => set("working_days_per_week", parseInt(v) || 0)} />
          <Field label="Urlaubstage / Jahr" type="number" value={String(form.vacation_days_per_year ?? "")} onChange={v => set("vacation_days_per_year", parseInt(v) || 0)} />
        </div>
        <div className="flex gap-4">
          <Toggle label="Samstag = Wochenende" checked={!!form.weekend_saturday} onChange={v => set("weekend_saturday", v)} />
          <Toggle label="Sonntag = Wochenende" checked={!!form.weekend_sunday} onChange={v => set("weekend_sunday", v)} />
        </div>
      </Section>

      <Section title="System">
        <div className="flex flex-wrap gap-4">
          <Toggle label="Wartungsmodus" checked={!!form.maintenance_mode} onChange={v => set("maintenance_mode", v)} />
          <Toggle label="Registrierung erlaubt" checked={!!form.allow_registration} onChange={v => set("allow_registration", v)} />
          <Toggle label="E-Mail-Verifizierung erforderlich" checked={!!form.require_email_verification} onChange={v => set("require_email_verification", v)} />
        </div>
      </Section>

      <Section title="E-Mail / SMTP">
        <Toggle label="E-Mail aktiviert" checked={!!form.email_enabled} onChange={v => set("email_enabled", v)} />
        {form.email_enabled && (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="SMTP Host" value={String(form.smtp_host ?? "")} onChange={v => set("smtp_host", v)} placeholder="smtp.example.com" />
            <Field label="SMTP Port" type="number" value={String(form.smtp_port ?? "")} onChange={v => set("smtp_port", parseInt(v) || 587)} />
            <Field label="Benutzername" value={String(form.smtp_username ?? "")} onChange={v => set("smtp_username", v)} />
            <Field label="Absender-E-Mail" type="email" value={String(form.smtp_from_email ?? "")} onChange={v => set("smtp_from_email", v)} />
            <div className="sm:col-span-2">
              <Field label="Absendername" value={String(form.smtp_from_name ?? "")} onChange={v => set("smtp_from_name", v)} />
            </div>
            <div className="flex gap-4 sm:col-span-2">
              <Toggle label="TLS" checked={!!form.smtp_use_tls} onChange={v => set("smtp_use_tls", v)} />
              <Toggle label="SSL" checked={!!form.smtp_use_ssl} onChange={v => set("smtp_use_ssl", v)} />
            </div>
          </div>
        )}
      </Section>

      <div className="flex items-center justify-end gap-3">
        {saved && <span className="text-sm text-green-600">Gespeichert.</span>}
        {hasPermission("admin.write") && (
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Speichern…" : "Einstellungen speichern"}
          </Button>
        )}
      </div>
    </div>
  )
}
