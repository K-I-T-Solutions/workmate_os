"use client"

import { useState } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { Topbar } from "@/components/topbar"
import { PageTitleProvider, usePageTitleValue } from "@/lib/page-title-context"

function ShellContent({ children, collapsed, onToggle }: { children: React.ReactNode; collapsed: boolean; onToggle: () => void }) {
  const pageTitle = usePageTitleValue()
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar collapsed={collapsed} onToggle={onToggle} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar pageTitle={pageTitle ?? undefined} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

export function ShellLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)
  return (
    <PageTitleProvider>
      <ShellContent collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)}>
        {children}
      </ShellContent>
    </PageTitleProvider>
  )
}
