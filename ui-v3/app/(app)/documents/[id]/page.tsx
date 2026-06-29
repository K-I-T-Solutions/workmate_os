import { DocumentDetail } from "@/components/documents/document-detail"
import { use } from "react"

export default function DocumentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <DocumentDetail id={id} />
}
