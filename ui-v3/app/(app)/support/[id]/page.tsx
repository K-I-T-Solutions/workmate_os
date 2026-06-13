import { use } from "react"
import { TicketDetailView } from "@/components/support/ticket-detail"

export default function TicketDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <TicketDetailView id={id} />
}
