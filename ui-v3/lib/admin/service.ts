import { apiClient } from "@/lib/api/client"
import type {
  SystemSettings, SystemSettingsUpdate,
  Department, DepartmentCreate,
  Role, RoleCreate,
  AuditLog,
} from "./types"

export const adminService = {
  // Settings
  async getSettings(): Promise<SystemSettings> {
    const { data } = await apiClient.get("/api/settings")
    return data
  },
  async updateSettings(payload: SystemSettingsUpdate): Promise<SystemSettings> {
    const { data } = await apiClient.put("/api/settings", payload)
    return data
  },

  // Departments
  async listDepartments(): Promise<Department[]> {
    const { data } = await apiClient.get("/api/departments")
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async createDepartment(payload: DepartmentCreate): Promise<Department> {
    const { data } = await apiClient.post("/api/departments", payload)
    return data
  },
  async updateDepartment(id: string, payload: Partial<DepartmentCreate>): Promise<Department> {
    const { data } = await apiClient.patch(`/api/departments/${id}`, payload)
    return data
  },
  async deleteDepartment(id: string): Promise<void> {
    await apiClient.delete(`/api/departments/${id}`)
  },

  // Roles
  async listRoles(): Promise<Role[]> {
    const { data } = await apiClient.get("/api/roles")
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async createRole(payload: RoleCreate): Promise<Role> {
    const { data } = await apiClient.post("/api/roles", payload)
    return data
  },
  async updateRole(id: string, payload: Partial<RoleCreate>): Promise<Role> {
    const { data } = await apiClient.patch(`/api/roles/${id}`, payload)
    return data
  },
  async deleteRole(id: string): Promise<void> {
    await apiClient.delete(`/api/roles/${id}`)
  },

  // Audit Logs
  async listAuditLogs(params?: {
    skip?: number
    limit?: number
    action?: string
    entity_type?: string
    user_id?: string
  }): Promise<{ items: AuditLog[]; total: number }> {
    const { data } = await apiClient.get("/api/audit-logs", { params })
    return Array.isArray(data) ? { items: data, total: data.length } : { items: data.items ?? [], total: data.total ?? 0 }
  },
}
