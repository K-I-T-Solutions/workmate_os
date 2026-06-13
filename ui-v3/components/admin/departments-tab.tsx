"use client"

import { useEffect, useState } from "react"
import { adminService } from "@/lib/admin/service"
import type { Department, DepartmentCreate } from "@/lib/admin/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { PlusIcon, Trash2Icon, PencilIcon } from "lucide-react"

function DeptForm({ initial, onSave, onClose }: {
  initial?: Department
  onSave: () => void
  onClose: () => void
}) {
  const [name, setName] = useState(initial?.name ?? "")
  const [code, setCode] = useState(initial?.code ?? "")
  const [description, setDescription] = useState(initial?.description ?? "")
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!name.trim() || !code.trim()) return
    setSaving(true)
    try {
      const payload: DepartmentCreate = {
        name: name.trim(),
        code: code.trim().toUpperCase(),
        description: description.trim() || null,
      }
      if (initial) {
        await adminService.updateDepartment(initial.id, payload)
      } else {
        await adminService.createDepartment(payload)
      }
      onSave()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Name *</Label>
          <Input value={name} onChange={e => setName(e.target.value)} placeholder="Entwicklung" />
        </div>
        <div className="grid gap-1.5">
          <Label>Kürzel *</Label>
          <Input value={code} onChange={e => setCode(e.target.value)} placeholder="DEV" className="uppercase" />
        </div>
      </div>
      <div className="grid gap-1.5">
        <Label>Beschreibung</Label>
        <Input value={description} onChange={e => setDescription(e.target.value)} placeholder="Kurze Beschreibung der Abteilung…" />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !name.trim() || !code.trim()}>
          {saving ? "Speichern…" : initial ? "Speichern" : "Anlegen"}
        </Button>
      </div>
    </div>
  )
}

export function DepartmentsTab() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editItem, setEditItem] = useState<Department | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    try {
      setDepartments(await adminService.listDepartments())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function handleDelete() {
    if (!deleteId) return
    await adminService.deleteDepartment(deleteId)
    setDeleteId(null)
    load()
  }

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="flex justify-end">
        <Button size="sm" onClick={() => { setEditItem(null); setShowForm(true) }}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Abteilung anlegen
        </Button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : departments.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Noch keine Abteilungen angelegt.
        </div>
      ) : (
        <div className="space-y-2">
          {departments.map(dept => (
            <div key={dept.id} className="group flex items-center justify-between rounded-lg border bg-card px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="rounded-md bg-muted px-2 py-0.5 text-xs font-mono font-medium">{dept.code}</span>
                <div>
                  <p className="font-medium">{dept.name}</p>
                  {dept.description && <p className="text-xs text-muted-foreground">{dept.description}</p>}
                </div>
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => { setEditItem(dept); setShowForm(true) }}>
                  <PencilIcon className="h-3.5 w-3.5" />
                </Button>
                <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:bg-destructive/10" onClick={() => setDeleteId(dept.id)}>
                  <Trash2Icon className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Dialog open={showForm} onOpenChange={open => !open && setShowForm(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editItem ? "Abteilung bearbeiten" : "Neue Abteilung"}</DialogTitle>
          </DialogHeader>
          <DeptForm
            initial={editItem ?? undefined}
            onSave={() => { setShowForm(false); load() }}
            onClose={() => setShowForm(false)}
          />
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteId} onOpenChange={open => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Abteilung löschen?</AlertDialogTitle>
            <AlertDialogDescription>Diese Abteilung wird unwiderruflich gelöscht.</AlertDialogDescription>
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
