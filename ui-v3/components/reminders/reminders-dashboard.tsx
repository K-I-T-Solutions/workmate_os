"use client"

import { useState, useEffect } from "react"
import { remindersService } from "@/lib/reminders/service"
import type { Reminder, ReminderCreate, ReminderPriority } from "@/lib/reminders/types"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/components/providers/auth-provider"

type Tab = "open" | "done"

const TABS: { id: Tab; label: string }[] = [
  { id: "open", label: "Offen" },
  { id: "done", label: "Erledigt" },
]

const PRIORITY_LABELS: Record<ReminderPriority, string> = {
  high: "Hoch",
  medium: "Mittel",
  low: "Niedrig",
}

const PRIORITY_CLASSES: Record<ReminderPriority, string> = {
  high: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  low: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
}

function PriorityBadge({ priority }: { priority: ReminderPriority }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITY_CLASSES[priority]}`}>
      {PRIORITY_LABELS[priority]}
    </span>
  )
}

function ReminderCard({
  reminder,
  onDone,
  onDelete,
}: {
  reminder: Reminder
  onDone?: (id: string) => void
  onDelete: (id: string) => void
}) {
  const { hasPermission } = useAuth()
  return (
    <div className="rounded-lg border bg-card p-4 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-1 flex-1 min-w-0">
          <p className="font-medium text-sm leading-tight">{reminder.title}</p>
          {reminder.description && (
            <p className="text-xs text-muted-foreground line-clamp-2">{reminder.description}</p>
          )}
        </div>
        <PriorityBadge priority={reminder.priority} />
      </div>
      {reminder.due_date && (
        <p className="text-xs text-muted-foreground">
          Fällig: {new Date(reminder.due_date).toLocaleDateString("de-DE")}
        </p>
      )}
      <div className="flex items-center gap-2 pt-1">
        {onDone && hasPermission("reminders.write") && (
          <Button size="sm" variant="outline" onClick={() => onDone(reminder.id)}>
            Erledigt
          </Button>
        )}
        {hasPermission("reminders.delete") && (
          <Button
            size="sm"
            variant="ghost"
            className="text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={() => onDelete(reminder.id)}
          >
            Löschen
          </Button>
        )}
      </div>
    </div>
  )
}

function CreateDialog({
  open,
  onClose,
  onCreated,
}: {
  open: boolean
  onClose: () => void
  onCreated: (r: Reminder) => void
}) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [dueDate, setDueDate] = useState("")
  const [priority, setPriority] = useState<ReminderPriority>("medium")
  const [saving, setSaving] = useState(false)

  function reset() {
    setTitle("")
    setDescription("")
    setDueDate("")
    setPriority("medium")
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    setSaving(true)
    const payload: ReminderCreate = {
      title: title.trim(),
      ...(description.trim() ? { description: description.trim() } : {}),
      ...(dueDate ? { due_date: dueDate } : {}),
      priority,
    }
    const created = await remindersService.create(payload).catch(() => null)
    setSaving(false)
    if (created) {
      onCreated(created)
      reset()
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Neue Erinnerung</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label htmlFor="r-title">Titel *</Label>
            <Input id="r-title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="r-desc">Beschreibung</Label>
            <Textarea id="r-desc" value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="r-date">Fälligkeitsdatum</Label>
            <Input id="r-date" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="r-priority">Priorität</Label>
            <select
              id="r-priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value as ReminderPriority)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="low">Niedrig</option>
              <option value="medium">Mittel</option>
              <option value="high">Hoch</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>
              Abbrechen
            </Button>
            <Button type="submit" disabled={saving || !title.trim()}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export function RemindersDashboard() {
  const { hasPermission } = useAuth()
  const [tab, setTab] = useState<Tab>("open")
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)

  function load() {
    setLoading(true)
    remindersService.list().then(setReminders).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  async function handleDone(id: string) {
    await remindersService.markDone(id).catch(() => {})
    load()
  }

  async function handleDelete(id: string) {
    await remindersService.remove(id).catch(() => {})
    setReminders((prev) => prev.filter((r) => r.id !== id))
  }

  function handleCreated(r: Reminder) {
    setReminders((prev) => [r, ...prev])
  }

  const sorted = [...reminders].sort((a, b) => {
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return a.due_date.localeCompare(b.due_date)
  })

  const open = sorted.filter((r) => !r.is_done)
  const done = sorted.filter((r) => r.is_done)
  const visible = tab === "open" ? open : done

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Erinnerungen</h1>
        {hasPermission("reminders.write") && (
          <Button onClick={() => setDialogOpen(true)}>Neue Erinnerung</Button>
        )}
      </div>

      <div className="flex gap-1 border-b">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === t.id
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.label}
            <span className="ml-1.5 text-xs text-muted-foreground">
              ({t.id === "open" ? open.length : done.length})
            </span>
          </button>
        ))}
      </div>

      {loading && <p className="text-sm text-muted-foreground">Lädt...</p>}

      {!loading && visible.length === 0 && (
        <p className="py-8 text-center text-sm text-muted-foreground">
          {tab === "open" ? "Keine offenen Erinnerungen." : "Keine erledigten Erinnerungen."}
        </p>
      )}

      {!loading && visible.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {visible.map((r) => (
            <ReminderCard
              key={r.id}
              reminder={r}
              onDone={tab === "open" ? handleDone : undefined}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      <CreateDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onCreated={handleCreated}
      />
    </div>
  )
}
