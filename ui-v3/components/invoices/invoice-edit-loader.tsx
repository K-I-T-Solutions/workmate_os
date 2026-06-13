"use client"

import { useEffect, useState } from "react"
import { invoiceService } from "@/lib/invoices/service"
import { InvoiceForm } from "./invoice-form"
import type { Invoice } from "@/lib/invoices/types"

export function InvoiceEditLoader({ id }: { id: string }) {
  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    invoiceService.get(id).then(setInvoice).finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
  }
  if (!invoice) {
    return <div className="flex items-center justify-center py-24 text-sm text-destructive">Rechnung nicht gefunden.</div>
  }

  return <InvoiceForm initial={invoice} invoiceId={id} />
}
