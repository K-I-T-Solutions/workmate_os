"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { documentService } from "@/lib/documents/service"
import { apiClient } from "@/lib/api/client"
import type { DocumentRecord } from "@/lib/documents/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  ArrowLeftIcon, DownloadIcon, Trash2Icon, PencilIcon, CheckIcon, XIcon,
  FileIcon, FileTextIcon, FileImageIcon, LockIcon, UnlockIcon,
} from "lucide-react"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"

const CATEGORIES = [
  "Vertrag", "Krankmeldung", "Zeugnis", "Rechnung", "Lohnabrechnung",
  "Angebot", "Protokoll", "Sonstiges",
]

function fmtSize(bytes: number | null) {
  if (!bytes) return "–"
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

function fmtDate(d: string | null) {
  if (!d) return "–"
  return new Date(d).toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short" })
}

function FileTypeIcon({ type }: { type: string | null }) {
  if (type === "pdf") return <FileTextIcon className="h-5 w-5 text-red-500" />
  if (type && ["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(type))
    return <FileImageIcon className="h-5 w-5 text-blue-500" />
  return <FileIcon className="h-5 w-5 text-muted-foreground" />
}

// ---------------------------------------------------------------------------
// Preview
// ---------------------------------------------------------------------------
function DocumentPreview({ doc }: { doc: DocumentRecord }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [fileMissing, setFileMissing] = useState(false)
  const [error, setError] = useState(false)

  const type = (doc.type ?? doc.file_path.split(".").pop() ?? "").toLowerCase()
  const isImage = ["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(type)
  const isPdf = type === "pdf"
  const isMarkdown = type === "md"
  const canPreview = isImage || isPdf || isMarkdown

  const [markdownContent, setMarkdownContent] = useState<string | null>(null)

  useEffect(() => {
    if (!canPreview) { setLoading(false); return }
    if (isMarkdown) {
      apiClient
        .get(`/api/documents/${doc.id}/download`, { responseType: "text" })
        .then(({ data }) => setMarkdownContent(data))
        .catch((err) => {
          if (err?.response?.status === 404) setFileMissing(true)
          else setError(true)
        })
        .finally(() => setLoading(false))
      return
    }
    apiClient
      .get(`/api/documents/${doc.id}/download`, { responseType: "blob" })
      .then(({ data }) => {
        const mimeExt = type === "svg" ? "svg+xml" : (type === "jpg" ? "jpeg" : type)
        const mime = isPdf ? "application/pdf" : `image/${mimeExt}`
        const blob = new Blob([data], { type: mime })
        setObjectUrl(URL.createObjectURL(blob))
      })
      .catch((err) => {
        if (err?.response?.status === 404) setFileMissing(true)
        else setError(true)
      })
      .finally(() => setLoading(false))

    return () => { if (objectUrl) URL.revokeObjectURL(objectUrl) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doc.id])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg border bg-muted/30">
        <p className="text-sm text-muted-foreground">Vorschau wird geladen…</p>
      </div>
    )
  }

  if (fileMissing) {
    return (
      <div className="flex h-48 flex-col items-center justify-center gap-2 rounded-lg border border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-950/30">
        <FileIcon className="h-10 w-10 text-orange-400" />
        <p className="text-sm font-medium text-orange-700 dark:text-orange-400">Datei nicht mehr verfügbar</p>
        <p className="text-xs text-muted-foreground">Die Datei wurde nicht gefunden. Bitte erneut hochladen.</p>
      </div>
    )
  }

  if (error || !canPreview || !objectUrl) {
    return (
      <div className="flex h-48 flex-col items-center justify-center gap-2 rounded-lg border bg-muted/30">
        <FileIcon className="h-10 w-10 text-muted-foreground/40" />
        <p className="text-sm text-muted-foreground">
          {!canPreview ? "Keine Vorschau für diesen Dateityp verfügbar." : "Vorschau konnte nicht geladen werden."}
        </p>
      </div>
    )
  }

  if (isMarkdown && markdownContent !== null) {
    return (
      <div className="rounded-lg border bg-card p-6">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdownContent}</ReactMarkdown>
        </div>
      </div>
    )
  }

  if (isImage) {
    return (
      <div className="overflow-hidden rounded-lg border bg-muted/20">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={objectUrl} alt={doc.title ?? "Dokument"} className="max-h-[600px] w-full object-contain" />
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border">
      <iframe src={objectUrl} title={doc.title ?? "PDF-Vorschau"} className="h-[680px] w-full" />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export function DocumentDetail({ id }: { id: string }) {
  const router = useRouter()
  const [doc, setDoc] = useState<DocumentRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [downloadError, setDownloadError] = useState<string | null>(null)

  // edit state
  const [editing, setEditing] = useState(false)
  const [editTitle, setEditTitle] = useState("")
  const [editCategory, setEditCategory] = useState("")
  const [editConfidential, setEditConfidential] = useState(false)
  const [saving, setSaving] = useState(false)

  // delete
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function handleDownload() {
    if (!doc) return
    setDownloadError(null)
    try {
      await documentService.download(doc.id, doc.title ?? undefined)
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      setDownloadError(status === 404 ? "Datei nicht mehr verfügbar — bitte erneut hochladen." : "Download fehlgeschlagen.")
    }
  }

  useEffect(() => {
    documentService.get(id)
      .then(setDoc)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false))
  }, [id])

  function startEdit() {
    if (!doc) return
    setEditTitle(doc.title ?? "")
    setEditCategory(doc.category ?? "Sonstiges")
    setEditConfidential(doc.is_confidential)
    setEditing(true)
  }

  async function saveEdit() {
    if (!doc) return
    setSaving(true)
    const updated = await documentService.update(doc.id, {
      title: editTitle || undefined,
      category: editCategory,
      is_confidential: editConfidential,
    }).catch(() => null)
    if (updated) setDoc(updated)
    setSaving(false)
    setEditing(false)
  }

  async function handleDelete() {
    if (!doc) return
    setDeleting(true)
    await documentService.delete(doc.id).catch(() => {})
    router.push("/documents")
  }

  if (loading) {
    return <div className="px-8 py-12 text-sm text-muted-foreground">Lädt…</div>
  }

  if (notFound || !doc) {
    return (
      <div className="px-8 py-12 text-center">
        <p className="text-muted-foreground">Dokument nicht gefunden.</p>
        <Button variant="outline" className="mt-4" onClick={() => router.push("/documents")}>
          Zurück zur Übersicht
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6 px-8 py-6 max-w-4xl">

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => router.push("/documents")}>
            <ArrowLeftIcon className="h-4 w-4" />
          </Button>
          <div className="flex items-center gap-2">
            <FileTypeIcon type={doc.type} />
            {editing ? (
              <Input
                value={editTitle}
                onChange={e => setEditTitle(e.target.value)}
                className="h-8 text-lg font-semibold w-80"
                placeholder="Titel"
              />
            ) : (
              <h1 className="text-xl font-semibold">{doc.title || doc.file_path.split("/").pop()}</h1>
            )}
            {doc.is_confidential && !editing && (
              <span className="inline-flex items-center gap-1 rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700 dark:bg-orange-900/40 dark:text-orange-300">
                <LockIcon className="h-3 w-3" /> Vertraulich
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {editing ? (
            <>
              <Button size="sm" variant="outline" onClick={() => setEditing(false)} disabled={saving}>
                <XIcon className="h-4 w-4 mr-1" /> Abbrechen
              </Button>
              <Button size="sm" onClick={saveEdit} disabled={saving}>
                <CheckIcon className="h-4 w-4 mr-1" /> {saving ? "Speichern…" : "Speichern"}
              </Button>
            </>
          ) : (
            <>
              <Button size="sm" variant="outline" onClick={startEdit}>
                <PencilIcon className="h-4 w-4 mr-1" /> Bearbeiten
              </Button>
              <Button size="sm" variant="outline" onClick={handleDownload}>
                <DownloadIcon className="h-4 w-4 mr-1" /> Download
              </Button>
              <Button size="sm" variant="destructive" onClick={() => setConfirmDelete(true)}>
                <Trash2Icon className="h-4 w-4 mr-1" /> Löschen
              </Button>
            </>
          )}
        </div>
      </div>

      {downloadError && (
        <div className="rounded-lg border border-orange-200 bg-orange-50 px-4 py-3 text-sm text-orange-700 dark:border-orange-900 dark:bg-orange-950/30 dark:text-orange-400">
          {downloadError}
        </div>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <MetaCard label="Dateityp" value={doc.type?.toUpperCase() ?? "–"} />
        <MetaCard label="Größe" value={fmtSize(doc.file_size)} />
        <MetaCard label="Hochgeladen" value={fmtDate(doc.uploaded_at)} />
        <MetaCard label="Modul" value={doc.linked_module ?? "–"} />
        <div className="rounded-lg border bg-card p-4">
          <p className="text-xs text-muted-foreground">Kategorie</p>
          {editing ? (
            <Select value={editCategory} onValueChange={setEditCategory}>
              <SelectTrigger className="mt-1 h-8 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          ) : (
            <p className="mt-1 font-medium">{doc.category ?? "–"}</p>
          )}
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-xs text-muted-foreground">Vertraulich</p>
          {editing ? (
            <button
              type="button"
              onClick={() => setEditConfidential(v => !v)}
              className={`mt-1 inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${
                editConfidential
                  ? "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {editConfidential ? <LockIcon className="h-3 w-3" /> : <UnlockIcon className="h-3 w-3" />}
              {editConfidential ? "Ja" : "Nein"}
            </button>
          ) : (
            <p className="mt-1 font-medium">{doc.is_confidential ? "Ja" : "Nein"}</p>
          )}
        </div>
      </div>

      {/* Preview */}
      <div>
        <h2 className="mb-3 text-sm font-semibold text-muted-foreground uppercase tracking-wide">Vorschau</h2>
        <DocumentPreview doc={doc} />
      </div>

      {/* Delete Dialog */}
      <AlertDialog open={confirmDelete} onOpenChange={setConfirmDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Dokument löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              „{doc.title || doc.file_path.split("/").pop()}" wird unwiderruflich gelöscht.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleting ? "Löschen…" : "Endgültig löschen"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

function MetaCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-medium">{value}</p>
    </div>
  )
}
