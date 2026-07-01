"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/components/providers/auth-provider"
import {
  LayoutDashboard,
  Users,
  FolderKanban,
  FileText,
  Wallet,
  Clock,
  UserCog,
  LifeBuoy,
  BookOpen,
  FolderOpen,
  Settings,
  LogOut,
  ChevronLeft,
  Package,
  Bell,
} from "lucide-react"
import { cn } from "@/lib/utils"

type NavItem = {
  label: string
  icon: React.ComponentType<{ className?: string }>
  href: string
  matchKey: string
  permission?: string | string[]   // ein Treffer reicht
}

type NavGroup = {
  label?: string
  items: NavItem[]
}

const navGroups: NavGroup[] = [
  {
    items: [{ label: "Dashboard", icon: LayoutDashboard, href: "/dashboard", matchKey: "/dashboard" }],
  },
  {
    label: "Business",
    items: [
      { label: "CRM", icon: Users, href: "/crm", matchKey: "/crm", permission: "backoffice.crm.read" },
      { label: "Projekte", icon: FolderKanban, href: "/projects", matchKey: "/projects", permission: "backoffice.projects.read" },
      { label: "Rechnungen", icon: FileText, href: "/invoices", matchKey: "/invoices", permission: "backoffice.invoices.read" },
      { label: "Finanzen", icon: Wallet, href: "/finance", matchKey: "/finance", permission: "backoffice.finance.read" },
      { label: "Produkte", icon: Package, href: "/products", matchKey: "/products", permission: "backoffice.products.read" },
    ],
  },
  {
    label: "Team",
    items: [
      { label: "Zeiterfassung", icon: Clock, href: "/time", matchKey: "/time", permission: ["backoffice.time_tracking.view", "backoffice.time_tracking.write"] },
      { label: "Personal", icon: UserCog, href: "/hr", matchKey: "/hr", permission: ["hr.view", "hr.view_own", "hr.request"] },
    ],
  },
  {
    label: "Support",
    items: [
      { label: "Tickets", icon: LifeBuoy, href: "/support", matchKey: "/support", permission: "support.view" },
      { label: "Wiki", icon: BookOpen, href: "/knowledge", matchKey: "/knowledge", permission: "kb.view" },
      { label: "Dokumente", icon: FolderOpen, href: "/documents", matchKey: "/documents", permission: "documents.read" },
    ],
  },
  {
    label: "Tools",
    items: [
      { label: "Erinnerungen", icon: Bell, href: "/reminders", matchKey: "/reminders", permission: "reminders.read" },
    ],
  },
]

export function AppSidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean
  onToggle: () => void
}) {
  const pathname = usePathname()
  const { user, logout, hasPermission } = useAuth()

  function isActive(matchKey: string) {
    return pathname.startsWith(matchKey)
  }

  return (
    <aside
      className={cn(
        "relative flex h-screen shrink-0 flex-col border-r border-border bg-sidebar transition-[width] duration-200 ease-in-out",
        collapsed ? "w-[72px]" : "w-[260px]",
      )}
    >
      {/* Logo */}
      <div
        className={cn(
          "flex h-[70px] items-center border-b border-border",
          collapsed ? "justify-center px-0" : "px-5",
        )}
      >
        <div className="flex items-center gap-3">
          <div className="relative flex h-9 w-9 shrink-0 items-center justify-center">
            <div className="absolute inset-0 rounded-lg bg-primary/30 blur-md" aria-hidden />
            <img src="/workmate-logo.png" alt="WorkmateOS" className="relative h-9 w-9 object-contain" />
          </div>
          {!collapsed && (
            <div className="flex items-baseline gap-1.5 font-heading leading-none">
              <span className="text-base font-bold tracking-tight text-foreground">WORKMATE</span>
              <span className="text-base font-light text-muted-foreground">|</span>
              <span className="text-base font-light text-primary">OS</span>
            </div>
          )}
        </div>
      </div>

      {/* Collapse toggle */}
      <button
        type="button"
        onClick={onToggle}
        aria-label={collapsed ? "Sidebar erweitern" : "Sidebar einklappen"}
        className="absolute -right-3 top-[58px] z-10 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-card text-muted-foreground transition-colors hover:border-primary hover:text-foreground"
      >
        <ChevronLeft className={cn("h-3.5 w-3.5 transition-transform", collapsed && "rotate-180")} />
      </button>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {navGroups.map((group, gi) => (
          <div key={group.label ?? `group-${gi}`} className={cn(gi > 0 && "mt-5")}>
            {group.label && !collapsed && (
              <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                {group.label}
              </p>
            )}
            {group.label && collapsed && gi > 0 && <div className="mx-3 mb-3 border-t border-border" />}
            <ul className="flex flex-col gap-1">
              {group.items.filter(item => {
                if (!item.permission) return true
                const perms = Array.isArray(item.permission) ? item.permission : [item.permission]
                return perms.some(p => hasPermission(p))
              }).map((item) => {
                const Icon = item.icon
                const active = isActive(item.matchKey)
                return (
                  <li key={item.label}>
                    <Link
                      href={item.href}
                      title={collapsed ? item.label : undefined}
                      className={cn(
                        "flex items-center rounded-lg text-sm font-medium transition-colors",
                        collapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2",
                        active
                          ? "bg-primary/15 text-primary"
                          : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                      )}
                    >
                      <Icon className="h-[22px] w-[22px] shrink-0" />
                      {!collapsed && <span>{item.label}</span>}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-border px-3 py-4">
        <ul className="flex flex-col gap-1">
          {hasPermission("admin.read") && (
            <li>
              <Link
                href="/admin"
                title={collapsed ? "Administration" : undefined}
                className={cn(
                  "flex items-center rounded-lg text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground",
                  collapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2",
                )}
              >
                <Settings className="h-[22px] w-[22px] shrink-0" />
                {!collapsed && <span>Administration</span>}
              </Link>
            </li>
          )}
          <li>
            <button
              type="button"
              title={collapsed ? "Abmelden" : undefined}
              className={cn(
                "w-full flex items-center rounded-lg text-sm font-medium text-muted-foreground transition-colors hover:bg-destructive/15 hover:text-destructive",
                collapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2",
              )}
              onClick={logout}
            >
              <LogOut className="h-[22px] w-[22px] shrink-0" />
              {!collapsed && <span>Abmelden</span>}
            </button>
          </li>
        </ul>
      </div>
    </aside>
  )
}
