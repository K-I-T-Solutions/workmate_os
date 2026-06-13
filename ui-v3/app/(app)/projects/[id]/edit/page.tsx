import { use } from "react"
import { ProjectEditLoader } from "@/components/projects/project-edit-loader"

export default function EditProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <ProjectEditLoader id={id} />
}
