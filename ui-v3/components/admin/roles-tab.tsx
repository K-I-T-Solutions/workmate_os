"use client"

import { useEffect, useState } from "react"
import { adminService } from "@/lib/admin/service"
import type { Role, RoleCreate } from "@/lib/admin/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlusIcon, Trash2Icon, PencilIcon, KeyIcon } from "lucide-react"
import { useAuth } from "@/components/providers/auth-provider"

function RoleForm({ initial, onSave, onClose }: {
  initial?: Role
  onSave: () => void
  onClose: () => void
}) {
  const [name, setName] = useState(initial?.name ?? "")
  const [description, setDescription] = useState(initial?.description ?? "")
  const [permissions, setPermissions] = useState(initial?.permissions_json ?? "")
  const [saving, setSaving] = useState(false)
  const [jsonError, setJsonError] = useState(false)

  function validateJson(v: string) {
    if (!v.trim()) { setJsonError(false); return }
    try { JSON.parse(v); setJsonError(false) } catch { setJsonError(true) }
  }

  async function handleSave() {
    if (!name.trim() || jsonError) return
    setSaving(true)
    try {
      const payload: RoleCreate = {
        name: name.trim(),
        description: description.trim() || null,
        permissions_json: permissions.trim() || null,
      }
      if (initial) {
        await adminService.updateRole(initial.id, payload)
      } else {
        await adminService.createRole(payload)
      }
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-1.5">
        <Label>Name *</Label>
        <Input value={name} onChange={e => setName(e.target.value)} placeholder="admin, viewer…" />
      </div>
      <div className="grid gap-1.5">
        <Label>Beschreibung</Label>
        <Input value={description} onChange={e => setDescription(e.target.value)} placeholder="Kurze Rollenbeschreibung…" />
      </div>
      <div className="grid gap-1.5">
        <Label>Berechtigungen (JSON)</Label>
        <Textarea
          value={permissions}
          onChange={e => { setPermissions(e.target.value); validateJson(e.target.value) }}
          rows={6}
          placeholder='{"invoices": ["read","write"], "hr": ["read"]}'
          className={`font-mono text-sm ${jsonError ? "border-destructive" : ""}`}
        />
        {jsonError && <p className="text-xs text-destructive">Ungültiges JSON</p>}
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !name.trim() || jsonError}>
          {saving ? "Speichern…" : initial ? "Speichern" : "Rolle anlegen"}
        </Button>
      </div>
    </div>
  )
}

export function RolesTab() {
  const { hasPermission } = useAuth()
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editItem, setEditItem] = useState<Role | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    try {
      setRoles(await adminService.listRoles())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function handleDelete() {
    if (!deleteId) return
    await adminService.deleteRole(deleteId)
    setDeleteId(null)
    load()
  }

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="flex justify-end">
        {hasPermission("employees.manage") && (
          <Button size="sm" onClick={() => { setEditItem(null); setShowForm(true) }}>
            <PlusIcon className="mr-2 h-4 w-4" />
            Rolle anlegen
          </Button>
        )}
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : roles.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Noch keine Rollen angelegt.
        </div>
      ) : (
        <div className="space-y-2">
          {roles.map(role => (
            <div key={role.id} className="rounded-lg border bg-card">
              <div className="group flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <KeyIcon className="h-4 w-4 text-muted-foreground shrink-0" />
                  <div>
                    <p className="font-medium">{role.name}</p>
                    {role.description && <p className="text-xs text-muted-foreground">{role.description}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  {role.permissions_json && (
                    <Button
                      variant="ghost" size="sm"
                      className="h-7 text-xs text-muted-foreground"
                      onClick={() => setExpandedId(expandedId === role.id ? null : role.id)}
                    >
                      Berechtigungen
                    </Button>
                  )}
                  {hasPermission("employees.manage") && (
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => { setEditItem(role); setShowForm(true) }}>
                        <PencilIcon className="h-3.5 w-3.5" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:bg-destructive/10" onClick={() => setDeleteId(role.id)}>
                        <Trash2Icon className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
              {expandedId === role.id && role.permissions_json && (
                <div className="border-t px-4 py-3">
                  <pre className="text-xs font-mono text-muted-foreground whitespace-pre-wrap break-all">
                    {(() => { try { return JSON.stringify(JSON.parse(role.permissions_json), null, 2) } catch { return role.permissions_json } })()}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Dialog open={showForm} onOpenChange={open => !open && setShowForm(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editItem ? "Rolle bearbeiten" : "Neue Rolle"}</DialogTitle>
          </DialogHeader>
          <RoleForm
            initial={editItem ?? undefined}
            onSave={() => { setShowForm(false); load() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Rolle löschen?</AlertDialogTitle>
            <AlertDialogDescription>Diese Rolle wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Löschen</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
