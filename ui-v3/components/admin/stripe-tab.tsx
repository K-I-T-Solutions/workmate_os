"use client"

import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog"
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { PlusIcon, Trash2Icon, PencilIcon } from "lucide-react"

interface StripeConfig {
  id: string
  publishable_key: string
  secret_key: string
  webhook_secret: string | null
  test_mode: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

interface FormState {
  publishable_key: string
  secret_key: string
  webhook_secret: string
  test_mode: boolean
  is_active: boolean
}

function emptyForm(): FormState {
  return { publishable_key: "", secret_key: "", webhook_secret: "", test_mode: true, is_active: false }
}

function fromConfig(c: StripeConfig): FormState {
  return {
    publishable_key: c.publishable_key,
    secret_key: c.secret_key,
    webhook_secret: c.webhook_secret ?? "",
    test_mode: c.test_mode,
    is_active: c.is_active,
  }
}

export function StripeTab() {
  const [configs, setConfigs] = useState<StripeConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm())
  const [saving, setSaving] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    try {
      const { data } = await apiClient.get<StripeConfig[]>("/api/backoffice/finance/stripe")
      setConfigs(Array.isArray(data) ? data : [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  function openCreate() {
    setEditId(null)
    setForm(emptyForm())
    setDialogOpen(true)
  }

  function openEdit(c: StripeConfig) {
    setEditId(c.id)
    setForm(fromConfig(c))
    setDialogOpen(true)
  }

  async function handleSave() {
    setSaving(true)
    try {
      const payload = {
        publishable_key: form.publishable_key,
        secret_key: form.secret_key,
        webhook_secret: form.webhook_secret || null,
        test_mode: form.test_mode,
        is_active: form.is_active,
      }
      if (editId) {
        await apiClient.put(`/api/backoffice/finance/stripe/${editId}`, payload)
      } else {
        await apiClient.post("/api/backoffice/finance/stripe", payload)
      }
      setDialogOpen(false)
      await load()
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!deleteId) return
    await apiClient.delete(`/api/backoffice/finance/stripe/${deleteId}`)
    setDeleteId(null)
    await load()
  }

  function set(field: keyof FormState, value: string | boolean) {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-medium">Stripe-Konfiguration</h2>
          <p className="text-sm text-muted-foreground">API-Keys und Webhook für Stripe-Zahlungen</p>
        </div>
        <Button size="sm" onClick={openCreate}>
          <PlusIcon className="mr-1.5 h-3.5 w-3.5" />
          Konfiguration hinzufügen
        </Button>
      </div>

      {loading ? (
        <p className="text-sm text-muted-foreground">Laden…</p>
      ) : configs.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
          Noch keine Stripe-Konfiguration vorhanden.
        </div>
      ) : (
        <div className="space-y-3">
          {configs.map(c => (
            <div key={c.id} className="rounded-lg border bg-card p-4 flex items-start justify-between gap-4">
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-sm truncate">{c.publishable_key}</span>
                  <span className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium ${
                    c.test_mode ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400" : "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                  }`}>
                    {c.test_mode ? "Test" : "Live"}
                  </span>
                  {c.is_active && (
                    <span className="inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                      Aktiv
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground font-mono">{c.secret_key}</p>
                {c.webhook_secret && (
                  <p className="text-xs text-muted-foreground">Webhook: {c.webhook_secret}</p>
                )}
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEdit(c)}>
                  <PencilIcon className="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="ghost" size="icon"
                  className="h-8 w-8 hover:text-destructive hover:bg-destructive/10"
                  onClick={() => setDeleteId(c.id)}
                >
                  <Trash2Icon className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editId ? "Konfiguration bearbeiten" : "Neue Stripe-Konfiguration"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Publishable Key *</Label>
              <Input
                placeholder="pk_test_… oder pk_live_…"
                value={form.publishable_key}
                onChange={e => set("publishable_key", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Secret Key *</Label>
              <Input
                placeholder="sk_test_… oder sk_live_…"
                value={form.secret_key}
                onChange={e => set("secret_key", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Webhook Secret</Label>
              <Input
                placeholder="whsec_… (optional)"
                value={form.webhook_secret}
                onChange={e => set("webhook_secret", e.target.value)}
              />
            </div>
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Test-Modus</p>
                <p className="text-xs text-muted-foreground">Stripe-Sandbox verwenden</p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={form.test_mode}
                onClick={() => set("test_mode", !form.test_mode)}
                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                  form.test_mode ? "bg-primary" : "bg-muted"
                }`}
              >
                <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform ${
                  form.test_mode ? "translate-x-4" : "translate-x-0"
                }`} />
              </button>
            </div>
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Aktiv</p>
                <p className="text-xs text-muted-foreground">Diese Konfiguration für Zahlungen verwenden</p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={form.is_active}
                onClick={() => set("is_active", !form.is_active)}
                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                  form.is_active ? "bg-primary" : "bg-muted"
                }`}
              >
                <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform ${
                  form.is_active ? "translate-x-4" : "translate-x-0"
                }`} />
              </button>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Abbrechen</Button>
            <Button onClick={handleSave} disabled={saving || !form.publishable_key || !form.secret_key}>
              {saving ? "Speichern…" : "Speichern"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Konfiguration löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              Diese Aktion kann nicht rückgängig gemacht werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
