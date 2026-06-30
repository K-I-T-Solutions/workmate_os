"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
const ReactMarkdown = dynamic(() => import("react-markdown"), { ssr: false })
import remarkGfm from "remark-gfm"
import { usePageTitle } from "@/lib/page-title-context"
import { knowledgeService } from "@/lib/knowledge/service"
import type { KBArticleDetail, KBCategory } from "@/lib/knowledge/types"
import { Button } from "@/components/ui/button"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { ArticleForm } from "./article-form"
import { ArrowLeftIcon, PencilIcon, Trash2Icon, ThumbsUpIcon, ThumbsDownIcon, PinIcon } from "lucide-react"

const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf", published: "Veröffentlicht", archived: "Archiviert",
}
const STATUS_COLOR: Record<string, string> = {
  draft: "bg-muted text-muted-foreground",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  archived: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE", { dateStyle: "long" })
}

export function ArticleDetail({
  article: initial,
  categories,
  onBack,
  onDeleted,
}: {
  article: KBArticleDetail
  categories: KBCategory[]
  onBack: () => void
  onDeleted: () => void
}) {
  const [article, setArticle] = useState(initial)
  const [editing, setEditing] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  usePageTitle(article.title)
  const [voted, setVoted] = useState<"helpful" | "not_helpful" | null>(null)
  const [localCounts, setLocalCounts] = useState({
    helpful: article.helpful_count,
    not_helpful: article.not_helpful_count,
  })

  async function handleVote(helpful: boolean) {
    if (voted !== null) return
    await knowledgeService.vote(article.id, helpful)
    setVoted(helpful ? "helpful" : "not_helpful")
    setLocalCounts(c => ({
      helpful: helpful ? c.helpful + 1 : c.helpful,
      not_helpful: !helpful ? c.not_helpful + 1 : c.not_helpful,
    }))
  }

  async function handleDelete() {
    await knowledgeService.deleteArticle(article.id)
    onDeleted()
  }

  if (editing) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => setEditing(false)}>
            <ArrowLeftIcon className="h-4 w-4" />
          </Button>
          <h1 className="text-xl font-semibold">Artikel bearbeiten</h1>
        </div>
        <ArticleForm
          initial={article}
          categories={categories}
          onSave={updated => { setArticle(updated); setEditing(false) }}
          onCancel={() => setEditing(false)}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-3">
        <Button variant="ghost" size="icon" className="mt-0.5 shrink-0" onClick={onBack}>
          <ArrowLeftIcon className="h-4 w-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[article.status] ?? "bg-muted"}`}>
              {STATUS_LABEL[article.status] ?? article.status}
            </span>
            {article.pinned && (
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                <PinIcon className="h-3 w-3" /> Angepinnt
              </span>
            )}
            {article.tags.length > 0 && article.tags.map(tag => (
              <span key={tag} className="rounded-full bg-muted px-2 py-0.5 text-xs">{tag}</span>
            ))}
          </div>
          <h1 className="text-2xl font-bold">{article.title}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {article.published_at ? `Veröffentlicht am ${fmtDate(article.published_at)}` : `Erstellt am ${fmtDate(article.created_at)}`}
            {" · "}{article.view_count} Aufrufe
          </p>
        </div>
        <div className="flex gap-1 shrink-0">
          <Button variant="ghost" size="icon" onClick={() => setEditing(true)}>
            <PencilIcon className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-destructive hover:bg-destructive/10" onClick={() => setShowDelete(true)}>
            <Trash2Icon className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="rounded-lg border bg-card p-6">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {article.content}
          </ReactMarkdown>
        </div>
      </div>

      {/* Feedback */}
      <div className="flex items-center gap-4 rounded-lg border bg-card p-4">
        <p className="text-sm text-muted-foreground">War dieser Artikel hilfreich?</p>
        <div className="flex gap-2">
          <button
            onClick={() => handleVote(true)}
            disabled={voted !== null}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${
              voted === "helpful"
                ? "border-green-400 bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300"
                : "hover:border-green-400 hover:text-green-700"
            } disabled:opacity-60`}
          >
            <ThumbsUpIcon className="h-4 w-4" />
            {localCounts.helpful}
          </button>
          <button
            onClick={() => handleVote(false)}
            disabled={voted !== null}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${
              voted === "not_helpful"
                ? "border-red-400 bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300"
                : "hover:border-red-400 hover:text-red-700"
            } disabled:opacity-60`}
          >
            <ThumbsDownIcon className="h-4 w-4" />
            {localCounts.not_helpful}
          </button>
        </div>
        {voted && (
          <p className="text-sm text-muted-foreground">Danke für dein Feedback!</p>
        )}
      </div>

      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Artikel löschen?</AlertDialogTitle>
            <AlertDialogDescription>„{article.title}" wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Löschen</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
