"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { documentService } from "@/lib/documents/service"
import { hrService } from "@/lib/hr/service"
import type { DocumentRecord } from "@/lib/documents/types"
import type { Employee } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  UploadIcon, DownloadIcon, Trash2Icon, SearchIcon, FileIcon,
  FileTextIcon, FileImageIcon, LockIcon, FolderIcon, EyeIcon,
} from "lucide-react"
import Link from "next/link"
import { useAuth } from "@/components/providers/auth-provider"

const CATEGORIES = [
  "Vertrag", "Krankmeldung", "Zeugnis", "Rechnung", "Lohnabrechnung",
  "Angebot", "Protokoll", "Sonstiges",
]

const MODULES = ["HR", "Finance", "CRM", "Backoffice", "General"]

const MODULE_LABELS: Record<string, string> = {
  HR: "Personal",
  Finance: "Finanzen",
  CRM: "Kunde",
  Backoffice: "Backoffice",
  General: "Allgemein",
}

function fileIcon(type: string | null) {
  if (!type) return <FileIcon className="h-4 w-4" />
  if (type === "pdf") return <FileTextIcon className="h-4 w-4 text-red-500" />
  if (["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(type)) return <FileImageIcon className="h-4 w-4 text-blue-500" />
  return <FileIcon className="h-4 w-4 text-muted-foreground" />
}

function fmtSize(bytes: number | null) {
  if (!bytes) return "–"
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function fmtDate(d: string | null) {
  if (!d) return "–"
  return new Date(d).toLocaleDateString("de-DE")
}

// ---------------------------------------------------------------------------
// Upload dialog
// ---------------------------------------------------------------------------

interface UploadDialogProps {
  employees: Employee[]
  /** When set: upload is pinned to this employee, selector is hidden */
  presetOwnerId?: string
  /** When set: upload is pinned to this customer, selector is hidden */
  presetCustomerId?: string
  onClose: () => void
  onUploaded: () => void
}

function UploadDialog({ employees, presetOwnerId, presetCustomerId, onClose, onUploaded }: UploadDialogProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState("")
  const [category, setCategory] = useState("Sonstiges")
  const [module, setModule] = useState(
    presetCustomerId ? "CRM" : presetOwnerId ? "HR" : "General"
  )
  const [ownerId, setOwnerId] = useState(presetOwnerId ?? employees[0]?.id ?? "")
  const [confidential, setConfidential] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleUpload() {
    if (!file) return
    if (!presetCustomerId && !presetOwnerId && !ownerId) return
    setUploading(true)
    setError(null)
    try {
      await documentService.upload(file, {
        owner_id: presetOwnerId ?? (presetCustomerId ? undefined : ownerId),
        customer_id: presetCustomerId,
        title: title.trim() || file.name,
        category,
        linked_module: module,
        is_confidential: confidential,
      })
      onUploaded()
      onClose()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload fehlgeschlagen")
    } finally {
      setUploading(false)
    }
  }

  const canSubmit = !!file && (!!presetCustomerId || !!presetOwnerId || !!ownerId)

  return (
    <Dialog open onOpenChange={open => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Dokument hochladen</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          {/* File drop area */}
          <div
            onClick={() => inputRef.current?.click()}
            className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed p-6 transition-colors hover:border-primary/50 hover:bg-muted/30 ${file ? "border-primary/40 bg-primary/5" : "border-border"}`}
          >
            <UploadIcon className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              {file ? file.name : "Datei auswählen oder hier ablegen"}
            </p>
            {file && <p className="text-xs text-muted-foreground">{fmtSize(file.size)}</p>}
            <input
              ref={inputRef}
              type="file"
              className="hidden"
              onChange={e => {
                const f = e.target.files?.[0]
                if (f) { setFile(f); if (!title) setTitle(f.name) }
              }}
            />
          </div>

          <div className="grid gap-1.5">
            <Label>Titel</Label>
            <Input value={title} onChange={e => setTitle(e.target.value)} placeholder={file?.name ?? "Dokumenttitel…"} />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-1.5">
              <Label>Kategorie</Label>
              <Select value={category} onValueChange={v => v && setCategory(v)}>
                <SelectTrigger>
                  <span data-slot="select-value">{category}</span>
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Modul</Label>
              <Select value={module} onValueChange={v => v && setModule(v)} disabled={!!presetCustomerId || !!presetOwnerId}>
                <SelectTrigger>
                  <span data-slot="select-value">{MODULE_LABELS[module] ?? module}</span>
                </SelectTrigger>
                <SelectContent>
                  {MODULES.map(m => <SelectItem key={m} value={m}>{MODULE_LABELS[m] ?? m}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Only show employee selector in standalone mode */}
          {!presetOwnerId && !presetCustomerId && (
            <div className="grid gap-1.5">
              <Label>Mitarbeiter (Eigentümer)</Label>
              <Select value={ownerId} onValueChange={v => v && setOwnerId(v)}>
                <SelectTrigger>
                  <span data-slot="select-value" className={ownerId ? "" : "text-muted-foreground"}>
                    {ownerId
                      ? (() => { const e = employees.find(e => e.id === ownerId); return e ? `${e.first_name} ${e.last_name}` : "…" })()
                      : "Mitarbeiter wählen"}
                  </span>
                </SelectTrigger>
                <SelectContent>
                  {employees.map(e => (
                    <SelectItem key={e.id} value={e.id}>
                      {e.first_name} {e.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={confidential}
              onChange={e => setConfidential(e.target.checked)}
              className="h-4 w-4 rounded"
            />
            <span className="flex items-center gap-1.5 text-sm">
              <LockIcon className="h-3.5 w-3.5" />
              Vertraulich
            </span>
          </label>

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="outline" onClick={onClose}>Abbrechen</Button>
          <Button onClick={handleUpload} disabled={uploading || !canSubmit}>
            {uploading ? "Hochladen…" : "Hochladen"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Document table (shared)
// ---------------------------------------------------------------------------

interface DocTableProps {
  documents: DocumentRecord[]
  employeeMap: Record<string, string>
  downloading: string | null
  onDownload: (doc: DocumentRecord) => void
  onDeleteRequest: (doc: DocumentRecord) => void
  /** Hide owner column when embedded in employee/customer detail */
  hideOwner?: boolean
}

function DocTable({ documents, employeeMap, downloading, onDownload, onDeleteRequest, hideOwner }: DocTableProps) {
  const { hasPermission } = useAuth()
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
        <FolderIcon className="h-10 w-10 opacity-30" />
        <span className="text-sm">Keine Dokumente gefunden.</span>
      </div>
    )
  }

  return (
    <div className="rounded-lg border overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/40">
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Datei</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Kategorie</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Modul</th>
            {!hideOwner && <th className="px-4 py-3 text-left font-medium text-muted-foreground">Eigentümer</th>}
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Größe</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Hochgeladen</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          {documents.map(doc => (
            <tr key={doc.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
              <td className="px-4 py-3">
                <div className="flex items-center gap-2.5 min-w-0">
                  {fileIcon(doc.type)}
                  <div className="min-w-0">
                    <p className="font-medium truncate max-w-48">{doc.title ?? "–"}</p>
                    <p className="text-xs text-muted-foreground uppercase">{doc.type ?? "–"}</p>
                  </div>
                  {doc.is_confidential && (
                    <span title="Vertraulich"><LockIcon className="h-3.5 w-3.5 shrink-0 text-amber-500" /></span>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 text-muted-foreground">{doc.category ?? "–"}</td>
              <td className="px-4 py-3">
                {doc.linked_module ? (
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs">
                    {MODULE_LABELS[doc.linked_module] ?? doc.linked_module}
                  </span>
                ) : "–"}
              </td>
              {!hideOwner && (
                <td className="px-4 py-3 text-muted-foreground">
                  {doc.owner_id ? (employeeMap[doc.owner_id] ?? "…") : "–"}
                </td>
              )}
              <td className="px-4 py-3 text-muted-foreground tabular-nums">{fmtSize(doc.file_size)}</td>
              <td className="px-4 py-3 text-muted-foreground">{fmtDate(doc.uploaded_at)}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1 justify-end">
                  <Link
                    href={`/documents/${doc.id}`}
                    className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                    title="Details & Vorschau"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={() => onDownload(doc)}
                    disabled={downloading === doc.id}
                    className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                    title="Herunterladen"
                  >
                    <DownloadIcon className="h-4 w-4" />
                  </button>
                  {hasPermission("documents.delete") && (
                    <button
                      onClick={() => onDeleteRequest(doc)}
                      className="rounded p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
                      title="Löschen"
                    >
                      <Trash2Icon className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Core hook — shared by all three views
// ---------------------------------------------------------------------------

interface UseDocumentsOptions {
  ownerId?: string
  customerId?: string
}

function useDocuments({ ownerId, customerId }: UseDocumentsOptions = {}) {
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [filterModule, setFilterModule] = useState("all")
  const [filterCategory, setFilterCategory] = useState("all")
  const [page, setPage] = useState(0)
  const PAGE_SIZE = 50

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params: Parameters<typeof documentService.list>[0] = {
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
        owner_id: ownerId,
        customer_id: customerId,
      }
      if (search.trim()) params.search = search.trim()
      if (filterModule !== "all") params.linked_module = filterModule
      if (filterCategory !== "all") params.category = filterCategory
      const res = await documentService.list(params)
      setDocuments(res.documents)
      setTotal(res.total)
    } finally {
      setLoading(false)
    }
  }, [search, filterModule, filterCategory, page, ownerId, customerId])

  useEffect(() => { load() }, [load])

  return {
    documents, total, loading,
    search, setSearch: (v: string) => { setSearch(v); setPage(0) },
    filterModule, setFilterModule: (v: string) => { setFilterModule(v); setPage(0) },
    filterCategory, setFilterCategory: (v: string) => { setFilterCategory(v); setPage(0) },
    page, setPage,
    PAGE_SIZE,
    reload: load,
  }
}

// ---------------------------------------------------------------------------
// Embedded tab (Customer or Employee detail)
// ---------------------------------------------------------------------------

interface EmbeddedDocsProps {
  /** Filter by employee owner_id */
  ownerId?: string
  /** Filter by customer customer_id */
  customerId?: string
}

export function DocumentsTab({ ownerId, customerId }: EmbeddedDocsProps) {
  const { hasPermission } = useAuth()
  const [employees, setEmployees] = useState<Employee[]>([])
  const [showUpload, setShowUpload] = useState(false)
  const [deleteDoc, setDeleteDoc] = useState<DocumentRecord | null>(null)
  const [downloading, setDownloading] = useState<string | null>(null)

  const {
    documents, total, loading,
    search, setSearch,
    filterCategory, setFilterCategory,
    reload,
  } = useDocuments({ ownerId, customerId })

  useEffect(() => {
    if (!customerId) return
    hrService.listEmployees({ limit: 200 }).then(setEmployees).catch(() => {})
  }, [customerId])

  const employeeMap = Object.fromEntries(employees.map(e => [e.id, `${e.first_name} ${e.last_name}`]))

  async function handleDownload(doc: DocumentRecord) {
    setDownloading(doc.id)
    try { await documentService.download(doc.id, doc.title ?? undefined) }
    finally { setDownloading(null) }
  }

  async function handleDelete() {
    if (!deleteDoc) return
    await documentService.delete(deleteDoc.id)
    setDeleteDoc(null)
    reload()
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-40 max-w-xs">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Suchen…" className="pl-9 h-8 text-sm" />
        </div>
        <Select value={filterCategory} onValueChange={v => v && setFilterCategory(v)}>
          <SelectTrigger className="w-36 h-8 text-sm">
            <span data-slot="select-value">{filterCategory === "all" ? "Alle Kategorien" : filterCategory}</span>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Kategorien</SelectItem>
            {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
        <span className="ml-auto text-xs text-muted-foreground">{total} Dokument{total !== 1 ? "e" : ""}</span>
        {hasPermission("documents.write") && (
          <Button size="sm" onClick={() => setShowUpload(true)}>
            <UploadIcon className="mr-1.5 h-3.5 w-3.5" />
            Hochladen
          </Button>
        )}
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : (
        <DocTable
          documents={documents}
          employeeMap={employeeMap}
          downloading={downloading}
          onDownload={handleDownload}
          onDeleteRequest={setDeleteDoc}
          hideOwner
        />
      )}

      {showUpload && (
        <UploadDialog
          employees={employees}
          presetOwnerId={ownerId}
          presetCustomerId={customerId}
          onClose={() => setShowUpload(false)}
          onUploaded={reload}
        />
      )}

      <AlertDialog open={!!deleteDoc} onOpenChange={open => !open && setDeleteDoc(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Dokument löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              „{deleteDoc?.title ?? "Dieses Dokument"}" wird unwiderruflich gelöscht.
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

// ---------------------------------------------------------------------------
// Full dashboard (standalone /documents page)
// ---------------------------------------------------------------------------

export function DocumentsDashboard() {
  const { hasPermission } = useAuth()
  const [employees, setEmployees] = useState<Employee[]>([])
  const [showUpload, setShowUpload] = useState(false)
  const [deleteDoc, setDeleteDoc] = useState<DocumentRecord | null>(null)
  const [downloading, setDownloading] = useState<string | null>(null)
  const [filterConfidential, setFilterConfidential] = useState<"all" | "true" | "false">("all")

  const {
    documents, total, loading,
    search, setSearch,
    filterModule, setFilterModule,
    filterCategory, setFilterCategory,
    page, setPage, PAGE_SIZE,
    reload,
  } = useDocuments()

  useEffect(() => {
    hrService.listEmployees({ limit: 200 }).then(setEmployees).catch(() => {})
  }, [])

  const employeeMap = Object.fromEntries(employees.map(e => [e.id, `${e.first_name} ${e.last_name}`]))
  const totalPages = Math.ceil(total / PAGE_SIZE)

  async function handleDownload(doc: DocumentRecord) {
    setDownloading(doc.id)
    try { await documentService.download(doc.id, doc.title ?? undefined) }
    finally { setDownloading(null) }
  }

  async function handleDelete() {
    if (!deleteDoc) return
    await documentService.delete(deleteDoc.id)
    setDeleteDoc(null)
    reload()
  }

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Dokumente</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">{total} Dokument{total !== 1 ? "e" : ""} · Nextcloud-Speicher</p>
        </div>
        {hasPermission("documents.write") && (
          <Button onClick={() => setShowUpload(true)}>
            <UploadIcon className="mr-2 h-4 w-4" />
            Hochladen
          </Button>
        )}
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-48 max-w-xs">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Dokument suchen…" className="pl-9" />
        </div>
        <Select value={filterModule} onValueChange={v => v && setFilterModule(v)}>
          <SelectTrigger className="w-36">
            <span data-slot="select-value">{filterModule === "all" ? "Alle Module" : (MODULE_LABELS[filterModule] ?? filterModule)}</span>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Module</SelectItem>
            {MODULES.map(m => <SelectItem key={m} value={m}>{MODULE_LABELS[m] ?? m}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterCategory} onValueChange={v => v && setFilterCategory(v)}>
          <SelectTrigger className="w-36">
            <span data-slot="select-value">{filterCategory === "all" ? "Alle Kategorien" : filterCategory}</span>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Kategorien</SelectItem>
            {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={filterConfidential} onValueChange={v => v && setFilterConfidential(v as typeof filterConfidential)}>
          <SelectTrigger className="w-36">
            <span data-slot="select-value">
              {filterConfidential === "all" ? "Alle" : filterConfidential === "true" ? "Vertraulich" : "Öffentlich"}
            </span>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle</SelectItem>
            <SelectItem value="false">Öffentlich</SelectItem>
            <SelectItem value="true">Vertraulich</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
      ) : (
        <DocTable
          documents={documents}
          employeeMap={employeeMap}
          downloading={downloading}
          onDownload={handleDownload}
          onDeleteRequest={setDeleteDoc}
        />
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <Button variant="outline" size="sm" onClick={() => setPage(p => p - 1)} disabled={page === 0}>Zurück</Button>
          <span className="text-sm text-muted-foreground">Seite {page + 1} / {totalPages}</span>
          <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={page >= totalPages - 1}>Weiter</Button>
        </div>
      )}

      {showUpload && (
        <UploadDialog
          employees={employees}
          onClose={() => setShowUpload(false)}
          onUploaded={() => { setPage(0); reload() }}
        />
      )}

      <AlertDialog open={!!deleteDoc} onOpenChange={open => !open && setDeleteDoc(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Dokument löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              „{deleteDoc?.title ?? "Dieses Dokument"}" wird unwiderruflich aus Nextcloud und der Datenbank gelöscht.
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
