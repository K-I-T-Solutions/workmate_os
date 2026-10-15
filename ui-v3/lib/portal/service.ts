import { portalClient } from "./client"

export interface PortalMe {
  contact_id: string
  firstname: string
  lastname: string
  email: string | null
  customer_id: string
  customer_name: string
}

export interface PortalTicket {
  id: string
  ticket_number: string
  title: string
  status: string
  priority: string
  created_at: string
  updated_at: string | null
  resolved_at: string | null
}

export interface PortalComment {
  id: string
  content: string
  from_customer: boolean
  created_at: string
}

export interface PortalTicketDetail extends PortalTicket {
  description: string | null
  comments: PortalComment[]
}

export const portalService = {
  async requestLink(email: string): Promise<string> {
    const { data } = await portalClient.post("/api/portal/auth/request-link", { email })
    return data.message
  },

  async verify(token: string): Promise<{ access_token: string; expires_at: string; me: PortalMe }> {
    const { data } = await portalClient.post("/api/portal/auth/verify", { token })
    return data
  },

  async me(): Promise<PortalMe> {
    const { data } = await portalClient.get("/api/portal/me")
    return data
  },

  async tickets(status?: "open" | "closed"): Promise<PortalTicket[]> {
    const { data } = await portalClient.get("/api/portal/tickets", { params: { status } })
    return data.items
  },

  async ticket(id: string): Promise<PortalTicketDetail> {
    const { data } = await portalClient.get(`/api/portal/tickets/${id}`)
    return data
  },

  async createTicket(payload: { title: string; description: string; priority: "low" | "medium" | "high" }): Promise<PortalTicketDetail> {
    const { data } = await portalClient.post("/api/portal/tickets", payload)
    return data
  },

  async reply(id: string, content: string): Promise<PortalTicketDetail> {
    const { data } = await portalClient.post(`/api/portal/tickets/${id}/comments`, { content })
    return data
  },
}

export const PORTAL_STATUS_LABELS: Record<string, string> = {
  open: "Offen",
  in_progress: "In Bearbeitung",
  escalated: "In Bearbeitung",
  waiting: "Wartet auf Ihre Rückmeldung",
  resolved: "Gelöst",
  closed: "Geschlossen",
}

export const PORTAL_STATUS_COLOR: Record<string, string> = {
  open: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  in_progress: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  escalated: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  waiting: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  resolved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  closed: "bg-muted text-muted-foreground",
}
