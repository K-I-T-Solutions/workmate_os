export type EmployeeStatus = "active" | "inactive" | "on_leave" | "terminated"
export type EmploymentType = "fulltime" | "parttime" | "freelancer" | "intern" | "minijob"
export type Gender = "male" | "female" | "other" | "prefer_not_to_say"
export type LeaveType = "vacation" | "sick" | "parental" | "other"
export type LeaveStatus = "pending" | "approved" | "rejected" | "cancelled"
export type ApplicationStatus = "new" | "screening" | "interview" | "offer" | "hired" | "rejected"
export type JobStatus = "draft" | "open" | "closed" | "archived"

export interface Department {
  id: string
  name: string
  code: string
  description: string | null
  manager_id: string | null
  created_at: string
}

export interface Role {
  id: string
  name: string
  description: string | null
}

export interface Employee {
  id: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  gender: Gender | null
  birth_date: string | null
  employment_type: EmploymentType | null
  hire_date: string | null
  termination_date: string | null
  status: EmployeeStatus | null
  employee_code: string | null
  workmate_id: string | null
  photo_url: string | null
  bio: string | null
  department_id: string | null
  role_id: string | null
  department: Department | null
  role: Role | null
  created_at: string
  updated_at: string
}

export interface EmployeeListResponse {
  employees: Employee[]
  total: number
  page: number
  page_size: number
}

export interface EmployeeStatistics {
  total_employees: number
  active_employees: number
  by_department: Record<string, number>
  by_employment_type: Record<string, number>
}

export interface EmployeeCreate {
  first_name: string
  last_name: string
  email: string
  phone?: string | null
  gender?: Gender | null
  birth_date?: string | null
  employment_type?: EmploymentType | null
  hire_date?: string | null
  status?: EmployeeStatus
  department_id?: string | null
  role_id?: string | null
  employee_code?: string | null
  workmate_id?: string | null
}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {
  bio?: string | null
  photo_url?: string | null
  termination_date?: string | null
}

export interface LeaveRequest {
  id: string
  employee_id: string
  leave_type: LeaveType
  start_date: string
  end_date: string
  total_days: number
  status: LeaveStatus
  reason: string | null
  notes: string | null
  approved_by_id: string | null
  approved_date: string | null
  rejection_reason: string | null
  created_at: string
  updated_at: string
}

export interface LeaveRequestCreate {
  employee_id: string
  leave_type: LeaveType
  start_date: string
  end_date: string
  total_days: number
  reason?: string | null
  notes?: string | null
}

export interface LeaveStatistics {
  total_requests: number
  pending_requests: number
  approved_requests: number
  rejected_requests: number
  by_type: Record<string, number>
  by_status: Record<string, number>
}

export interface JobPosting {
  id: string
  title: string
  description: string | null
  requirements: string | null
  location: string | null
  remote: boolean
  employment_type: string | null
  salary_min: number | null
  salary_max: number | null
  department_id: string | null
  status: JobStatus
  deadline: string | null
  published_at: string | null
  application_count: number
  created_at: string
  updated_at: string
}

export interface JobPostingCreate {
  title: string
  description?: string | null
  requirements?: string | null
  location?: string | null
  remote?: boolean
  employment_type?: string | null
  salary_min?: number | null
  salary_max?: number | null
  department_id?: string | null
  status?: JobStatus
  deadline?: string | null
}

export interface Application {
  id: string
  job_posting_id: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  cover_letter: string | null
  cv_url: string | null
  linkedin_url: string | null
  status: ApplicationStatus
  notes: string | null
  interview_date: string | null
  rating: number | null
  created_at: string
  updated_at: string
}
