"use client"

import { useState } from "react"
import { apiClient } from "@/lib/api/client"
import { Button } from "@/components/ui/button"
import { EmployeeSelect } from "./employee-select"

interface HrDocument {
  id: string
  employee_id: string
  document_type: string
  name: string
  created_at: string
}

export function HrDocumentsTab() {
  const [employeeId, setEmployeeId] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [documents, setDocuments] = useState<HrDocument[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!inputValue.trim()) return
    setLoading(true)
    const id = inputValue.trim()
    setEmployeeId(id)
    const { data } = await apiClient
      .get<HrDocument[] | { items: HrDocument[] }>(`/api/hr/documents`, { params: { employee_id: id } })
      .catch(() => ({ data: [] as HrDocument[] }))
    setDocuments(Array.isArray(data) ? data : (data as { items: HrDocument[] }).items ?? [])
    setSearched(true)
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border bg-muted/30 p-4">
        <p className="text-sm text-muted-foreground">
          Mitarbeiter-Dokumente sind personenbezogen. Mitarbeiter auswählen um Dokumente zu filtern.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex items-end gap-3 max-w-sm">
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

      {searched && !loading && (
        <div>
          <h2 className="text-sm font-semibold mb-3">Dokumente — {employeeId}</h2>
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
                      <td className="px-4 py-3 text-muted-foreground">{d.document_type}</td>
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
    </div>
  )
}
