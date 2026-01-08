// HR Module Types

// ============================================================================
// Enums
// ============================================================================

export type LeaveType = 'vacation' | 'sick' | 'personal' | 'unpaid' | 'parental' | 'bereavement' | 'other';
export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'intern' | 'freelance';

// ============================================================================
// Employee
// ============================================================================

export interface Employee {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  department?: string;
  position?: string;
  employment_type: EmploymentType;
  hire_date: string;
  termination_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  department?: string;
  position?: string;
  employment_type: EmploymentType;
  hire_date: string;
}

export interface EmployeeUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  department?: string;
  position?: string;
  employment_type?: EmploymentType;
  hire_date?: string;
  termination_date?: string;
  is_active?: boolean;
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
