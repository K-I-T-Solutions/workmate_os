"use client"

import { usePathname, useRouter } from "next/navigation"
import { Search, ChevronRight, LogOut, Settings } from "lucide-react"
import { useAuth } from "@/components/providers/auth-provider"
import { useState, useRef, useEffect, useCallback } from "react"
import { sha256hex } from "@/lib/auth/pkce"
import { CommandPalette } from "@/components/command-palette"
import { NotificationsPanel } from "@/components/notifications-panel"

const labels: Record<string, string> = {
  dashboard: "Dashboard",
  documents: "Dokumente",
  products: "Produkte",
  reminders: "Erinnerungen",
  crm: "CRM",
  customers: "Kunden",
  pipeline: "Pipeline",
  contacts: "Kontakte",
  projects: "Projekte",
  invoices: "Rechnungen",
  finance: "Finanzen",
  time: "Zeiterfassung",
  hr: "Personal",
  employees: "Mitarbeiter",
  "my-leave": "Meine Abwesenheiten",
  support: "Support",
  knowledge: "Wissensdatenbank",
  admin: "Administration",
  settings: "Einstellungen",
  edit: "Bearbeiten",
  new: "Neu",
}

function gravatarUrl(email: string): string {
  const hash = sha256hex(email.trim().toLowerCase())
  return `https://gravatar.com/avatar/${hash}?s=64&d=404`
}

export function Topbar({ pageTitle }: { pageTitle?: string }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, loading, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null)
  const [avatarError, setAvatarError] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  const openSearch = useCallback(() => setSearchOpen(true), [])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        openSearch()
      }
    }
    document.addEventListener("keydown", onKey)
    return () => document.removeEventListener("keydown", onKey)
  }, [openSearch])

  useEffect(() => {
    if (!user?.email) return
    setAvatarError(false)
    setAvatarUrl(gravatarUrl(user.email))
  }, [user?.email])

  const segments = pathname.split("/").filter(Boolean)
  const crumbs = segments.map((s) => labels[s] ?? s)

  const showImage = avatarUrl && !avatarError

  return (
    <header className="flex h-[70px] shrink-0 items-center gap-4 border-b border-border bg-sidebar px-6">
      {/* Breadcrumb */}
      <nav className="flex min-w-0 flex-1 items-center gap-1 text-sm">
        <span className="text-muted-foreground">WORKMATE | OS</span>
        {crumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-1">
            <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground/50" />
            <span className={i === crumbs.length - 1 ? "font-medium text-foreground" : "text-muted-foreground"}>
              {pageTitle && i === crumbs.length - 1 ? pageTitle : crumb}
            </span>
          </span>
        ))}
      </nav>

      {/* Search */}
      <button
        type="button"
        onClick={openSearch}
        className="hidden items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:border-border/80 hover:text-foreground md:flex"
      >
        <Search className="h-3.5 w-3.5" />
        <span>Suche</span>
        <kbd className="rounded border border-border bg-background px-1.5 py-0.5 text-[10px]">⌘K</kbd>
      </button>

      {/* Notifications */}
      <NotificationsPanel />

      {/* Command Palette */}
      <CommandPalette open={searchOpen} onClose={() => setSearchOpen(false)} />

      {/* Avatar + Dropdown */}
      <div className="relative" ref={ref}>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground transition-opacity hover:opacity-80 overflow-hidden"
          title={user?.name}
          disabled={loading}
        >
          {loading ? (
            <span className="h-full w-full rounded-full bg-primary-foreground/30 animate-pulse" />
          ) : showImage ? (
            <img
              src={avatarUrl}
              alt={user?.name ?? ""}
              className="h-full w-full rounded-full object-cover"
              onError={() => setAvatarError(true)}
            />
          ) : (
            user?.initials ?? "?"
          )}
        </button>

        {open && (
          <div className="absolute right-0 top-10 z-50 w-52 rounded-xl border border-border bg-card shadow-lg">
            <div className="flex items-center gap-3 border-b border-border px-4 py-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground overflow-hidden">
                {showImage ? (
                  <img src={avatarUrl} alt={user?.name ?? ""} className="h-full w-full object-cover" onError={() => setAvatarError(true)} />
                ) : (
                  user?.initials ?? "?"
                )}
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-foreground">{user?.name ?? "Benutzer"}</p>
                <p className="truncate text-xs text-muted-foreground">{user?.email ?? ""}</p>
              </div>
            </div>
            <div className="p-1.5">
              <button
                type="button"
                onClick={() => { setOpen(false); router.push("/settings") }}
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-foreground transition-colors hover:bg-secondary"
              >
                <Settings className="h-4 w-4" />
                Einstellungen
              </button>
              <button
                type="button"
                onClick={logout}
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-destructive transition-colors hover:bg-destructive/10"
              >
                <LogOut className="h-4 w-4" />
                Abmelden
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
