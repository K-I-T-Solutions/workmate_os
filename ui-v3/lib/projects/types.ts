export type ProjectStatus = "planning" | "active" | "on_hold" | "completed" | "cancelled"

export interface Project {
  id: string
  title: string
  description: string | null
  status: ProjectStatus | string
  start_date: string | null
  end_date: string | null
  customer_id: string | null
  department_id: string | null
  created_at: string
  updated_at: string
}

export interface CreateProjectPayload {
  title: string
  description?: string | null
  status?: string
  start_date?: string | null
  end_date?: string | null
  customer_id?: string | null
  department_id?: string | null
}

export interface UpdateProjectPayload {
  title?: string
  description?: string | null
  status?: string
  start_date?: string | null
  end_date?: string | null
  department_id?: string | null
}
