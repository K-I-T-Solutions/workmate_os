// HR Module Types

// ============================================================================
// Enums
// ============================================================================

export type LeaveType = 'vacation' | 'sick' | 'personal' | 'unpaid' | 'parental' | 'bereavement' | 'other';
export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'intern' | 'freelance';

// ============================================================================
// Employee (matches Core API schema)
// ============================================================================

export interface Employee {
  id: string;
  employee_code: string;
  uuid_keycloak?: string;
  first_name?: string;
  last_name?: string;
  email: string;
  phone?: string;
  gender?: string;
  birth_date?: string;
  nationality?: string;
  photo_url?: string;
  bio?: string;

  // Address
  address_street?: string;
  address_zip?: string;
  address_city?: string;
  address_country?: string;

  // Organization
  department?: string;  // Will be department name from joined data
  department_id?: string;
  role_id?: string;
  reports_to?: string;

  // Employment
  employment_type?: EmploymentType;
  hire_date?: string;
  termination_date?: string;
  status?: string;  // 'active' | 'inactive' | 'on_leave'

  // Preferences
  timezone?: string;
  language?: string;
  theme?: string;
  notifications_enabled?: boolean;
  matrix_username?: string;

  // Timestamps
  created_at?: string;
  updated_at?: string;
  last_login?: string;

  // Helper for UI
  is_active?: boolean;  // Computed from status
}

export interface EmployeeCreate {
  employee_code: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  gender?: string;
  birth_date?: string;
  nationality?: string;

  // Address
  address_street?: string;
  address_zip?: string;
  address_city?: string;
  address_country?: string;

  // Organization
  department_id?: string;
  role_id?: string;
  reports_to?: string;

  // Employment
  employment_type?: EmploymentType;
  hire_date?: string;
  status?: string;

  // Preferences
  timezone?: string;
  language?: string;
  theme?: string;
  notifications_enabled?: boolean;
}

export interface EmployeeUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  gender?: string;
  birth_date?: string;
  nationality?: string;
  photo_url?: string;
  bio?: string;

  // Address
  address_street?: string;
  address_zip?: string;
  address_city?: string;
  address_country?: string;

  // Organization
  department_id?: string;
  role_id?: string;
  reports_to?: string;

  // Employment
  employment_type?: string;
  hire_date?: string;
  termination_date?: string;
  status?: string;

  // Preferences
  timezone?: string;
  language?: string;
  theme?: string;
  notifications_enabled?: boolean;
  matrix_username?: string;
}

// ============================================================================
// Leave Request
// ============================================================================

export interface LeaveRequest {
  id: string;
  employee_id: string;
  employee?: Employee;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  total_days: number;
  reason?: string;
  status: LeaveStatus;
  approver_id?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequestCreate {
  employee_id: string;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  reason?: string;
}

export interface LeaveRequestUpdate {
  leave_type?: LeaveType;
  start_date?: string;
  end_date?: string;
  reason?: string;
  status?: LeaveStatus;
  rejection_reason?: string;
}

export interface LeaveRequestApprove {
  approver_id: string;
}

export interface LeaveRequestReject {
  approver_id: string;
  rejection_reason: string;
}

// ============================================================================
// Leave Balance
// ============================================================================

export interface LeaveBalance {
  id: string;
  employee_id: string;
  employee?: Employee;
  year: number;
  leave_type: LeaveType;
  total_days: number;
  used_days: number;
  available_days: number;
  created_at: string;
  updated_at: string;
}

export interface LeaveBalanceCreate {
  employee_id: string;
  year: number;
  leave_type: LeaveType;
  total_days: number;
}

export interface LeaveBalanceUpdate {
  total_days?: number;
  used_days?: number;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface EmployeeListResponse {
  items: Employee[];
  total: number;
  skip: number;
  limit: number;
}

export interface LeaveRequestListResponse {
  items: LeaveRequest[];
  total: number;
  skip: number;
  limit: number;
}

export interface LeaveBalanceListResponse {
  items: LeaveBalance[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// Filters
// ============================================================================

export interface EmployeeFilters {
  department?: string;
  employment_type?: EmploymentType;
  is_active?: boolean;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface LeaveRequestFilters {
  employee_id?: string;
  leave_type?: LeaveType;
  status?: LeaveStatus;
  from_date?: string;
  to_date?: string;
  skip?: number;
  limit?: number;
}

export interface LeaveBalanceFilters {
  employee_id?: string;
  year?: number;
  leave_type?: LeaveType;
}

// ============================================================================
// Statistics & Analytics
// ============================================================================

export interface LeaveStatistics {
  total_requests: number;
  pending_requests: number;
  approved_requests: number;
  rejected_requests: number;
  by_type: Record<LeaveType, number>;
  by_status: Record<LeaveStatus, number>;
}

export interface EmployeeStatistics {
  total_employees: number;
  active_employees: number;
  by_department: Record<string, number>;
  by_employment_type: Record<EmploymentType, number>;
}
