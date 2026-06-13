"use client"

import { useEffect, useState } from "react"
import { crmService } from "@/lib/crm/service"
import { CustomerForm } from "@/components/crm/customer-form"
import type { Customer } from "@/lib/crm/types"

export function CustomerEditLoader({ id }: { id: string }) {
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    crmService.getCustomer(id).then(setCustomer).finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
  }
  if (!customer) {
    return <div className="flex items-center justify-center py-24 text-sm text-destructive">Kunde nicht gefunden.</div>
  }

  return <CustomerForm initial={customer} customerId={id} />
}
