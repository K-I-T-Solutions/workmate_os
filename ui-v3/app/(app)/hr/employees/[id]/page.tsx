import { use } from "react"
import { EmployeeDetail } from "@/components/hr/employee-detail"

export default function EmployeeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <EmployeeDetail id={id} />
}
