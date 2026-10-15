"use client"

import { createContext, useContext, useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { clearPortalSession, getPortalToken } from "@/lib/portal/client"
import { portalService, type PortalMe } from "@/lib/portal/service"
import { LogOutIcon } from "lucide-react"

const PortalMeContext = createContext<PortalMe | null>(null)
export const usePortalMe = () => useContext(PortalMeContext)

export function PortalBrand({ subtitle }: { subtitle?: string }) {
  return (
    <div className="flex items-center gap-3">
      <img src="/workmate-logo.png" alt="" className="h-8 w-8 object-contain" />
      <div className="leading-tight">
        <p className="font-heading text-sm font-semibold text-foreground">Kundenportal</p>
        {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
      </div>
    </div>
  )
}

/** Rahmen für eingeloggte Portal-Seiten – leitet ohne gültige Session zum Login. */
export function PortalShell({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [me, setMe] = useState<PortalMe | null>(null)

  useEffect(() => {
    if (!getPortalToken()) {
      router.replace("/portal")
      return
    }
    portalService.me().then(setMe).catch(() => {})
  }, [router])

  function logout() {
    clearPortalSession()
    router.replace("/portal")
  }

  if (!me) {
    return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">Laden…</div>
  }

  return (
    <PortalMeContext.Provider value={me}>
      <div className="min-h-screen bg-background">
        <header className="border-b border-border bg-card">
          <div className="mx-auto flex h-16 max-w-4xl items-center justify-between px-4">
            <Link href="/portal/tickets"><PortalBrand subtitle={me.customer_name} /></Link>
            <div className="flex items-center gap-4">
              <span className="hidden text-sm text-muted-foreground sm:inline">{me.firstname} {me.lastname}</span>
              <button onClick={logout} className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
                <LogOutIcon className="h-4 w-4" /> Abmelden
              </button>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-4xl px-4 py-8">{children}</main>
      </div>
    </PortalMeContext.Provider>
  )
}
