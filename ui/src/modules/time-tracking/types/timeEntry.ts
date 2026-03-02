export type TaskType = 'development' | 'meeting' | 'support' | 'documentation' | 'testing' | 'planning' | 'other';

export interface TimeEntry {
  id: string;
  employee_id: string;
  project_id: string | null;

  // Time
  start_time: string;
  end_time: string | null;
  duration_minutes: number | null;

  // Details
  note: string | null;
  task_type: TaskType | null;

  // Billing
  billable: boolean;
  hourly_rate: number | null;

  // Status
  is_approved: boolean;
  is_invoiced: boolean;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface TimeEntryCreateRequest {
  employee_id: string;
  project_id?: string | null;
  start_time: string;
  end_time?: string | null;
  note?: string | null;
  task_type?: TaskType | null;
  billable?: boolean;
  hourly_rate?: number | null;
}

export interface TimeEntryUpdateRequest {
  end_time?: string | null;
  note?: string | null;
  task_type?: TaskType | null;
  billable?: boolean;
  hourly_rate?: number | null;
}

// Running timer state
export interface RunningTimer {
  id: string;
  project_id: string | null;
  start_time: string;
  elapsed_seconds: number;
}

// Query parameters for server-side filtering
export interface TimeEntryFilters {
  skip?: number;
  limit?: number;
  employee_id?: string;
  project_id?: string;
  start_date?: string;
  end_date?: string;
  task_type?: TaskType;
  billable?: boolean;
  is_approved?: boolean;
  is_invoiced?: boolean;
  search?: string;
}

// Stats response
export interface TimeTrackingStats {
  total_hours_today: number;
  total_hours_week: number;
  total_hours_month: number;
  total_entries: number;
  billable_hours: number;
  non_billable_hours: number;
  hours_by_project: { project_id: string; hours: number }[];
  hours_by_task_type: { task_type: string; hours: number }[];
}

// Weekly summary
export interface DaySummary {
  date: string;
  hours: number;
  entries_count: number;
}

export interface WeeklySummary {
  employee_id: string;
  week: string;
  total_hours: number;
  daily_breakdown: DaySummary[];
}
