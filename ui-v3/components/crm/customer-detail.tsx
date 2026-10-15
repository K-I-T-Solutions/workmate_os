"use client"

import { useEffect, useState, useCallback } from "react"
import { usePageTitle } from "@/lib/page-title-context"
import { useRouter } from "next/navigation"
import { ArrowLeft, Edit, Phone, Mail, Globe, MapPin, Plus, Star, Trash2, X, Save, FileText, FolderKanban, MessageSquare, FolderOpen, ScrollText, HardDrive, KeyRound } from "lucide-react"
import { crmService } from "@/lib/crm/service"
import { invoiceService } from "@/lib/invoices/service"
import { projectService } from "@/lib/projects/service"
import { supportService } from "@/lib/support/service"
import { contractsService } from "@/lib/contracts/service"
import { assetsService } from "@/lib/assets/service"
import type { Contract } from "@/lib/contracts/types"
import type { CustomerAsset, SoftwareLicense } from "@/lib/assets/types"
import { CONTRACT_STATUS_COLOR, CONTRACT_STATUS_LABELS, INTERVAL_LABELS, fmtDate, fmtEur } from "@/lib/contracts/labels"
import { DocumentsTab } from "@/components/documents/documents-dashboard"
import type { Customer, Contact, CrmActivity, ActivityType } from "@/lib/crm/types"
import type { Invoice } from "@/lib/invoices/types"
import type { Project } from "@/lib/projects/types"
import type { Ticket } from "@/lib/support/types"
import { cn } from "@/lib/utils"
import { useAuth } from "@/components/providers/auth-provider"

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-500/15 text-green-400",
  inactive: "bg-slate-500/15 text-slate-400",
  lead: "bg-blue-500/15 text-blue-400",
  blocked: "bg-red-500/15 text-red-400",
}
const STATUS_LABELS: Record<string, string> = {
  active: "Aktiv", inactive: "Inaktiv", lead: "Lead", blocked: "Gesperrt",
}
const ACTIVITY_LABELS: Record<string, string> = {
  call: "Anruf", email: "E-Mail", onsite: "Vor Ort", remote: "Remote", note: "Notiz", system: "System",
}

const inputCls =
  "w-full rounded-lg border border-border bg-secondary px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"

// ─── Contact Modal ──────────────────────────────────────────────────────────
interface ContactModalProps {
  customerId: string
  contact?: Contact
  onClose: () => void
  onSaved: (c: Contact) => void
}

function ContactModal({ customerId, contact, onClose, onSaved }: ContactModalProps) {
  const isEdit = !!contact
  const [form, setForm] = useState({
    firstname: contact?.firstname ?? "",
    lastname: contact?.lastname ?? "",
    email: contact?.email ?? "",
    phone: contact?.phone ?? "",
    mobile: contact?.mobile ?? "",
    position: contact?.position ?? "",
    department: contact?.department ?? "",
    is_primary: contact?.is_primary ?? false,
    notes: contact?.notes ?? "",
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function set(field: keyof typeof form, value: string | boolean) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.firstname.trim() || !form.lastname.trim()) {
      setError("Vor- und Nachname sind Pflicht")
      return
    }
    setSaving(true)
    setError(null)
    try {
      const payload = {
        customer_id: customerId,
        firstname: form.firstname.trim(),
        lastname: form.lastname.trim(),
        email: form.email || null,
        phone: form.phone || null,
        mobile: form.mobile || null,
        position: form.position || null,
        department: form.department || null,
        is_primary: form.is_primary,
        notes: form.notes || null,
      }
      let saved: Contact
      if (isEdit) {
        const res = await crmService.updateContact(contact.id, payload)
        saved = res.data
      } else {
        const res = await crmService.createContact(payload)
        saved = res.data
      }
      onSaved(saved)
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message ?? "Fehler beim Speichern")
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="font-heading text-base font-semibold text-foreground">
            {isEdit ? "Ansprechpartner bearbeiten" : "Ansprechpartner hinzufügen"}
          </h2>
          <button type="button" onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-4 py-2 text-sm text-destructive">{error}</div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Vorname *</label>
              <input className={inputCls} placeholder="Max" value={form.firstname} onChange={(e) => set("firstname", e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Nachname *</label>
              <input className={inputCls} placeholder="Mustermann" value={form.lastname} onChange={(e) => set("lastname", e.target.value)} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">E-Mail</label>
              <input type="email" className={inputCls} placeholder="max@beispiel.de" value={form.email} onChange={(e) => set("email", e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Telefon</label>
              <input type="tel" className={inputCls} placeholder="+49 261 …" value={form.phone} onChange={(e) => set("phone", e.target.value)} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Mobil</label>
              <input type="tel" className={inputCls} placeholder="+49 151 …" value={form.mobile} onChange={(e) => set("mobile", e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Position</label>
              <input className={inputCls} placeholder="Geschäftsführer" value={form.position} onChange={(e) => set("position", e.target.value)} />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Abteilung</label>
            <input className={inputCls} placeholder="Einkauf" value={form.department} onChange={(e) => set("department", e.target.value)} />
          </div>

          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={form.is_primary}
              onChange={(e) => set("is_primary", e.target.checked)}
              className="h-4 w-4 rounded border-border accent-primary"
            />
            <span className="text-sm text-foreground">Hauptansprechpartner</span>
          </label>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Notizen</label>
            <textarea className={inputCls + " resize-none"} rows={2} value={form.notes} onChange={(e) => set("notes", e.target.value)} />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-border bg-secondary py-2 text-sm text-muted-foreground hover:text-foreground">
              Abbrechen
            </button>
            <button type="submit" disabled={saving}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-primary py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60">
              <Save className="h-4 w-4" />
              {saving ? "Speichern…" : isEdit ? "Speichern" : "Hinzufügen"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ─── Delete Confirm ──────────────────────────────────────────────────────────
function ConfirmDialog({ title, text, onCancel, onConfirm }: { title: string; text: string; onCancel: () => void; onConfirm: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-6">
        <h2 className="font-heading text-lg font-semibold text-foreground">{title}</h2>
        <p className="mt-1 text-sm text-muted-foreground">{text}</p>
        <div className="mt-5 flex gap-3">
          <button onClick={onCancel} className="flex-1 rounded-lg border border-border bg-secondary py-2 text-sm text-muted-foreground hover:text-foreground">
            Abbrechen
          </button>
          <button onClick={onConfirm} className="flex-1 rounded-lg bg-destructive py-2 text-sm font-medium text-white hover:bg-destructive/90">
            Löschen
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Activity Modal ──────────────────────────────────────────────────────────
const ACTIVITY_TYPES: { value: ActivityType; label: string }[] = [
  { value: "call", label: "Anruf" },
  { value: "email", label: "E-Mail" },
  { value: "onsite", label: "Vor Ort" },
  { value: "remote", label: "Remote" },
  { value: "note", label: "Notiz" },
]

function ActivityModal({ customerId, contacts, onClose, onSaved }: {
  customerId: string
  contacts: Contact[]
  onClose: () => void
  onSaved: () => void
}) {
  const today = new Date().toISOString().slice(0, 10)
  const [type, setType] = useState<ActivityType>("call")
  const [description, setDescription] = useState("")
  const [occurredAt, setOccurredAt] = useState(today)
  const [contactId, setContactId] = useState("")
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!description.trim()) return
    setSaving(true)
    try {
      await crmService.createActivity({
        customer_id: customerId,
        contact_id: contactId || null,
        type,
        description: description.trim(),
        occurred_at: occurredAt || undefined,
      })
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="font-heading text-base font-semibold text-foreground">Aktivität erfassen</h2>
          <button type="button" onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="h-5 w-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Typ</label>
              <select
                className={inputCls}
                value={type}
                onChange={e => setType(e.target.value as ActivityType)}
              >
                {ACTIVITY_TYPES.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Datum</label>
              <input
                type="date"
                className={inputCls}
                value={occurredAt}
                onChange={e => setOccurredAt(e.target.value)}
              />
            </div>
          </div>
          {contacts.length > 0 && (
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Ansprechpartner (optional)</label>
              <select className={inputCls} value={contactId} onChange={e => setContactId(e.target.value)}>
                <option value="">–</option>
                {contacts.map(c => (
                  <option key={c.id} value={c.id}>{c.firstname} {c.lastname}</option>
                ))}
              </select>
            </div>
          )}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Beschreibung *</label>
            <textarea
              className={inputCls + " resize-none"}
              rows={4}
              placeholder="Was ist passiert?"
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-border bg-secondary py-2 text-sm text-muted-foreground hover:text-foreground">
              Abbrechen
            </button>
            <button type="submit" disabled={saving || !description.trim()}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-primary py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60">
              <Save className="h-4 w-4" />
              {saving ? "Speichern…" : "Erfassen"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ─── CustomerDetail ──────────────────────────────────────────────────────────
export function CustomerDetail({ id }: { id: string }) {
  const router = useRouter()
  const { hasPermission } = useAuth()
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [contacts, setContacts] = useState<Contact[]>([])
  const [activities, setActivities] = useState<CrmActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  usePageTitle(customer?.name)

  // Contact modal state
  const [contactModal, setContactModal] = useState<{ open: boolean; contact?: Contact }>({ open: false })
  const [showActivityModal, setShowActivityModal] = useState(false)
  // Delete states
  const [deleteContactId, setDeleteContactId] = useState<string | null>(null)
  const [deleteCustomer, setDeleteCustomer] = useState(false)
  // Linked data tabs
  type LinkTab = "invoices" | "projects" | "tickets" | "contracts" | "assets" | "documents"
  const [linkTab, setLinkTab] = useState<LinkTab>("invoices")
  const [linkedInvoices, setLinkedInvoices] = useState<Invoice[] | null>(null)
  const [linkedProjects, setLinkedProjects] = useState<Project[] | null>(null)
  const [linkedTickets, setLinkedTickets] = useState<Ticket[] | null>(null)
  const [linkedContracts, setLinkedContracts] = useState<Contract[] | null>(null)
  const [linkedAssets, setLinkedAssets] = useState<{ assets: CustomerAsset[]; licenses: SoftwareLicense[] } | null>(null)
  const [portalMsg, setPortalMsg] = useState<string | null>(null)
  const [loadingLink, setLoadingLink] = useState(false)

  const loadLinkTab = useCallback(async (tab: LinkTab) => {
    setLoadingLink(true)
    try {
      if (tab === "invoices" && linkedInvoices === null) {
        const res = await invoiceService.list({ customer_id: id, limit: 50 })
        setLinkedInvoices(res.items ?? [])
      } else if (tab === "projects" && linkedProjects === null) {
        const data = await projectService.list({ customer_id: id })
        setLinkedProjects(data)
      } else if (tab === "tickets" && linkedTickets === null) {
        const res = await supportService.list({ customer_id: id, limit: 50 })
        setLinkedTickets(res.items ?? [])
      } else if (tab === "contracts" && linkedContracts === null) {
        const res = await contractsService.list({ customer_id: id, limit: 100 })
        setLinkedContracts(res.items)
      } else if (tab === "assets" && linkedAssets === null) {
        const [a, l] = await Promise.all([
          assetsService.list({ customer_id: id, limit: 200 }),
          assetsService.listLicenses({ customer_id: id, limit: 200 }),
        ])
        setLinkedAssets({ assets: a.items, licenses: l.items })
      }
    } finally {
      setLoadingLink(false)
    }
  }, [id, linkedInvoices, linkedProjects, linkedTickets, linkedContracts, linkedAssets])

  async function handlePortalInvite(ct: Contact) {
    setPortalMsg(null)
    try {
      const res = await crmService.inviteContactToPortal(ct.id)
      setContacts(cs => cs.map(c => c.id === ct.id ? { ...c, portal_enabled: true } : c))
      setPortalMsg(res.sent ? `Anmeldelink an ${res.email} gesendet.` : `Zugang aktiviert, aber E-Mail an ${res.email} konnte nicht gesendet werden.`)
    } catch (e: any) {
      setPortalMsg(e?.response?.data?.detail ?? "Einladung fehlgeschlagen.")
    }
  }

  async function handlePortalRevoke(ct: Contact) {
    await crmService.updateContact(ct.id, { portal_enabled: false })
    setContacts(cs => cs.map(c => c.id === ct.id ? { ...c, portal_enabled: false } : c))
    setPortalMsg(`Portal-Zugang für ${ct.firstname} ${ct.lastname} entzogen.`)
  }

  useEffect(() => { loadLinkTab(linkTab) }, [linkTab]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const [c, acts] = await Promise.all([
          crmService.getCustomer(id),
          crmService.getCustomerActivities(id, { limit: 20 }),
        ])
        setCustomer(c)
        setContacts(c.contacts ?? [])
        setActivities(acts)
      } catch (e: any) {
        setError(e?.message ?? "Fehler beim Laden")
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  async function handleDeleteContact() {
    if (!deleteContactId) return
    await crmService.deleteContact(deleteContactId)
    setContacts((cs) => cs.filter((c) => c.id !== deleteContactId))
    setDeleteContactId(null)
  }

  async function handleDeleteCustomer() {
    await crmService.deleteCustomer(id)
    router.push("/crm/customers")
  }

  function handleContactSaved(saved: Contact) {
    setContacts((cs) => {
      const idx = cs.findIndex((c) => c.id === saved.id)
      if (idx >= 0) {
        const next = [...cs]
        next[idx] = saved
        return next
      }
      return [...cs, saved]
    })
    setContactModal({ open: false })
  }

  if (loading) {
    return <div className="flex items-center justify-center py-24 text-muted-foreground text-sm">Laden…</div>
  }
  if (error || !customer) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-3">
        <p className="text-sm text-destructive">{error ?? "Kunde nicht gefunden"}</p>
        <button onClick={() => router.push("/crm/customers")} className="text-sm text-primary hover:underline">
          Zurück zur Liste
        </button>
      </div>
    )
  }

  return (
    <div className="px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <button
          onClick={() => router.push("/crm/customers")}
          className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="font-heading text-2xl font-bold text-foreground">{customer.name}</h1>
            <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", STATUS_COLORS[customer.status])}>
              {STATUS_LABELS[customer.status]}
            </span>
          </div>
          {customer.customer_number && (
            <p className="mt-0.5 text-sm text-muted-foreground">{customer.customer_number}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasPermission("backoffice.crm.write") && (
            <button
              onClick={() => router.push(`/crm/customers/${id}/edit`)}
              className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <Edit className="h-4 w-4" />
              Bearbeiten
            </button>
          )}
          {hasPermission("backoffice.crm.delete") && (
            <button
              onClick={() => setDeleteCustomer(true)}
              className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive transition-colors hover:bg-destructive/20"
            >
              <Trash2 className="h-4 w-4" />
              Löschen
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-xl border border-border bg-card p-5 space-y-4">
              <h2 className="font-heading text-sm font-semibold text-foreground">Kontaktdaten</h2>
              {customer.email ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Mail className="h-4 w-4 shrink-0" />
                  <a href={`mailto:${customer.email}`} className="hover:text-foreground">{customer.email}</a>
                </div>
              ) : null}
              {customer.phone ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Phone className="h-4 w-4 shrink-0" />
                  <span>{customer.phone}</span>
                </div>
              ) : null}
              {customer.website ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Globe className="h-4 w-4 shrink-0" />
                  <a href={customer.website} target="_blank" rel="noopener noreferrer" className="hover:text-foreground truncate">{customer.website}</a>
                </div>
              ) : null}
              {!customer.email && !customer.phone && !customer.website && (
                <p className="text-sm text-muted-foreground">Keine Kontaktdaten.</p>
              )}
            </div>

            <div className="rounded-xl border border-border bg-card p-5 space-y-4">
              <h2 className="font-heading text-sm font-semibold text-foreground">Adresse</h2>
              {customer.street || customer.city ? (
                <div className="flex items-start gap-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4 shrink-0 mt-0.5" />
                  <div>
                    {customer.street && <p>{customer.street}</p>}
                    {(customer.zip_code || customer.city) && (
                      <p>{[customer.zip_code, customer.city].filter(Boolean).join(" ")}</p>
                    )}
                    {customer.country && <p>{customer.country}</p>}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Keine Adresse hinterlegt.</p>
              )}
            </div>
          </div>

          {/* Contacts */}
          <div className="rounded-xl border border-border bg-card">
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Ansprechpartner <span className="ml-1 text-muted-foreground font-normal">({contacts.length})</span>
              </h2>
              {hasPermission("backoffice.crm.write") && (
                <button
                  onClick={() => setContactModal({ open: true })}
                  className="flex items-center gap-1.5 text-xs text-primary hover:text-primary/80"
                >
                  <Plus className="h-3.5 w-3.5" /> Hinzufügen
                </button>
              )}
            </div>
            {contacts.length === 0 ? (
              <p className="px-5 py-4 text-sm text-muted-foreground">Keine Ansprechpartner hinterlegt.</p>
            ) : (
              <>
              {portalMsg && <p className="border-b border-border/50 px-5 py-2 text-xs text-muted-foreground">{portalMsg}</p>}
              <ul className="divide-y divide-border/50">
                {contacts.map((ct) => (
                  <li key={ct.id} className="group flex items-center gap-3 px-5 py-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                      {ct.firstname[0]}{ct.lastname[0]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground flex items-center gap-1.5">
                        {ct.firstname} {ct.lastname}
                        {ct.is_primary && <Star className="h-3 w-3 text-amber-400 fill-amber-400" />}
                        {ct.portal_enabled && (
                          <span className="rounded-full bg-blue-500/15 px-1.5 py-0.5 text-[10px] font-medium text-blue-400" title={ct.portal_last_login_at ? `Letzter Login: ${new Date(ct.portal_last_login_at).toLocaleString("de-DE")}` : "Noch nicht angemeldet"}>
                            Portal
                          </span>
                        )}
                      </p>
                      {ct.position && <p className="text-xs text-muted-foreground">{ct.position}</p>}
                    </div>
                    <div className="text-right text-xs text-muted-foreground">
                      {ct.email && <p>{ct.email}</p>}
                      {ct.phone && <p>{ct.phone}</p>}
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {hasPermission("backoffice.crm.write") && ct.email && (
                        <button
                          onClick={() => ct.portal_enabled ? handlePortalRevoke(ct) : handlePortalInvite(ct)}
                          className={`rounded p-1 hover:text-foreground ${ct.portal_enabled ? "text-blue-400" : "text-muted-foreground"}`}
                          title={ct.portal_enabled ? "Portal-Zugang entziehen" : "Zum Kundenportal einladen"}
                        >
                          <KeyRound className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {hasPermission("backoffice.crm.write") && (
                        <button
                          onClick={() => setContactModal({ open: true, contact: ct })}
                          className="rounded p-1 text-muted-foreground hover:text-foreground"
                          title="Bearbeiten"
                        >
                          <Edit className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {hasPermission("backoffice.crm.delete") && (
                        <button
                          onClick={() => setDeleteContactId(ct.id)}
                          className="rounded p-1 text-muted-foreground hover:text-destructive"
                          title="Löschen"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
              </>
            )}
          </div>
        </div>

        {/* Aktivitäten */}
        <div className="rounded-xl border border-border bg-card">
          <div className="flex items-center justify-between border-b border-border px-5 py-4">
            <h2 className="font-heading text-sm font-semibold text-foreground">Aktivitäten</h2>
            {hasPermission("backoffice.crm.write") && (
              <button
                onClick={() => setShowActivityModal(true)}
                className="flex items-center gap-1 rounded-lg border border-border px-2 py-1 text-xs text-muted-foreground hover:text-foreground hover:border-primary/50 transition-colors"
              >
                <Plus className="h-3 w-3" />
                Neu
              </button>
            )}
          </div>
          {activities.length === 0 ? (
            <p className="px-5 py-4 text-sm text-muted-foreground">Keine Aktivitäten vorhanden.</p>
          ) : (
            <ul className="divide-y divide-border/50">
              {activities.map((a) => (
                <li key={a.id} className="px-5 py-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
                      {ACTIVITY_LABELS[a.type] ?? a.type}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(a.occurred_at).toLocaleDateString("de-DE")}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{a.description}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Linked data section */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b border-border">
          {([
            { id: "invoices" as const, label: "Rechnungen", icon: <FileText className="h-3.5 w-3.5" /> },
            { id: "projects" as const, label: "Projekte", icon: <FolderKanban className="h-3.5 w-3.5" /> },
            { id: "tickets" as const, label: "Support-Tickets", icon: <MessageSquare className="h-3.5 w-3.5" /> },
            ...(hasPermission("backoffice.contracts.read") ? [{ id: "contracts" as const, label: "Verträge", icon: <ScrollText className="h-3.5 w-3.5" /> }] : []),
            ...(hasPermission("backoffice.assets.read") ? [{ id: "assets" as const, label: "Geräte & Lizenzen", icon: <HardDrive className="h-3.5 w-3.5" /> }] : []),
            { id: "documents" as const, label: "Dokumente", icon: <FolderOpen className="h-3.5 w-3.5" /> },
          ]).map(t => (
            <button
              key={t.id}
              onClick={() => setLinkTab(t.id)}
              className={`flex items-center gap-1.5 border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
                linkTab === t.id
                  ? "border-primary text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {t.icon}{t.label}
            </button>
          ))}
        </div>

        <div className="min-h-[120px]">
          {loadingLink ? (
            <div className="py-10 text-center text-sm text-muted-foreground">Laden…</div>
          ) : linkTab === "invoices" ? (
            !linkedInvoices || linkedInvoices.length === 0 ? (
              <p className="px-5 py-6 text-sm text-muted-foreground">Keine Rechnungen vorhanden.</p>
            ) : (
              <div className="divide-y divide-border/50">
                {linkedInvoices.map(inv => {
                  const STATUS_COLOR: Record<string, string> = {
                    draft: "bg-muted text-muted-foreground", sent: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                    paid: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200", partial: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
                    overdue: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200", cancelled: "bg-muted text-muted-foreground",
                  }
                  const STATUS_LABELS: Record<string, string> = { draft: "Entwurf", sent: "Versendet", paid: "Bezahlt", partial: "Teilbezahlt", overdue: "Überfällig", cancelled: "Storniert" }
                  return (
                    <button
                      key={inv.id}
                      onClick={() => router.push(`/invoices/${inv.id}`)}
                      className="flex w-full items-center gap-3 px-5 py-3 hover:bg-muted/30 transition-colors text-left"
                    >
                      <span className="font-mono text-xs text-muted-foreground w-32 shrink-0">{inv.invoice_number}</span>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium shrink-0 ${STATUS_COLOR[inv.status] ?? "bg-muted"}`}>
                        {STATUS_LABELS[inv.status] ?? inv.status}
                      </span>
                      <span className="flex-1 text-xs text-muted-foreground">{inv.issued_date ? new Date(inv.issued_date).toLocaleDateString("de-DE") : "–"}</span>
                      <span className="text-sm font-medium shrink-0">
                        {parseFloat(inv.total).toLocaleString("de-DE", { style: "currency", currency: "EUR" })}
                      </span>
                    </button>
                  )
                })}
              </div>
            )
          ) : linkTab === "projects" ? (
            !linkedProjects || linkedProjects.length === 0 ? (
              <p className="px-5 py-6 text-sm text-muted-foreground">Keine Projekte vorhanden.</p>
            ) : (
              <div className="divide-y divide-border/50">
                {linkedProjects.map(p => {
                  const STATUS_COLOR: Record<string, string> = {
                    planning: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                    active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
                    on_hold: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
                    completed: "bg-muted text-muted-foreground", cancelled: "bg-muted text-muted-foreground",
                  }
                  const STATUS_LABELS: Record<string, string> = { planning: "Planung", active: "Aktiv", on_hold: "Pausiert", completed: "Abgeschlossen", cancelled: "Abgebrochen" }
                  return (
                    <button
                      key={p.id}
                      onClick={() => router.push(`/projects/${p.id}`)}
                      className="flex w-full items-center gap-3 px-5 py-3 hover:bg-muted/30 transition-colors text-left"
                    >
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium shrink-0 ${STATUS_COLOR[p.status] ?? "bg-muted"}`}>
                        {STATUS_LABELS[p.status] ?? p.status}
                      </span>
                      <span className="flex-1 text-sm font-medium">{p.title}</span>
                      <span className="text-xs text-muted-foreground shrink-0">
                        {p.start_date ? new Date(p.start_date).toLocaleDateString("de-DE") : "–"}
                        {" → "}
                        {p.end_date ? new Date(p.end_date).toLocaleDateString("de-DE") : "offen"}
                      </span>
                    </button>
                  )
                })}
              </div>
            )
          ) : linkTab === "tickets" ? (
            !linkedTickets || linkedTickets.length === 0 ? (
              <p className="px-5 py-6 text-sm text-muted-foreground">Keine Tickets vorhanden.</p>
            ) : (
              <div className="divide-y divide-border/50">
                {linkedTickets.map(t => {
                  const STATUS_COLOR: Record<string, string> = {
                    open: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
                    in_progress: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
                    waiting: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
                    resolved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
                    closed: "bg-muted text-muted-foreground",
                  }
                  const STATUS_LABELS: Record<string, string> = { open: "Offen", in_progress: "In Bearbeitung", waiting: "Wartend", resolved: "Gelöst", closed: "Geschlossen" }
                  const PRIORITY_COLOR: Record<string, string> = { low: "text-muted-foreground", medium: "text-blue-600", high: "text-orange-600", urgent: "text-red-600 font-semibold" }
                  return (
                    <button
                      key={t.id}
                      onClick={() => router.push(`/support/${t.id}`)}
                      className="flex w-full items-center gap-3 px-5 py-3 hover:bg-muted/30 transition-colors text-left"
                    >
                      <span className="font-mono text-xs text-muted-foreground w-24 shrink-0">{t.ticket_number}</span>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium shrink-0 ${STATUS_COLOR[t.status] ?? "bg-muted"}`}>
                        {STATUS_LABELS[t.status] ?? t.status}
                      </span>
                      <span className="flex-1 text-sm truncate">{t.title}</span>
                      <span className={`text-xs shrink-0 ${PRIORITY_COLOR[t.priority] ?? ""}`}>{t.priority}</span>
                    </button>
                  )
                })}
              </div>
            )
          ) : linkTab === "contracts" ? (
            !linkedContracts || linkedContracts.length === 0 ? (
              <p className="px-5 py-6 text-sm text-muted-foreground">Keine Verträge vorhanden.</p>
            ) : (
              <div className="divide-y divide-border/50">
                {linkedContracts.map(c => (
                  <button
                    key={c.id}
                    onClick={() => router.push(`/contracts/${c.id}`)}
                    className="flex w-full items-center gap-3 px-5 py-3 hover:bg-muted/30 transition-colors text-left"
                  >
                    <span className="font-mono text-xs text-muted-foreground w-28 shrink-0">{c.contract_number}</span>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium shrink-0 ${CONTRACT_STATUS_COLOR[c.status]}`}>
                      {CONTRACT_STATUS_LABELS[c.status]}
                    </span>
                    <span className="flex-1 text-sm truncate">{c.title}</span>
                    <span className="text-xs text-muted-foreground shrink-0">{fmtEur(c.net_amount_per_period)} {INTERVAL_LABELS[c.billing_interval]}</span>
                  </button>
                ))}
              </div>
            )
          ) : linkTab === "assets" ? (
            !linkedAssets || (linkedAssets.assets.length === 0 && linkedAssets.licenses.length === 0) ? (
              <p className="px-5 py-6 text-sm text-muted-foreground">Keine Geräte oder Lizenzen erfasst.</p>
            ) : (
              <div className="divide-y divide-border/50">
                {linkedAssets.assets.map(a => (
                  <div key={a.id} className="flex items-center gap-3 px-5 py-3">
                    <span className="font-mono text-xs text-muted-foreground w-24 shrink-0">{a.asset_tag}</span>
                    <span className="flex-1 text-sm truncate">{a.name}{a.serial_number ? ` · ${a.serial_number}` : ""}</span>
                    <span className="text-xs text-muted-foreground shrink-0">Garantie: {fmtDate(a.warranty_until)}</span>
                  </div>
                ))}
                {linkedAssets.licenses.map(l => (
                  <div key={l.id} className="flex items-center gap-3 px-5 py-3">
                    <span className="text-xs text-muted-foreground w-24 shrink-0">Lizenz</span>
                    <span className="flex-1 text-sm truncate">{l.product_name} ({l.seats} Plätze)</span>
                    <span className="text-xs text-muted-foreground shrink-0">bis {fmtDate(l.valid_until)}</span>
                  </div>
                ))}
              </div>
            )
          ) : (
            <div className="p-5">
              <DocumentsTab customerId={id} />
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showActivityModal && (
        <ActivityModal
          customerId={id}
          contacts={contacts}
          onClose={() => setShowActivityModal(false)}
          onSaved={async () => {
            setShowActivityModal(false)
            const acts = await crmService.getCustomerActivities(id, { limit: 20 })
            setActivities(acts)
          }}
        />
      )}

      {contactModal.open && (
        <ContactModal
          customerId={id}
          contact={contactModal.contact}
          onClose={() => setContactModal({ open: false })}
          onSaved={handleContactSaved}
        />
      )}

      {deleteContactId && (
        <ConfirmDialog
          title="Ansprechpartner löschen?"
          text="Diese Aktion kann nicht rückgängig gemacht werden."
          onCancel={() => setDeleteContactId(null)}
          onConfirm={handleDeleteContact}
        />
      )}

      {deleteCustomer && (
        <ConfirmDialog
          title={`„${customer.name}" löschen?`}
          text="Der Kunde und alle zugehörigen Daten werden dauerhaft gelöscht."
          onCancel={() => setDeleteCustomer(false)}
          onConfirm={handleDeleteCustomer}
        />
      )}
    </div>
  )
}
