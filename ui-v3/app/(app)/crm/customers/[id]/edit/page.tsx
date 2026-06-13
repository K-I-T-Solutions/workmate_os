import { use } from "react"
import { CustomerEditLoader } from "@/components/crm/customer-edit-loader"

export default function EditCustomerPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <CustomerEditLoader id={id} />
}
