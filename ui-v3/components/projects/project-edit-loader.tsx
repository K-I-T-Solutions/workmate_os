"use client"

import { useEffect, useState } from "react"
import { projectService } from "@/lib/projects/service"
import { ProjectForm } from "./project-form"
import type { Project } from "@/lib/projects/types"

export function ProjectEditLoader({ id }: { id: string }) {
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    projectService.get(id).then(setProject).finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">Laden…</div>
  if (!project) return <div className="flex items-center justify-center py-24 text-sm text-destructive">Projekt nicht gefunden.</div>

  return <ProjectForm initial={project} projectId={id} />
}
