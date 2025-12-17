export type ActivityType = "call" | "email" | "onsite" | "remote" | "note";

export interface CrmActivity {
  id: string;
  customer_id: string;
  contact_id?: string | null;
  type: ActivityType;
  description: string;
  occurred_at: string;
  created_at: string;
}

export interface CreateCrmActivity {
  customer_id: string;
  contact_id?: string | null;
  type: ActivityType;
  description: string;
  occurred_at?: string;
}
