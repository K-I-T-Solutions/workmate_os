import { use } from "react"
import { ContractDetailView } from "@/components/contracts/contract-detail"

export default function ContractDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <ContractDetailView id={id} />
}
