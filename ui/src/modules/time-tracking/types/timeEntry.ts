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
