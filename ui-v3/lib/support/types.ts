export type TicketStatus = "open" | "in_progress" | "waiting" | "resolved" | "closed"
export type TicketPriority = "low" | "medium" | "high" | "urgent"

export interface Ticket {
  id: string
  ticket_number: string
  title: string
  description: string | null
  type: string
  status: TicketStatus | string
  priority: TicketPriority | string
  category: string
  channel: string
  customer_id: string | null
  assignee_id: string | null
  reporter_id: string | null
  reporter_email: string | null
  sla_deadline: string | null
  sla_breached: boolean
  comment_count: number
  created_at: string
  updated_at: string
  resolved_at: string | null
  closed_at: string | null
}

export interface TicketDetail extends Ticket {
  comments: TicketComment[]
  events: TicketEvent[]
}

export interface TicketComment {
  id: string
  ticket_id: string
  author_id: string | null
  content: string
  is_internal: boolean
  created_at: string
}

export interface TicketEvent {
  id: string
  ticket_id: string
  event_type: string
  actor_id: string | null
  old_value: Record<string, unknown> | null
  new_value: Record<string, unknown> | null
  comment: string | null
  created_at: string
}

export interface TicketListResponse {
  items: Ticket[]
  total: number
  skip: number
  limit: number
}

export interface CreateTicketPayload {
  title: string
  description?: string | null
  type: string
  priority: string
  category: string
  channel: string
  customer_id?: string | null
  reporter_email?: string | null
}

export interface UpdateTicketPayload {
  title?: string
  description?: string | null
  type?: string
  status?: string
  priority?: string
  category?: string
  customer_id?: string | null
  assignee_id?: string | null
}
