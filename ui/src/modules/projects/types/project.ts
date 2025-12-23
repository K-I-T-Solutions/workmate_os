export type ProjectStatus = 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
export type ProjectPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Project {
  id: string;
  title: string;
  description: string | null;
  project_number: string | null;
  status: ProjectStatus;
  priority: ProjectPriority | null;

  // Dates
  start_date: string | null;
  end_date: string | null;
  deadline: string | null;

  // Financial
  budget: number | null;
  hourly_rate: number | null;

  // Relations
  customer_id: string;
  department_id: string | null;
  project_manager_id: string | null;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateRequest {
  title: string;
  description?: string | null;
  status?: ProjectStatus;
  priority?: ProjectPriority | null;
  start_date?: string | null;
  end_date?: string | null;
  deadline?: string | null;
  budget?: number | null;
  hourly_rate?: number | null;
  customer_id: string;
  department_id?: string | null;
  project_manager_id?: string | null;
}

export interface ProjectUpdateRequest {
  title?: string;
  description?: string | null;
  status?: ProjectStatus;
  priority?: ProjectPriority | null;
  start_date?: string | null;
  end_date?: string | null;
  deadline?: string | null;
  budget?: number | null;
  hourly_rate?: number | null;
  department_id?: string | null;
  project_manager_id?: string | null;
}
