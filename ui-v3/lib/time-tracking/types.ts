export interface TimeEntry {
  id: string
  employee_id: string
  project_id: string | null
  start_time: string
  end_time: string | null
  duration_minutes: number | null
  note: string | null
  task_type: string | null
  billable: boolean
  hourly_rate: string | null
  is_approved: boolean
  is_invoiced: boolean
  created_at: string
  updated_at: string
}

export interface TimeEntryCreate {
  employee_id: string
  project_id?: string | null
  start_time: string
  end_time?: string | null
  note?: string | null
  task_type?: string | null
  billable: boolean
  hourly_rate?: number | string | null
}

export interface TimeEntryUpdate {
  end_time?: string | null
  note?: string | null
  task_type?: string | null
  billable?: boolean | null
  hourly_rate?: number | string | null
}

export interface TimeTrackingStats {
  total_hours_today: number
  total_hours_week: number
  total_hours_month: number
  total_entries: number
  billable_hours: number
  non_billable_hours: number
  hours_by_project: { project_id: string; project_title: string; hours: number }[]
  hours_by_task_type: { task_type: string; hours: number }[]
}

export interface TimeListParams {
  skip?: number
  limit?: number
  employee_id?: string
  project_id?: string
  start_date?: string
  end_date?: string
  task_type?: string
  billable?: boolean
  is_approved?: boolean
  is_invoiced?: boolean
  search?: string
}
