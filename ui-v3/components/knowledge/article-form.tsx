"use client"

import { useEffect, useState } from "react"
import { knowledgeService } from "@/lib/knowledge/service"
import type { KBArticleDetail, KBCategory, ArticleStatus } from "@/lib/knowledge/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CheckCircle2Icon, CircleIcon } from "lucide-react"

const STATUS_OPTIONS: { value: ArticleStatus; label: string }[] = [
  { value: "draft", label: "Entwurf" },
  { value: "published", label: "Veröffentlicht" },
  { value: "archived", label: "Archiviert" },
]

export function ArticleForm({
  initial,
  categories,
  onSave,
  onCancel,
}: {
  initial?: KBArticleDetail
  categories: KBCategory[]
  onSave: (article: KBArticleDetail) => void
  onCancel: () => void
}) {
  const [title, setTitle] = useState(initial?.title ?? "")
  const [content, setContent] = useState(initial?.content ?? "")
  const [excerpt, setExcerpt] = useState(initial?.excerpt ?? "")
  const [categoryId, setCategoryId] = useState(initial?.category_id ?? "none")
  const [status, setStatus] = useState<ArticleStatus>(initial?.status ?? "draft")
  const [tagsInput, setTagsInput] = useState((initial?.tags ?? []).join(", "))
  const [pinned, setPinned] = useState(initial?.pinned ?? false)
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!title.trim() || !content.trim()) return
    setSaving(true)
    try {
      const tags = tagsInput.split(",").map(t => t.trim()).filter(Boolean)
      const payload = {
        title: title.trim(),
        content: content.trim(),
        excerpt: excerpt.trim() || null,
        category_id: categoryId === "none" ? null : categoryId,
        status,
        tags,
        pinned,
      }
      const result = initial
        ? await knowledgeService.updateArticle(initial.id, payload)
        : await knowledgeService.createArticle(payload)
      onSave(result)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-5">
      <div className="grid gap-1.5">
        <Label>Titel *</Label>
        <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Artikeltitel…" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-1.5">
          <Label>Kategorie</Label>
          <Select value={categoryId} onValueChange={v => v && setCategoryId(v)}>
            <SelectTrigger>
              <span data-slot="select-value" className={categoryId === "none" ? "text-muted-foreground" : ""}>
                {categoryId === "none"
                  ? "Keine Kategorie"
                  : (categories.find(c => c.id === categoryId)?.name ?? "…")}
              </span>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">Keine Kategorie</SelectItem>
              {categories.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Status</Label>
          <Select value={status} onValueChange={v => v && setStatus(v as ArticleStatus)}>
            <SelectTrigger>
              <span data-slot="select-value">
                {STATUS_OPTIONS.find(s => s.value === status)?.label ?? status}
              </span>
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="grid gap-1.5">
        <Label>Kurzbeschreibung</Label>
        <Input value={excerpt} onChange={e => setExcerpt(e.target.value)} placeholder="Kurze Zusammenfassung für die Listenansicht…" />
      </div>
      <div className="grid gap-1.5">
        <Label>Inhalt *</Label>
        <Textarea
          value={content}
          onChange={e => setContent(e.target.value)}
          rows={14}
          placeholder="Artikel-Inhalt (Markdown wird unterstützt)…"
          className="font-mono text-sm"
        />
      </div>
      <div className="grid gap-1.5">
        <Label>Tags (kommagetrennt)</Label>
        <Input value={tagsInput} onChange={e => setTagsInput(e.target.value)} placeholder="keycloak, auth, tutorial" />
      </div>
      <div className="flex items-center gap-2">
        <button type="button" onClick={() => setPinned(v => !v)} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
          {pinned ? <CheckCircle2Icon className="h-4 w-4 text-primary" /> : <CircleIcon className="h-4 w-4" />}
          Artikel anpinnen
        </button>
      </div>
      <div className="flex justify-end gap-3 pt-2 border-t">
        <Button variant="outline" onClick={onCancel}>Abbrechen</Button>
        <Button onClick={handleSave} disabled={saving || !title.trim() || !content.trim()}>
          {saving ? "Speichern…" : initial ? "Speichern" : "Artikel erstellen"}
        </Button>
      </div>
    </div>
  )
}
