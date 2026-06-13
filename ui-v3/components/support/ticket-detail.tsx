"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { supportService } from "@/lib/support/service"
import { hrService } from "@/lib/hr/service"
import type { TicketDetail, TicketComment } from "@/lib/support/types"
import type { Employee } from "@/lib/hr/types"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { ArrowLeftIcon, Trash2Icon, SendIcon, LockIcon, UserIcon } from "lucide-react"

const STATUS_LABELS: Record<string, string> = {
  open: "Offen", in_progress: "In Bearbeitung", waiting: "Wartend",
  resolved: "Gelöst", closed: "Geschlossen",
}
const STATUS_COLOR: Record<string, string> = {
  open: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  in_progress: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  waiting: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  resolved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  closed: "bg-muted text-muted-foreground",
}
const PRIORITY_LABELS: Record<string, string> = {
  low: "Niedrig", medium: "Mittel", high: "Hoch", urgent: "Dringend",
}
const PRIORITY_COLOR: Record<string, string> = {
  low: "text-muted-foreground", medium: "text-blue-600",
  high: "text-orange-600", urgent: "text-red-600",
}

function fmtDateTime(d: string) {
  return new Date(d).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" })
}

export function TicketDetailView({ id }: { id: string }) {
  const router = useRouter()
  const [ticket, setTicket] = useState<TicketDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [showDelete, setShowDelete] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  const [comment, setComment] = useState("")
  const [isInternal, setIsInternal] = useState(false)
  const [sending, setSending] = useState(false)
  const [deleteCommentId, setDeleteCommentId] = useState<string | null>(null)
  const [employees, setEmployees] = useState<Employee[]>([])
  const [assigningId, setAssigningId] = useState<string | null>(null)

  async function load() {
    const data = await supportService.get(id)
    setTicket(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [id])
  useEffect(() => {
    hrService.listEmployees({ limit: 100 }).then(setEmployees).catch(() => {})
  }, [])

  async function handleAssign(employeeId: string | null) {
    if (!ticket) return
    setAssigningId(employeeId)
    try {
      await supportService.update(id, { assignee_id: employeeId })
      setTicket(t => t ? { ...t, assignee_id: employeeId } : t)
    } finally {
      setAssigningId(null)
    }
  }

  async function handleStatusChange(status: string) {
    if (!ticket) return
    setUpdatingStatus(true)
    try {
      const updated = await supportService.update(id, { status })
      setTicket(t => t ? { ...t, status: updated.status } : t)
    } finally {
      setUpdatingStatus(false)
    }
  }

  async function handleDelete() {
    await supportService.delete(id)
    router.push("/support")
  }

  async function handleSendComment() {
    if (!comment.trim()) return
    setSending(true)
    try {
      await supportService.addComment(id, comment.trim(), isInternal)
      setComment("")
      load()
    } finally {
      setSending(false)
    }
  }

  async function handleDeleteComment() {
    if (!deleteCommentId || !ticket) return
    await supportService.deleteComment(ticket.id, deleteCommentId)
    setDeleteCommentId(null)
    load()
  }

  if (loading) return <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
  if (!ticket) return <div className="flex items-center justify-center py-24 text-sm text-destructive">Ticket nicht gefunden.</div>

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Header */}
      <div className="flex items-start gap-3">
        <Button variant="ghost" size="icon" className="shrink-0 mt-0.5" onClick={() => router.push("/support")}>
          <ArrowLeftIcon className="h-4 w-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs text-muted-foreground">{ticket.ticket_number}</span>
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[ticket.status] ?? "bg-muted"}`}>
              {STATUS_LABELS[ticket.status] ?? ticket.status}
            </span>
            <span className={`text-sm font-medium ${PRIORITY_COLOR[ticket.priority] ?? ""}`}>
              {PRIORITY_LABELS[ticket.priority] ?? ticket.priority}
            </span>
            {ticket.sla_breached && (
              <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">SLA überschritten</span>
            )}
          </div>
          <h1 className="mt-1 text-xl font-semibold">{ticket.title}</h1>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Select value={ticket.status} onValueChange={v => v && handleStatusChange(v)} disabled={updatingStatus}>
            <SelectTrigger className="w-40">
              <span data-slot="select-value" className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[ticket.status] ?? "bg-muted"}`}>
                {STATUS_LABELS[ticket.status] ?? ticket.status}
              </span>
            </SelectTrigger>
            <SelectContent>
              {Object.entries(STATUS_LABELS).map(([v, l]) => <SelectItem key={v} value={v}>{l}</SelectItem>)}
            </SelectContent>
          </Select>
          <Button variant="ghost" size="icon" className="text-destructive hover:bg-destructive/10" onClick={() => setShowDelete(true)}>
            <Trash2Icon className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 gap-3 rounded-lg border bg-card p-4 text-sm sm:grid-cols-5">
        {[
          { label: "Typ", value: ticket.type },
          { label: "Kategorie", value: ticket.category },
          { label: "Kanal", value: ticket.channel },
          { label: "Erstellt", value: fmtDateTime(ticket.created_at) },
        ].map(m => (
          <div key={m.label}>
            <p className="text-xs text-muted-foreground">{m.label}</p>
            <p className="mt-0.5 font-medium capitalize">{m.value}</p>
          </div>
        ))}
        <div>
          <p className="text-xs text-muted-foreground flex items-center gap-1"><UserIcon className="h-3 w-3" />Zugewiesen</p>
          <Select
            value={ticket.assignee_id ?? "none"}
            onValueChange={v => v && handleAssign(v === "none" ? null : v)}
            disabled={!!assigningId}
          >
            <SelectTrigger className="mt-0.5 h-7 text-xs px-2 w-40">
              <span data-slot="select-value" className={ticket.assignee_id ? "" : "text-muted-foreground"}>
                {ticket.assignee_id
                  ? (() => { const e = employees.find(e => e.id === ticket.assignee_id); return e ? `${e.first_name} ${e.last_name}` : "…" })()
                  : "Niemand"}
              </span>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Niemand</SelectItem>
              {employees.map(e => (
                <SelectItem key={e.id} value={e.id}>
                  {e.first_name} {e.last_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Description */}
      {ticket.description && (
        <div>
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Beschreibung</h2>
          <p className="rounded-lg border bg-card p-4 text-sm whitespace-pre-wrap">{ticket.description}</p>
        </div>
      )}

      {/* Comments */}
      <div>
        <h2 className="mb-3 text-sm font-medium text-muted-foreground">
          Kommentare {ticket.comments.length > 0 && `(${ticket.comments.length})`}
        </h2>
        <div className="space-y-3">
          {ticket.comments.map(c => (
            <CommentBubble
              key={c.id}
              comment={c}
              onDelete={() => setDeleteCommentId(c.id)}
            />
          ))}
        </div>

        {/* New comment */}
        <div className="mt-4 rounded-lg border bg-card p-4 space-y-3">
          <Textarea
            value={comment}
            onChange={e => setComment(e.target.value)}
            placeholder="Kommentar schreiben…"
            rows={3}
          />
          <div className="flex items-center justify-between">
            <button
              onClick={() => setIsInternal(v => !v)}
              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${isInternal ? "border-amber-400 bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300" : "border-border text-muted-foreground"}`}
            >
              <LockIcon className="h-3.5 w-3.5" />
              Intern
            </button>
            <Button size="sm" onClick={handleSendComment} disabled={sending || !comment.trim()}>
              <SendIcon className="mr-2 h-3.5 w-3.5" />
              {sending ? "Senden…" : "Senden"}
            </Button>
          </div>
        </div>
      </div>

      {/* Delete ticket */}
      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Ticket löschen?</AlertDialogTitle>
            <AlertDialogDescription>{ticket.ticket_number} wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Löschen</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete comment */}
      <AlertDialog open={!!deleteCommentId} onOpenChange={open => !open && setDeleteCommentId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Kommentar löschen?</AlertDialogTitle>
            <AlertDialogDescription>Dieser Kommentar wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteComment} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Löschen</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

function CommentBubble({ comment, onDelete }: { comment: TicketComment; onDelete: () => void }) {
  return (
    <div className={`group relative rounded-lg border p-4 ${comment.is_internal ? "border-amber-200 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-950/30" : "bg-card"}`}>
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          {comment.is_internal && (
            <span className="flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 dark:bg-amber-900 dark:text-amber-300">
              <LockIcon className="h-3 w-3" /> Intern
            </span>
          )}
          <span className="text-xs text-muted-foreground">
            {new Date(comment.created_at).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" })}
          </span>
        </div>
        <button
          onClick={onDelete}
          className="opacity-0 group-hover:opacity-100 p-1 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-opacity"
        >
          <Trash2Icon className="h-3.5 w-3.5" />
        </button>
      </div>
      <p className="text-sm whitespace-pre-wrap">{comment.content}</p>
    </div>
  )
}
