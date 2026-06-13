import { use } from "react"
import { InvoiceEditLoader } from "@/components/invoices/invoice-edit-loader"

export default function EditInvoicePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <InvoiceEditLoader id={id} />
}
