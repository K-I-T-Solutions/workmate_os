import { use } from "react"
import { CustomerDetail } from "@/components/crm/customer-detail"

export default function CustomerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <CustomerDetail id={id} />
}
