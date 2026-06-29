"use client"

import { useState } from "react"
import { documentService } from "@/lib/documents/service"
import type { DocumentRecord } from "@/lib/documents/types"
import { hrService } from "@/lib/hr/service"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { EmployeeSelect } from "./employee-select"
import { FileIcon, DownloadIcon, Trash2Icon } from "lucide-react"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"

const DOC_CATEGORY_LABELS: Record<string, string> = {
  Arbeitsvertrag: "Arbeitsvertrag",
  Vertragsänderung: "Vertragsänderung",
  Zertifikat: "Zertifikat",
  Arbeitszeugnis: "Arbeitszeugnis",
  Abmahnung: "Abmahnung",
  Beurteilung: "Beurteilung",
  Beschäftigungsnachweis: "Beschäftigungsnachweis",
  Steuerdokument: "Steuerdokument",
  Sonstiges: "Sonstiges",
}

function fmtBytes(bytes: number | null) {
  if (!bytes) return "–"
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function UploadDialog({
  open,
  employeeId,
  onClose,
  onUploaded,
}: {
  open: boolean
  employeeId: string
  onClose: () => void
  onUploaded: () => void
}) {
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState("")
  const [category, setCategory] = useState("Arbeitsvertrag")
  const [isConfidential, setIsConfidential] = useState(true)
  const [saving, setSaving] = useState(false)

  function reset() {
    setFile(null); setTitle(""); setCategory("Arbeitsvertrag"); setIsConfidential(true)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return
    setSaving(true)
    await documentService.upload(file, {
      owner_id: employeeId,
      title: title.trim() || file.name,
      category,
      linked_module: "HR",
      is_confidential: isConfidential,
    }).catch(() => null)
    setSaving(false)
    reset()
    onClose()
    onUploaded()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dokument hochladen</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label>Datei *</Label>
            <Input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              required
            />
          </div>
          <div className="space-y-1.5">
            <Label>Titel</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Leer = Dateiname"
            />
          </div>
          <div className="space-y-1.5">
            <Label>Kategorie</Label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              {Object.entries(DOC_CATEGORY_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={isConfidential}
              onChange={(e) => setIsConfidential(e.target.checked)}
              className="h-4 w-4 rounded border-input"
            />
            Vertraulich
          </label>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>
              Abbrechen
            </Button>
            <Button type="submit" disabled={saving || !file}>
              {saving ? "Hochladen…" : "Hochladen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export function HrDocumentsTab() {
  const [employeeId, setEmployeeId] = useState("")
  const [employeeName, setEmployeeName] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<DocumentRecord | null>(null)
  const [deleting, setDeleting] = useState(false)

  async function fetchDocuments(id: string) {
    const res = await documentService.list({ owner_id: id, linked_module: "HR", limit: 200 })
    setDocuments(res.documents)
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!inputValue.trim()) return
    setLoading(true)
    const id = inputValue.trim()
    setEmployeeId(id)
    const emp = await hrService.getEmployee(id).catch(() => null)
    if (emp) {
      const nr = emp.workmate_id ?? emp.employee_code
      setEmployeeName(nr ? `${nr} — ${emp.first_name} ${emp.last_name}` : `${emp.first_name} ${emp.last_name}`)
    }
    await fetchDocuments(id)
    setSearched(true)
    setLoading(false)
  }

  async function handleDelete() {
    if (!deleteTarget) return
    setDeleting(true)
    await documentService.delete(deleteTarget.id).catch(() => {})
    setDeleting(false)
    setDeleteTarget(null)
    await fetchDocuments(employeeId)
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border bg-muted/30 p-4">
        <p className="text-sm text-muted-foreground">
          Mitarbeiter auswählen um Personaldokumente zu filtern.
        </p>
      </div>

      <div className="flex items-end gap-3 flex-wrap">
        <form onSubmit={handleSearch} className="flex items-end gap-3 max-w-sm flex-1">
          <div className="flex-1">
            <EmployeeSelect
              id="doc-emp"
              label="Mitarbeiter"
              value={inputValue}
              onChange={setInputValue}
              disabled={loading}
            />
          </div>
          <Button type="submit" disabled={loading || !inputValue.trim()}>
            {loading ? "Lädt…" : "Anzeigen"}
          </Button>
        </form>
        {inputValue.trim() && (
          <Button variant="outline" onClick={() => setUploadOpen(true)}>
            + Dokument
          </Button>
        )}
      </div>

      {searched && !loading && (
        <div>
          <h2 className="text-sm font-semibold mb-3">
            Dokumente — {employeeName || employeeId}
          </h2>
          {documents.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Keine Dokumente vorhanden.
            </p>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Datei</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Kategorie</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Größe</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Hochgeladen</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {documents.map((d) => (
                    <tr key={d.id} className="hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <FileIcon className="h-4 w-4 text-muted-foreground shrink-0" />
                          <span className="font-medium">{d.title ?? "–"}</span>
                          {d.is_confidential && (
                            <span className="text-xs bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300 rounded px-1.5 py-0.5">
                              Vertraulich
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {DOC_CATEGORY_LABELS[d.category ?? ""] ?? d.category ?? "–"}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{fmtBytes(d.file_size)}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {d.uploaded_at ? new Date(d.uploaded_at).toLocaleDateString("de-DE") : "–"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1 justify-end">
                          <Button
                            size="icon" variant="ghost" className="h-7 w-7"
                            title="Herunterladen"
                            onClick={() => documentService.download(d.id, d.title ?? undefined)}
                          >
                            <DownloadIcon className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            size="icon" variant="ghost"
                            className="h-7 w-7 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                            title="Löschen"
                            onClick={() => setDeleteTarget(d)}
                          >
                            <Trash2Icon className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <UploadDialog
        open={uploadOpen}
        employeeId={employeeId || inputValue.trim()}
        onClose={() => setUploadOpen(false)}
        onUploaded={() => fetchDocuments(employeeId || inputValue.trim())}
      />

      <AlertDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Dokument löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              {deleteTarget && `„${deleteTarget.title}" wird endgültig gelöscht.`}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleting ? "Löschen…" : "Löschen"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
