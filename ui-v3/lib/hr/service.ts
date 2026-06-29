import { apiClient } from "@/lib/api/client"
import type {
  Employee, EmployeeListResponse, EmployeeCreate, EmployeeUpdate, EmployeeStatistics,
  LeaveRequest, LeaveRequestCreate, LeaveStatistics,
  JobPosting, JobPostingCreate, Application,
  Course, CourseCreate, OnboardingTemplate, OnboardingProcess,
  HeadcountStats, LeaveSummary, RecruitingFunnel,
  SalaryRecord, Benefit,
} from "./types"

export const hrService = {
  // Employees
  async listEmployees(params?: { search?: string; status?: string; limit?: number; skip?: number }): Promise<Employee[]> {
    const { data } = await apiClient.get<EmployeeListResponse>("/api/employees", { params })
    return data.employees ?? []
  },
  async getEmployee(id: string): Promise<Employee> {
    const { data } = await apiClient.get(`/api/employees/${id}`)
    return data
  },
  async createEmployee(payload: EmployeeCreate): Promise<Employee> {
    const { data } = await apiClient.post("/api/employees", payload)
    return data
  },
  async updateEmployee(id: string, payload: EmployeeUpdate): Promise<Employee> {
    const { data } = await apiClient.patch(`/api/employees/${id}`, payload)
    return data
  },
  async getStatistics(): Promise<EmployeeStatistics> {
    const { data } = await apiClient.get("/api/employees/statistics")
    return data
  },

  // Leave Requests
  async listLeaveRequests(params?: { status?: string; leave_type?: string; employee_id?: string }): Promise<LeaveRequest[]> {
    const { data } = await apiClient.get("/api/hr/leave/requests", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async createLeaveRequest(payload: LeaveRequestCreate): Promise<LeaveRequest> {
    const { data } = await apiClient.post("/api/hr/leave/requests", payload)
    return data
  },
  async approveLeave(id: string): Promise<LeaveRequest> {
    const { data } = await apiClient.post(`/api/hr/leave/requests/${id}/approve`)
    return data
  },
  async rejectLeave(id: string, reason: string): Promise<LeaveRequest> {
    const { data } = await apiClient.post(`/api/hr/leave/requests/${id}/reject`, { rejection_reason: reason })
    return data
  },
  async cancelLeaveRequest(id: string): Promise<LeaveRequest> {
    const { data } = await apiClient.post(`/api/hr/leave/requests/${id}/cancel`)
    return data
  },
  async getLeaveStatistics(): Promise<LeaveStatistics> {
    const { data } = await apiClient.get("/api/hr/leave/statistics")
    return data
  },

  // Job Postings
  async listJobs(params?: { status?: string }): Promise<JobPosting[]> {
    const { data } = await apiClient.get("/api/hr/recruiting/jobs", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async createJob(payload: JobPostingCreate): Promise<JobPosting> {
    const { data } = await apiClient.post("/api/hr/recruiting/jobs", payload)
    return data
  },
  async updateJob(id: string, payload: Partial<JobPostingCreate>): Promise<JobPosting> {
    const { data } = await apiClient.patch(`/api/hr/recruiting/jobs/${id}`, payload)
    return data
  },
  async deleteJob(id: string): Promise<void> {
    await apiClient.delete(`/api/hr/recruiting/jobs/${id}`)
  },

  async getMyEmployee(): Promise<Employee | null> {
    try {
      const { data } = await apiClient.get("/api/employees/me")
      return data
    } catch {
      return null
    }
  },

  // Applications
  async listApplications(params?: { job_posting_id?: string; status?: string }): Promise<Application[]> {
    const { data } = await apiClient.get("/api/hr/recruiting/applications", { params })
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async updateApplication(id: string, payload: { status?: string; notes?: string; interview_date?: string | null; rating?: number | null }): Promise<Application> {
    const { data } = await apiClient.patch(`/api/hr/recruiting/applications/${id}`, payload)
    return data
  },

  // Training
  async listCourses(): Promise<Course[]> {
    const { data } = await apiClient.get("/api/hr/training/courses")
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async createCourse(payload: CourseCreate): Promise<Course> {
    const { data } = await apiClient.post("/api/hr/training/courses", payload)
    return data
  },
  async enrollEmployee(courseId: string, employeeId: string): Promise<void> {
    await apiClient.post(`/api/hr/training/courses/${courseId}/enroll`, { employee_id: employeeId })
  },

  // Onboarding
  async listOnboardingTemplates(): Promise<OnboardingTemplate[]> {
    const { data } = await apiClient.get("/api/hr/onboarding/templates")
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async startOnboarding(payload: { employee_id: string; template_id: string; start_date: string }): Promise<OnboardingProcess> {
    const { data } = await apiClient.post("/api/hr/onboarding/processes", payload)
    return data
  },

  // Analytics
  async getHeadcount(): Promise<HeadcountStats> {
    const { data } = await apiClient.get("/api/hr/analytics/headcount")
    return data
  },
  async getLeaveSummary(): Promise<LeaveSummary> {
    const { data } = await apiClient.get("/api/hr/analytics/leave-summary")
    return data
  },
  async getRecruitingFunnel(): Promise<RecruitingFunnel> {
    const { data } = await apiClient.get("/api/hr/analytics/recruiting-funnel")
    return data
  },

  // Compensation
  async getEmployeeSalary(employeeId: string): Promise<SalaryRecord[]> {
    const { data } = await apiClient.get(`/api/hr/compensation/employees/${employeeId}/salary`)
    return Array.isArray(data) ? data : (data.items ?? [])
  },
  async getEmployeeBenefits(employeeId: string): Promise<Benefit[]> {
    const { data } = await apiClient.get(`/api/hr/compensation/employees/${employeeId}/benefits`)
    return Array.isArray(data) ? data : (data.items ?? [])
  },
}
