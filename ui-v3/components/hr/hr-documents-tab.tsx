"use client"

import { useState } from "react"
import { apiClient } from "@/lib/api/client"
import { hrService } from "@/lib/hr/service"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { EmployeeSelect } from "./employee-select"

// ---------- Konstanten ----------

const DOC_TYPE_LABELS: Record<string, string> = {
  contract: "Arbeitsvertrag",
  amendment: "Vertragsänderung",
  certificate: "Zertifikat",
  reference: "Arbeitszeugnis",
  warning: "Abmahnung",
  evaluation: "Beurteilung",
  proof_of_employment: "Beschäftigungsnachweis",
  tax_document: "Steuerdokument",
  other: "Sonstiges",
}

// ---------- lokale Helpers ----------

interface HrDocument {
  id: string
  employee_id: string
  document_type: string
  name: string
  created_at: string
}

async function createHrDocument(employeeId: string, payload: object) {
  const { data } = await apiClient.post(`/api/hr/documents/employees/${employeeId}/documents`, payload)
  return data
}

// ---------- Dialog: Dokument anlegen ----------

function CreateDocumentDialog({
  open,
  employeeId,
  onClose,
  onCreated,
}: {
  open: boolean
  employeeId: string
  onClose: () => void
  onCreated: () => void
}) {
  const [docType, setDocType] = useState("contract")
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [filePath, setFilePath] = useState("")
  const [saving, setSaving] = useState(false)

  function reset() { setDocType("contract"); setTitle(""); setDescription(""); setFilePath("") }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim() || !filePath.trim()) return
    setSaving(true)
    await createHrDocument(employeeId, {
      document_type: docType,
      title: title.trim(),
      file_path: filePath.trim(),
      ...(description.trim() ? { description: description.trim() } : {}),
    }).catch(() => null)
    setSaving(false)
    reset()
    onClose()
    onCreated()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dokument anlegen</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label htmlFor="doc-type">Dokumententyp</Label>
            <select
              id="doc-type"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              {Object.entries(DOC_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="doc-title">Titel *</Label>
            <Input id="doc-title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="doc-desc">Beschreibung</Label>
            <textarea
              id="doc-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="doc-path">Nextcloud-Pfad *</Label>
            <Input id="doc-path" value={filePath} onChange={(e) => setFilePath(e.target.value)} placeholder="/Mitarbeiter/..." required />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !title.trim() || !filePath.trim()}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ---------- Haupt-Komponente ----------

export function HrDocumentsTab() {
  const [employeeId, setEmployeeId] = useState("")
  const [employeeName, setEmployeeName] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [documents, setDocuments] = useState<HrDocument[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [docDialogOpen, setDocDialogOpen] = useState(false)

  async function fetchDocuments(id: string) {
    const { data } = await apiClient
      .get<HrDocument[]>(`/api/hr/documents/employees/${id}/documents`)
      .catch(() => ({ data: [] as HrDocument[] }))
    setDocuments(Array.isArray(data) ? data : [])
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

  async function handleDocCreated() {
    const id = employeeId || inputValue.trim()
    if (id) await fetchDocuments(id)
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border bg-muted/30 p-4">
        <p className="text-sm text-muted-foreground">
          Mitarbeiter-Dokumente sind personenbezogen. Mitarbeiter auswählen um Dokumente zu filtern.
        </p>
      </div>

      <div className="flex items-end gap-3">
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
          <Button variant="outline" onClick={() => setDocDialogOpen(true)}>+ Dokument</Button>
        )}
      </div>

      {searched && !loading && (
        <div>
          <h2 className="text-sm font-semibold mb-3">Dokumente — {employeeName || employeeId}</h2>
          {documents.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">Keine Dokumente vorhanden.</p>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Typ</th>
                    <th className="text-left px-4 py-3 font-medium text-muted-foreground">Erstellt</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {documents.map((d) => (
                    <tr key={d.id} className="hover:bg-muted/30">
                      <td className="px-4 py-3 font-medium">{d.name}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {DOC_TYPE_LABELS[d.document_type] ?? d.document_type}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {new Date(d.created_at).toLocaleDateString("de-DE")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <CreateDocumentDialog
        open={docDialogOpen}
        employeeId={employeeId || inputValue.trim()}
        onClose={() => setDocDialogOpen(false)}
        onCreated={handleDocCreated}
      />
    </div>
  )
}
