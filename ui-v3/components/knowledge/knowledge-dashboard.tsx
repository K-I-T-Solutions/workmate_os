"use client"

import { useEffect, useState } from "react"
import { knowledgeService } from "@/lib/knowledge/service"
import type { KBArticle, KBArticleDetail, KBCategory } from "@/lib/knowledge/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ArticleDetail } from "./article-detail"
import { ArticleForm } from "./article-form"
import { PlusIcon, PinIcon, EyeIcon, ThumbsUpIcon, SearchIcon } from "lucide-react"
import { useAuth } from "@/components/providers/auth-provider"

const STATUS_COLOR: Record<string, string> = {
  draft: "bg-muted text-muted-foreground",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  archived: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
}
const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf", published: "Veröffentlicht", archived: "Archiviert",
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("de-DE")
}

function ArticleCard({ article, onClick }: { article: KBArticle; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="group w-full text-left rounded-lg border bg-card p-4 hover:border-primary/50 hover:bg-muted/30 transition-colors"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[article.status] ?? "bg-muted"}`}>
            {STATUS_LABEL[article.status] ?? article.status}
          </span>
          {article.pinned && <PinIcon className="h-3.5 w-3.5 text-muted-foreground" />}
        </div>
        <span className="text-xs text-muted-foreground shrink-0">{fmtDate(article.updated_at)}</span>
      </div>
      <h3 className="font-semibold group-hover:text-primary transition-colors line-clamp-2">{article.title}</h3>
      {article.excerpt && (
        <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{article.excerpt}</p>
      )}
      {article.tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {article.tags.slice(0, 4).map(tag => (
            <span key={tag} className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">{tag}</span>
          ))}
        </div>
      )}
      <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1"><EyeIcon className="h-3.5 w-3.5" />{article.view_count}</span>
        <span className="flex items-center gap-1"><ThumbsUpIcon className="h-3.5 w-3.5" />{article.helpful_count}</span>
      </div>
    </button>
  )
}

export function KnowledgeDashboard() {
  const { hasPermission } = useAuth()
  const [categories, setCategories] = useState<KBCategory[]>([])
  const [articles, setArticles] = useState<KBArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [activeCat, setActiveCat] = useState<string | null>(null)
  const [activeStatus, setActiveStatus] = useState<string>("published")
  const [openArticle, setOpenArticle] = useState<KBArticleDetail | null>(null)
  const [loadingArticle, setLoadingArticle] = useState(false)
  const [showNewForm, setShowNewForm] = useState(false)
  const [deleteCatId, setDeleteCatId] = useState<string | null>(null)

  async function loadAll() {
    setLoading(true)
    try {
      const [cats, arts] = await Promise.all([
        knowledgeService.listCategories(),
        knowledgeService.listArticles({ status: activeStatus as "published", limit: 100 }),
      ])
      setCategories(cats)
      setArticles(arts)
    } finally {
      setLoading(false)
    }
  }

  async function loadArticles() {
    setLoading(true)
    try {
      const params: Record<string, string> = { limit: "100" }
      if (activeStatus !== "all") params.status = activeStatus
      if (activeCat) params.category_id = activeCat
      if (search.trim()) params.search = search.trim()
      const arts = await knowledgeService.listArticles(params as Parameters<typeof knowledgeService.listArticles>[0])
      setArticles(arts)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadAll() }, [])
  useEffect(() => { loadArticles() }, [search, activeCat, activeStatus])

  async function openDetail(article: KBArticle) {
    setLoadingArticle(true)
    try {
      const detail = await knowledgeService.getArticle(article.id)
      setOpenArticle(detail)
    } finally {
      setLoadingArticle(false)
    }
  }

  async function handleDeleteCat() {
    if (!deleteCatId) return
    await knowledgeService.deleteCategory(deleteCatId)
    setDeleteCatId(null)
    loadAll()
  }

  if (openArticle) {
    return (
      <div className="px-8 py-6">
        <ArticleDetail
          article={openArticle}
          categories={categories}
          onBack={() => setOpenArticle(null)}
          onDeleted={() => { setOpenArticle(null); loadArticles() }}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Wissensdatenbank</h1>
        {hasPermission("kb.write") && (
          <Button size="sm" onClick={() => setShowNewForm(true)}>
            <PlusIcon className="mr-2 h-4 w-4" />
            Artikel erstellen
          </Button>
        )}
      </div>

      {/* Search */}
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
        <Input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Artikel durchsuchen…"
          className="pl-9"
        />
      </div>

      {/* Category + Status filter */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setActiveCat(null)}
          className={`rounded-full border px-3 py-1 text-sm transition-colors ${activeCat === null ? "bg-primary text-primary-foreground border-primary" : "border-border text-muted-foreground hover:text-foreground"}`}
        >
          Alle
        </button>
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setActiveCat(cat.id === activeCat ? null : cat.id)}
            className={`rounded-full border px-3 py-1 text-sm transition-colors ${activeCat === cat.id ? "bg-primary text-primary-foreground border-primary" : "border-border text-muted-foreground hover:text-foreground"}`}
          >
            {cat.name}
            {cat.article_count > 0 && (
              <span className="ml-1.5 text-xs opacity-70">{cat.article_count}</span>
            )}
          </button>
        ))}
        <div className="ml-auto flex gap-1">
          {["all", "published", "draft", "archived"].map(s => (
            <button
              key={s}
              onClick={() => setActiveStatus(s)}
              className={`rounded-lg border px-2 py-1 text-xs transition-colors ${activeStatus === s ? "bg-muted font-medium" : "text-muted-foreground hover:text-foreground"}`}
            >
              {s === "all" ? "Alle" : STATUS_LABEL[s]}
            </button>
          ))}
        </div>
      </div>

      {/* Articles */}
      {loading || loadingArticle ? (
        <div className="py-16 text-center text-sm text-muted-foreground">Laden…</div>
      ) : articles.length === 0 ? (
        <div className="rounded-lg border border-dashed p-16 text-center text-sm text-muted-foreground">
          Keine Artikel gefunden.
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {articles
            .sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0))
            .map(article => (
              <ArticleCard key={article.id} article={article} onClick={() => openDetail(article)} />
            ))}
        </div>
      )}

      {/* New Article Dialog */}
      <Dialog open={showNewForm} onOpenChange={open => !open && setShowNewForm(false)}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Neuer Artikel</DialogTitle>
          </DialogHeader>
          <ArticleForm
            categories={categories}
            onSave={article => {
              setShowNewForm(false)
              loadArticles()
              setOpenArticle(article)
            }}
            onCancel={() => setShowNewForm(false)}
          />
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteCatId} onOpenChange={open => !open && setDeleteCatId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Kategorie löschen?</AlertDialogTitle>
            <AlertDialogDescription>Die Kategorie wird unwiderruflich gelöscht.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteCat} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Löschen</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
