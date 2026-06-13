"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { crmService } from "@/lib/crm/service"
import type { ContactWithCustomer } from "@/lib/crm/types"
import { Input } from "@/components/ui/input"
import { MailIcon, PhoneIcon, StarIcon, ExternalLinkIcon } from "lucide-react"

function initials(c: ContactWithCustomer) {
  return `${c.firstname[0] ?? ""}${c.lastname[0] ?? ""}`.toUpperCase()
}

export function ContactsList() {
  const router = useRouter()
  const [contacts, setContacts] = useState<ContactWithCustomer[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await crmService.getAllContacts({
        search: search.trim() || undefined,
        limit: 200,
      })
      setContacts(data)
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => {
    const t = setTimeout(load, 300)
    return () => clearTimeout(t)
  }, [load])

  return (
    <div className="space-y-6 px-8 py-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Kontakte</h1>
          {!loading && <p className="text-sm text-muted-foreground mt-0.5">{contacts.length} Kontakte</p>}
        </div>
      </div>

      <Input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="Name oder E-Mail suchen…"
        className="max-w-sm"
      />

      {loading ? (
        <div className="py-12 text-center text-sm text-muted-foreground">Laden…</div>
      ) : contacts.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Keine Kontakte gefunden.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Name</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Position</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Kontakt</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Kunde</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground w-8" />
              </tr>
            </thead>
            <tbody>
              {contacts.map(c => (
                <tr key={c.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium shrink-0">
                        {initials(c)}
                      </div>
                      <div>
                        <p className="font-medium">
                          {c.firstname} {c.lastname}
                          {c.is_primary && (
                            <StarIcon className="inline ml-1 h-3 w-3 text-amber-500 fill-amber-500" />
                          )}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {[c.position, c.department].filter(Boolean).join(" · ") || "–"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="space-y-0.5">
                      {c.email && (
                        <a
                          href={`mailto:${c.email}`}
                          onClick={e => e.stopPropagation()}
                          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
                        >
                          <MailIcon className="h-3 w-3 shrink-0" />
                          {c.email}
                        </a>
                      )}
                      {(c.phone || c.mobile) && (
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <PhoneIcon className="h-3 w-3 shrink-0" />
                          {c.phone ?? c.mobile}
                        </div>
                      )}
                      {!c.email && !c.phone && !c.mobile && <span className="text-xs text-muted-foreground">–</span>}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {c.customer_name ? (
                      <button
                        onClick={() => router.push(`/crm/customers/${c.customer_id}`)}
                        className="group flex items-center gap-1 text-sm text-primary hover:underline"
                      >
                        {c.customer_name}
                        <ExternalLinkIcon className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ) : (
                      <span className="text-sm text-muted-foreground">–</span>
                    )}
                  </td>
                  <td className="px-4 py-3" />
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
