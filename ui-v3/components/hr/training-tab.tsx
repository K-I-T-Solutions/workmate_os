"use client"

import { useState, useEffect } from "react"
import { hrService } from "@/lib/hr/service"
import { apiClient } from "@/lib/api/client"
import type { Course, CourseCreate } from "@/lib/hr/types"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { UserPlusIcon } from "lucide-react"
import { EmployeeSelect } from "./employee-select"
import { useAuth } from "@/components/providers/auth-provider"

// ---------- lokale Helpers ----------

async function createCertification(payload: {
  employee_id: string
  name: string
  issuer?: string
  issued_date: string
  expiry_date?: string
  skill_level?: string
}) {
  const { data } = await apiClient.post("/api/hr/certifications", payload)
  return data
}

interface Certification {
  id: string
  employee_id: string
  name: string
  issuer?: string
  issued_date: string
  expiry_date?: string
  skill_level?: string
}

// ---------- Dialog: Kurs erstellen ----------

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

// ---------- Dialog: Mitarbeiter einschreiben ----------

function EnrollDialog({
  courseId,
  onClose,
  onEnrolled,
}: {
  courseId: string | null
  onClose: () => void
  onEnrolled: () => void
}) {
  const [employeeId, setEmployeeId] = useState("")
  const [saving, setSaving] = useState(false)

  function reset() { setEmployeeId("") }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!courseId || !employeeId.trim()) return
    setSaving(true)
    await hrService.enrollEmployee(courseId, employeeId.trim()).catch(() => null)
    setSaving(false)
    reset()
    onClose()
    onEnrolled()
  }

  return (
    <Dialog open={!!courseId} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Mitarbeiter einschreiben</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <EmployeeSelect
            id="enroll-emp"
            label="Mitarbeiter *"
            value={employeeId}
            onChange={setEmployeeId}
            disabled={saving}
          />
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !employeeId.trim()}>
              {saving ? "Speichern…" : "Einschreiben"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ---------- Dialog: Zertifikat anlegen ----------

function CreateCertificationDialog({
  open,
  onClose,
  onCreated,
}: {
  open: boolean
  onClose: () => void
  onCreated: (cert: Certification) => void
}) {
  const [employeeId, setEmployeeId] = useState("")
  const [name, setName] = useState("")
  const [issuer, setIssuer] = useState("")
  const [issuedDate, setIssuedDate] = useState("")
  const [expiryDate, setExpiryDate] = useState("")
  const [skillLevel, setSkillLevel] = useState("beginner")
  const [saving, setSaving] = useState(false)

  function reset() {
    setEmployeeId(""); setName(""); setIssuer(""); setIssuedDate(""); setExpiryDate(""); setSkillLevel("beginner")
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!employeeId.trim() || !name.trim() || !issuedDate) return
    setSaving(true)
    const payload = {
      employee_id: employeeId.trim(),
      name: name.trim(),
      issued_date: issuedDate,
      ...(issuer.trim() ? { issuer: issuer.trim() } : {}),
      ...(expiryDate ? { expiry_date: expiryDate } : {}),
      skill_level: skillLevel,
    }
    const created = await createCertification(payload).catch(() => null)
    setSaving(false)
    if (created) { onCreated(created); reset(); onClose() }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) { reset(); onClose() } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Zertifikat anlegen</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <EmployeeSelect
            id="cert-emp"
            label="Mitarbeiter *"
            value={employeeId}
            onChange={setEmployeeId}
            disabled={saving}
          />
          <div className="space-y-1.5">
            <Label htmlFor="cert-name">Name *</Label>
            <Input id="cert-name" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="cert-issuer">Aussteller</Label>
            <Input id="cert-issuer" value={issuer} onChange={(e) => setIssuer(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="cert-issued">Ausstelldatum *</Label>
              <Input id="cert-issued" type="date" value={issuedDate} onChange={(e) => setIssuedDate(e.target.value)} required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="cert-expiry">Ablaufdatum</Label>
              <Input id="cert-expiry" type="date" value={expiryDate} onChange={(e) => setExpiryDate(e.target.value)} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="cert-level">Niveau</Label>
            <select
              id="cert-level"
              value={skillLevel}
              onChange={(e) => setSkillLevel(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="beginner">Einsteiger</option>
              <option value="intermediate">Fortgeschritten</option>
              <option value="advanced">Experte</option>
              <option value="expert">Profi</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => { reset(); onClose() }}>Abbrechen</Button>
            <Button type="submit" disabled={saving || !employeeId.trim() || !name.trim() || !issuedDate}>
              {saving ? "Speichern…" : "Erstellen"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ---------- Haupt-Komponente ----------

export function TrainingTab() {
  const { hasPermission } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [certDialogOpen, setCertDialogOpen] = useState(false)
  const [enrollCourseId, setEnrollCourseId] = useState<string | null>(null)
  const [certifications, setCertifications] = useState<Certification[]>([])
  const [certsLoading, setCertsLoading] = useState(true)

  useEffect(() => {
    hrService.listCourses().then(setCourses).catch(() => {}).finally(() => setLoading(false))
    apiClient
      .get<Certification[] | { items: Certification[] }>("/api/hr/certifications")
      .then(({ data }) => setCertifications(Array.isArray(data) ? data : (data as { items: Certification[] }).items ?? []))
      .catch(() => {})
      .finally(() => setCertsLoading(false))
  }, [])

  function handleCreated(c: Course) {
    setCourses((prev) => [c, ...prev])
  }

  function reloadCerts() {
    apiClient
      .get<Certification[] | { items: Certification[] }>("/api/hr/certifications")
      .then(({ data }) => setCertifications(Array.isArray(data) ? data : (data as { items: Certification[] }).items ?? []))
      .catch(() => {})
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end gap-2">
        {hasPermission("hr.manage") && (
          <Button variant="outline" onClick={() => setCertDialogOpen(true)}>Zertifikat +</Button>
        )}
        {hasPermission("hr.manage") && (
          <Button onClick={() => setDialogOpen(true)}>Neue Schulung</Button>
        )}
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
                <th className="px-4 py-3"></th>
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
                  <td className="px-4 py-3 text-right">
                    {hasPermission("hr.manage") && (
                      <Button
                        size="icon"
                        variant="ghost"
                        title="Mitarbeiter einschreiben"
                        onClick={() => setEnrollCourseId(c.id)}
                      >
                        <UserPlusIcon className="h-4 w-4" />
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Zertifikate-Abschnitt */}
      <div className="pt-4">
        <h2 className="text-sm font-semibold mb-3">Zertifikate</h2>
        {certsLoading && <p className="text-sm text-muted-foreground">Lädt...</p>}
        {!certsLoading && certifications.length === 0 && (
          <p className="py-4 text-center text-sm text-muted-foreground">Keine Zertifikate vorhanden.</p>
        )}
        {!certsLoading && certifications.length > 0 && (
          <div className="rounded-lg border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Mitarbeiter</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Aussteller</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Ausstelldatum</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Ablaufdatum</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {certifications.map((cert) => (
                  <tr key={cert.id} className="hover:bg-muted/30">
                    <td className="px-4 py-3 font-mono text-muted-foreground">
                      {cert.employee_id.slice(0, 8)}…
                    </td>
                    <td className="px-4 py-3 font-medium">{cert.name}</td>
                    <td className="px-4 py-3 text-muted-foreground">{cert.issuer ?? "—"}</td>
                    <td className="px-4 py-3">
                      {cert.issued_date ? new Date(cert.issued_date).toLocaleDateString("de-DE") : "—"}
                    </td>
                    <td className="px-4 py-3">
                      {cert.expiry_date ? new Date(cert.expiry_date).toLocaleDateString("de-DE") : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <CreateCourseDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onCreated={handleCreated}
      />

      <EnrollDialog
        courseId={enrollCourseId}
        onClose={() => setEnrollCourseId(null)}
        onEnrolled={() => {}}
      />

      <CreateCertificationDialog
        open={certDialogOpen}
        onClose={() => setCertDialogOpen(false)}
        onCreated={(cert) => {
          setCertifications((prev) => [cert, ...prev])
          reloadCerts()
        }}
      />
    </div>
  )
}
