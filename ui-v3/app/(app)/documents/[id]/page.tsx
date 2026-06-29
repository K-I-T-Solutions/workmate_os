import { DocumentDetail } from "@/components/documents/document-detail"

export default function DocumentDetailPage({ params }: { params: { id: string } }) {
  return <DocumentDetail id={params.id} />
}
