/**
 * Employee Management Composable
 * Provides full CRUD operations for employees, departments, and roles
 */

import { ref } from 'vue';
import { apiClient } from '@/services/api/client';
import type { Employee } from '@/types/api';

export interface EmployeeFilters {
  skip?: number;
  limit?: number;
  search?: string;
  department_id?: string;
  role_id?: string;
  status?: string;
}

export interface EmployeeCreate {
  employee_code: string;
  first_name?: string;
  last_name?: string;
  email: string;
  phone?: string;
  gender?: string;
  birth_date?: string;
  nationality?: string;
  address_street?: string;
  address_zip?: string;
  address_city?: string;
  address_country?: string;
  department_id?: string;
  role_id?: string;
  reports_to?: string;
  employment_type?: string;
  hire_date?: string;
  status?: string;
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
  address_street?: string;
  address_zip?: string;
  address_city?: string;
  address_country?: string;
  department_id?: string;
  role_id?: string;
  reports_to?: string;
  employment_type?: string;
  hire_date?: string;
  termination_date?: string;
  status?: string;
  timezone?: string;
  language?: string;
  theme?: string;
  notifications_enabled?: boolean;
  matrix_username?: string;
}

export interface Department {
  id: string;
  name: string;
  code?: string;
  description?: string;
  manager_id?: string;
  created_at?: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions_json?: string[];
  keycloak_id?: string;
}

export function useEmployees() {
  // State
  const employees = ref<Employee[]>([]);
  const departments = ref<Department[]>([]);
  const roles = ref<Role[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const total = ref(0);

  // Fetch employees with filters
  const fetchEmployees = async (params?: EmployeeFilters) => {
    loading.value = true;
    error.value = null;
    try {
      // Remove empty string values from params
      const cleanParams = params ? Object.fromEntries(
        Object.entries(params).filter(([_, value]) => value !== '' && value !== null && value !== undefined)
      ) : {};

      const response = await apiClient.get('/api/employees', { params: cleanParams });
      employees.value = response.data.employees;
      total.value = response.data.total;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Mitarbeiter';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Fetch single employee by ID
  const fetchEmployee = async (id: string): Promise<Employee> => {
    try {
      const response = await apiClient.get(`/api/employees/${id}`);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden des Mitarbeiters';
      throw err;
    }
  };

  // Create new employee
  const createEmployee = async (data: EmployeeCreate): Promise<Employee> => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.post('/api/employees', data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Erstellen des Mitarbeiters';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Update employee
  const updateEmployee = async (id: string, data: EmployeeUpdate): Promise<Employee> => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.put(`/api/employees/${id}`, data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Aktualisieren des Mitarbeiters';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Delete employee (soft delete)
  const deleteEmployee = async (id: string): Promise<void> => {
    loading.value = true;
    error.value = null;
    try {
      await apiClient.delete(`/api/employees/${id}`);
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Löschen des Mitarbeiters';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Reset employee password
  const resetPassword = async (
    id: string,
    newPassword: string,
    sendNotification: boolean = true
  ): Promise<void> => {
    loading.value = true;
    error.value = null;
    try {
      await apiClient.post(`/api/employees/${id}/reset-password`, {
        new_password: newPassword,
        send_notification: sendNotification,
      });
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Zurücksetzen des Passworts';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Update employee status
  const updateStatus = async (
    id: string,
    status: string,
    reason?: string
  ): Promise<Employee> => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.patch(`/api/employees/${id}/status`, {
        status,
        reason,
      });
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Ändern des Status';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Fetch departments
  const fetchDepartments = async (): Promise<Department[]> => {
    try {
      const response = await apiClient.get('/api/departments');
      departments.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Abteilungen';
      throw err;
    }
  };

  // Fetch roles
  const fetchRoles = async (): Promise<Role[]> => {
    try {
      const response = await apiClient.get('/api/roles');
      roles.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Rollen';
      throw err;
    }
  };

  return {
    // State
    employees,
    departments,
    roles,
    loading,
    error,
    total,

    // Methods
    fetchEmployees,
    fetchEmployee,
    createEmployee,
    updateEmployee,
    deleteEmployee,
    resetPassword,
    updateStatus,
    fetchDepartments,
    fetchRoles,
  };
}
