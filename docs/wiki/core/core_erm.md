# 🧩 Core Entity-Relationship Model

Das folgende DBML beschreibt das komplette Core-Schema.

```dbml
Project WorkmateOS {
  database_type: "PostgreSQL"
  note: "Core data model for Workmate OS (Employees, Departments, Roles, Documents, Reminders, Dashboards, Infra)"
}

Table employees {
  id uuid [pk]
  employee_code varchar [unique, not null, note: "KIT-0001 etc."]
  uuid_keycloak varchar [note: "Linked Keycloak user ID"]
  first_name varchar
  last_name varchar
  gender varchar [note: "male, female, diverse, other"]
  birth_date date
  nationality varchar
  photo_url varchar [note: "/uploads/avatars/..."]
  bio text
  email varchar [unique, not null]
  phone varchar
  address_street varchar
  address_zip varchar
  address_city varchar
  address_country varchar
  department_id uuid
  role_id uuid
  reports_to uuid [note: "Supervisor"]
  employment_type varchar [note: "Default fulltime; values: fulltime, parttime, intern, external"]
  hire_date date
  termination_date date
  status varchar [note: "Default active; values: active, inactive, on_leave"]
  timezone varchar [note: "Default Europe/Berlin"]
  language varchar [note: "Default de"]
  theme varchar [note: "Default catppuccin-frappe"]
  notifications_enabled boolean [note: "Default true"]
  matrix_username varchar [note: "@user:intern.phudevelopement.xyz"]
  created_at timestamp [note: "Default now()"]
  updated_at timestamp [note: "Default now()"]
  last_login timestamp
  Note: "Core employee entity with organizational & personal info"
}

Table departments {
  id uuid [pk]
  name varchar [not null]
  code varchar [note: "Short code, e.g. HR, FIN, IT"]
  description text
  manager_id uuid
  created_at timestamp [note: "Default now()"]
  Note: "Organizational unit such as IT, HR, Finance"
}

Table roles {
  id uuid [pk]
  name varchar [not null]
  description text
  keycloak_id varchar [note: "Linked Keycloak role ID"]
  permissions_json jsonb [note: "List of permissions, e.g. ['hr.view', 'finance.edit']"]
  Note: "System roles and access levels"
}

Table documents {
  id uuid [pk]
  title varchar
  file_path varchar [not null]
  type varchar [note: "pdf, image, doc, etc."]
  category varchar [note: "e.g. Krankmeldung, Vertrag, Rechnung"]
  owner_id uuid
  linked_module varchar [note: "Origin module e.g. HR, Finance"]
  uploaded_at timestamp [note: "Default now()"]
  checksum varchar
  is_confidential boolean [note: "Default false"]
  Note: "Central file storage and reference system"
}

Table reminders {
  id uuid [pk]
  title varchar
  description text
  due_date date
  priority varchar [note: "low, medium, high, critical"]
  linked_entity_type varchar [note: "Target type, e.g. Document, Ticket"]
  linked_entity_id uuid
  owner_id uuid
  status varchar [note: "Default open; values: open, done, overdue"]
  created_at timestamp [note: "Default now()"]
  notified boolean [note: "Default false"]
  Note: "Universal reminder and notification system"
}

Table dashboards {
  id uuid [pk]
  owner_id uuid
  widgets_json jsonb
  layout_json jsonb
  theme varchar [note: "Default catppuccin-frappe"]
  last_accessed timestamp
  Note: "User-specific workspace layout and preferences"
}

```

> 🔍 Kann direkt bei [dbdiagram.io](https://dbdiagram.io) eingefügt werden, um das Diagramm visuell anzuzeigen.
