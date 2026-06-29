"use client"

import { useState, useEffect } from "react"
import { hrService } from "@/lib/hr/service"
import type { Course, CourseCreate } from "@/lib/hr/types"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

function CreateCourseDialog({
  open,
  onClose,
  onCreated,
}: {
  open: boolean
  onClose: () => void
  onCreated: (c: Course) => void
}) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [provider, setProvider] = useState("")
  const [courseType, setCourseType] = useState("internal")
  const [durationHours, setDurationHours] = useState("")
  const [cost, setCost] = useState("")
  const [saving, setSaving] = useState(false)

  function reset() {
    setTitle(""); setDescription(""); setProvider(""); setCourseType("internal")
    setDurationHours(""); setCost("")
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    setSaving(true)
    const payload: CourseCreate = {
      title: title.trim(),
      course_type: courseType,
      ...(description.trim() ? { description: description.trim() } : {}),
      ...(provider.trim() ? { provider: provider.trim() } : {}),
      ...(durationHours ? { duration_hours: parseFloat(durationHours) } : {}),
      ...(cost ? { cost: parseFloat(cost) } : {}),
    }
    const created = await hrService.createCourse(payload).catch(() => null)
    setSaving(false)
    if (created) { onCreated(created); reset(); onClose() }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Neue Schulung</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1.5">
            <Label htmlFor="ct-title">Titel *</Label>
            <Input id="ct-title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="ct-provider">Anbieter</Label>
            <Input id="ct-provider" value={provider} onChange={(e) => setProvider(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="ct-type">Art</Label>
            <select
              id="ct-type"
              value={courseType}
              onChange={(e) => setCourseType(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="internal">Intern</option>
              <option value="external">Extern</option>
              <option value="online">Online</option>
              <option value="certification">Zertifizierung</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="ct-duration">Dauer (Std.)</Label>
              <Input id="ct-duration" type="number" min="0" step="0.5" value={durationHours} onChange={(e) => setDurationHours(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="ct-cost">Kosten (€)</Label>
              <Input id="ct-cost" type="number" min="0" step="0.01" value={cost} onChange={(e) => setCost(e.target.value)} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="ct-desc">Beschreibung</Label>
            <Input id="ct-desc" value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !title.trim()}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export function TrainingTab() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)

  useEffect(() => {
    hrService.listCourses().then(setCourses).catch(() => {}).finally(() => setLoading(false))
  }, [])

  function handleCreated(c: Course) {
    setCourses((prev) => [c, ...prev])
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setDialogOpen(true)}>Neue Schulung</Button>
      </div>

      {loading && <p className="text-sm text-muted-foreground">Lädt...</p>}

      {!loading && courses.length === 0 && (
        <p className="py-8 text-center text-sm text-muted-foreground">Keine Einträge vorhanden.</p>
      )}

      {!loading && courses.length > 0 && (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Titel</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Anbieter</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Art</th>
                <th className="text-right px-4 py-3 font-medium text-muted-foreground">Dauer (Std.)</th>
                <th className="text-right px-4 py-3 font-medium text-muted-foreground">Kosten</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {courses.map((c) => (
                <tr key={c.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-medium">{c.title}</td>
                  <td className="px-4 py-3 text-muted-foreground">{c.provider ?? "—"}</td>
                  <td className="px-4 py-3">{c.course_type}</td>
                  <td className="px-4 py-3 text-right">{c.duration_hours ?? "—"}</td>
                  <td className="px-4 py-3 text-right">
                    {c.cost != null
                      ? new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(Number(c.cost))
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <CreateCourseDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onCreated={handleCreated}
      />
    </div>
  )
}
