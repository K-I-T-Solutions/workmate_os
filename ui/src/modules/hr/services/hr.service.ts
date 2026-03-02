import { apiClient } from '@/services/api/client';
import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  EmployeeListResponse,
  EmployeeFilters,
  Department,
  Role,
  LeaveRequest,
  LeaveRequestCreate,
  LeaveRequestUpdate,
  LeaveRequestListResponse,
  LeaveRequestFilters,
  LeaveRequestApprove,
  LeaveRequestReject,
  LeaveBalance,
  LeaveBalanceCreate,
  LeaveBalanceUpdate,
  LeaveBalanceListResponse,
  LeaveBalanceFilters,
  LeaveStatistics,
  EmployeeStatistics,
} from '../types';

// ============================================================================
// Employees (using Core Employee API)
// ============================================================================

/**
 * Get list of employees
 */
export async function getEmployees(
  filters?: EmployeeFilters
): Promise<EmployeeListResponse> {
  const params: Record<string, any> = {
    skip: filters?.skip || 0,
    limit: Math.min(filters?.limit || 50, 500), // Backend max is 500
  };

  if (filters?.department) params.department_id = filters.department;
  if (filters?.is_active !== undefined) params.status = filters.is_active ? 'active' : 'inactive';
  if (filters?.search) params.search = filters.search;

  const response = await apiClient.get('/api/employees', { params });

  // Transform response to match our interface
  let items = response.data.employees || [];

  // Client-side filter for employment_type since API doesn't support it
  if (filters?.employment_type) {
    items = items.filter((emp: any) => emp.employment_type === filters.employment_type);
  }

  return {
    items,
    total: response.data.total || 0,
    skip: filters?.skip || 0,
    limit: Math.min(filters?.limit || 50, 500),
  };
}

/**
 * Get single employee by ID
 */
export async function getEmployee(id: string): Promise<Employee> {
  const response = await apiClient.get(`/api/employees/${id}`);
  return response.data;
}

/**
 * Create new employee
 */
export async function createEmployee(data: EmployeeCreate): Promise<Employee> {
  const response = await apiClient.post('/api/employees', data);
  return response.data;
}

/**
 * Update employee
 */
export async function updateEmployee(
  id: string,
  data: EmployeeUpdate
): Promise<Employee> {
  const response = await apiClient.put(`/api/employees/${id}`, data);
  return response.data;
}

/**
 * Delete employee (soft delete)
 */
export async function deleteEmployee(id: string): Promise<void> {
  await apiClient.delete(`/api/employees/${id}`);
}

/**
 * Get employee statistics
 */
export async function getEmployeeStatistics(): Promise<EmployeeStatistics> {
  const response = await apiClient.get('/api/employees/statistics');
  return response.data;
}

// ============================================================================
// Departments
// ============================================================================

/**
 * Get list of departments
 */
export async function getDepartments(): Promise<Department[]> {
  const response = await apiClient.get('/api/departments');
  return response.data;
}

/**
 * Get single department by ID
 */
export async function getDepartment(id: string): Promise<Department> {
  const response = await apiClient.get(`/api/departments/${id}`);
  return response.data;
}

// ============================================================================
// Roles
// ============================================================================

/**
 * Get list of roles
 */
export async function getRoles(): Promise<Role[]> {
  const response = await apiClient.get('/api/roles');
  return response.data;
}

/**
 * Get single role by ID
 */
export async function getRole(id: string): Promise<Role> {
  const response = await apiClient.get(`/api/roles/${id}`);
  return response.data;
}

// ============================================================================
// Leave Requests
// ============================================================================

/**
 * Get list of leave requests
 */
export async function getLeaveRequests(
  filters?: LeaveRequestFilters
): Promise<LeaveRequestListResponse> {
  const params: Record<string, any> = {
    skip: filters?.skip || 0,
    limit: Math.min(filters?.limit || 50, 500), // Backend max is 500
  };

  if (filters?.employee_id) params.employee_id = filters.employee_id;
  if (filters?.leave_type) params.leave_type = filters.leave_type;
  if (filters?.status) params.status = filters.status;
  if (filters?.from_date) params.date_from = filters.from_date; // Backend expects date_from
  if (filters?.to_date) params.date_to = filters.to_date; // Backend expects date_to

  const response = await apiClient.get('/api/hr/leave/requests', { params });
  return response.data;
}

/**
 * Get single leave request by ID
 */
export async function getLeaveRequest(id: string): Promise<LeaveRequest> {
  const response = await apiClient.get(`/api/hr/leave/requests/${id}`);
  return response.data;
}

/**
 * Create new leave request
 */
export async function createLeaveRequest(
  data: LeaveRequestCreate
): Promise<LeaveRequest> {
  const response = await apiClient.post('/api/hr/leave/requests', data);
  return response.data;
}

/**
 * Update leave request
 */
export async function updateLeaveRequest(
  id: string,
  data: LeaveRequestUpdate
): Promise<LeaveRequest> {
  const response = await apiClient.put(`/api/hr/leave/requests/${id}`, data);
  return response.data;
}

/**
 * Approve leave request
 */
export async function approveLeaveRequest(
  id: string,
  data: LeaveRequestApprove
): Promise<LeaveRequest> {
  const response = await apiClient.post(`/api/hr/leave/requests/${id}/approve`, data);
  return response.data;
}

/**
 * Reject leave request
 */
export async function rejectLeaveRequest(
  id: string,
  data: LeaveRequestReject
): Promise<LeaveRequest> {
  const response = await apiClient.post(`/api/hr/leave/requests/${id}/reject`, data);
  return response.data;
}

/**
 * Cancel leave request
 */
export async function cancelLeaveRequest(id: string): Promise<LeaveRequest> {
  const response = await apiClient.post(`/api/hr/leave/requests/${id}/cancel`);
  return response.data;
}

/**
 * Delete leave request
 */
export async function deleteLeaveRequest(id: string): Promise<void> {
  await apiClient.delete(`/api/hr/leave/requests/${id}`);
}

/**
 * Get leave request statistics
 */
export async function getLeaveStatistics(
  filters?: LeaveRequestFilters
): Promise<LeaveStatistics> {
  const response = await apiClient.get('/api/hr/leave/statistics');
  return response.data;
}

// ============================================================================
// Leave Balances
// ============================================================================

/**
 * Get list of leave balances
 */
export async function getLeaveBalances(
  filters?: LeaveBalanceFilters
): Promise<LeaveBalanceListResponse> {
  const params: Record<string, any> = {};

  if (filters?.employee_id) params.employee_id = filters.employee_id;
  if (filters?.year) params.year = filters.year;
  if (filters?.leave_type) params.leave_type = filters.leave_type;

  const response = await apiClient.get('/api/hr/leave/balances', { params });
  return response.data;
}

/**
 * Get single leave balance by ID
 */
export async function getLeaveBalance(id: string): Promise<LeaveBalance> {
  const response = await apiClient.get(`/api/hr/leave/balances/${id}`);
  return response.data;
}

/**
 * Create new leave balance
 */
export async function createLeaveBalance(
  data: LeaveBalanceCreate
): Promise<LeaveBalance> {
  const response = await apiClient.post('/api/hr/leave/balances', data);
  return response.data;
}

/**
 * Update leave balance
 */
export async function updateLeaveBalance(
  id: string,
  data: LeaveBalanceUpdate
): Promise<LeaveBalance> {
  const response = await apiClient.put(`/api/hr/leave/balances/${id}`, data);
  return response.data;
}

/**
 * Delete leave balance
 */
export async function deleteLeaveBalance(id: string): Promise<void> {
  await apiClient.delete(`/api/hr/leave/balances/${id}`);
}
