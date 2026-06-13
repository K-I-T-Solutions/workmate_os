import { use } from "react"
import { InvoiceDetail } from "@/components/invoices/invoice-detail"

export default function InvoiceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <InvoiceDetail id={id} />
}
