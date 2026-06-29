export type ReminderPriority = "low" | "medium" | "high"

export interface Reminder {
  id: string
  title: string
  description: string | null
  due_date: string | null
  priority: ReminderPriority
  is_done: boolean
  created_at: string
}

export interface ReminderCreate {
  title: string
  description?: string
  due_date?: string
  priority?: ReminderPriority
}
