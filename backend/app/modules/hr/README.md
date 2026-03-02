# HR Module - Leave Management

## Overview

Das HR-Modul verwaltet Urlaubsanträge, Krankmeldungen und Abwesenheiten für Mitarbeiter.

**Wichtig:** Das HR-Modul verwendet **Core Employees** aus `app.modules.employees`. Es gibt keine separaten HR-Employees!

## Architecture

### Database Integration

Alle HR-Tabellen referenzieren die **Core `employees`-Tabelle**:

```python
# app/modules/hr/leave/models.py
from app.modules.employees.models import Employee

class LeaveRequest(Base):
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    employee: Mapped["Employee"] = relationship("Employee")
```

### Tables

#### Core Reference
- `employees` (from `app.modules.employees`)

#### HR Tables
- `hr_leave_policies` - Urlaubsregelungen
- `hr_leave_balances` - Urlaubskontingente pro Mitarbeiter/Jahr
  - **References:** `employees.id`
- `hr_leave_requests` - Urlaubsanträge
  - **References:** `employees.id` (Antragsteller)
  - **References:** `employees.id` (Genehmiger)
- `hr_absence_calendar` - Team-Abwesenheitskalender
  - **References:** `employees.id`

### Foreign Key Relationships

```sql
-- LeaveBalance → Employee
hr_leave_balances.employee_id → employees.id (CASCADE)

-- LeaveRequest → Employee (Antragsteller)
hr_leave_requests.employee_id → employees.id (CASCADE)

-- LeaveRequest → Employee (Genehmiger)
hr_leave_requests.approved_by_id → employees.id (SET NULL)

-- AbsenceCalendar → Employee
hr_absence_calendar.employee_id → employees.id (CASCADE)
```

## API Endpoints

### Employees
Use Core Employee API:
- `GET /api/employees` - Liste aller Mitarbeiter
- `GET /api/employees/{id}` - Einzelner Mitarbeiter
- `POST /api/employees` - Mitarbeiter erstellen
- `PUT /api/employees/{id}` - Mitarbeiter aktualisieren
- `DELETE /api/employees/{id}` - Mitarbeiter löschen (soft delete)

### Leave Requests
- `GET /api/hr/leave-requests` - Liste aller Urlaubsanträge
- `GET /api/hr/leave-requests/{id}` - Einzelner Antrag
- `POST /api/hr/leave-requests` - Antrag erstellen
- `PUT /api/hr/leave-requests/{id}` - Antrag aktualisieren
- `POST /api/hr/leave-requests/{id}/approve` - Antrag genehmigen
- `POST /api/hr/leave-requests/{id}/reject` - Antrag ablehnen
- `DELETE /api/hr/leave-requests/{id}` - Antrag löschen

### Leave Balances
- `GET /api/hr/leave-balances` - Liste aller Kontingente
- `GET /api/hr/leave-balances/{id}` - Einzelnes Kontingent
- `POST /api/hr/leave-balances` - Kontingent erstellen
- `PUT /api/hr/leave-balances/{id}` - Kontingent aktualisieren
- `DELETE /api/hr/leave-balances/{id}` - Kontingent löschen

## Data Flow

### Creating a Leave Request

1. **Frontend** erstellt Antrag mit `employee_id` (UUID aus Core Employees)
2. **Backend** validiert:
   - Employee existiert (`employees` Tabelle)
   - Datumformat korrekt
   - Kontingent verfügbar
3. **Database** erstellt `hr_leave_requests` mit Foreign Key zu `employees.id`
4. **Response** inkludiert Employee-Daten via Relationship

### Approving a Leave Request

1. **Manager** genehmigt Antrag
2. **Backend** setzt:
   - `status = 'approved'`
   - `approved_by_id` (UUID des Managers aus Core Employees)
   - `approved_date`
3. **Database** aktualisiert `hr_leave_balances.vacation_used`
4. **Trigger** erstellt `hr_absence_calendar` Einträge

## Development Notes

### Adding New HR Features

Wenn neue HR-Features hinzugefügt werden:

1. **IMMER** Core `employees` referenzieren, NIEMALS eigene Employee-Tabelle erstellen
2. **Foreign Keys** korrekt setzen:
   ```python
   employee_id: Mapped[uuid.UUID] = mapped_column(
       ForeignKey("employees.id", ondelete="CASCADE")
   )
   ```
3. **Relationships** definieren:
   ```python
   employee: Mapped["Employee"] = relationship("Employee")
   ```
4. **Imports** aus Core verwenden:
   ```python
   if TYPE_CHECKING:
       from app.modules.employees.models import Employee
   ```

### Migrations

Bei neuen HR-Tabellen sicherstellen:
```python
sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
```

## Testing

```bash
# Create Employee (Core API)
POST /api/employees
{
  "employee_code": "KIT-0001",
  "email": "test@example.com",
  "first_name": "Max",
  "last_name": "Mustermann"
}

# Create Leave Request (HR API)
POST /api/hr/leave-requests
{
  "employee_id": "<uuid from above>",
  "leave_type": "vacation",
  "start_date": "2026-02-01",
  "end_date": "2026-02-14",
  "total_days": 10,
  "reason": "Winterurlaub"
}
```

## Schema Compatibility

### Employee Schema (Core)
```python
# From app.modules.employees.schemas
class EmployeeResponse:
    id: UUID
    employee_code: str
    email: str
    first_name: str | None
    last_name: str | None
    department_id: UUID | None
    hire_date: date | None
    status: str  # 'active' | 'inactive' | 'on_leave'
```

### LeaveRequest Schema (HR)
```python
# From app.modules.hr.leave.schemas
class LeaveRequestCreate:
    employee_id: UUID  # References employees.id
    leave_type: str
    start_date: date
    end_date: date
    total_days: Decimal
    reason: str | None
```

## Benefits of Core Integration

1. **Single Source of Truth** - Mitarbeiter-Daten nur in `employees`
2. **No Duplication** - Keine Synchronisation zwischen HR- und Core-Employees
3. **Referential Integrity** - Foreign Keys garantieren Daten-Konsistenz
4. **Cascading Deletes** - Employee-Löschung entfernt automatisch HR-Daten
5. **Unified API** - `/api/employees` für alle Module

## Migration History

- `2026-01-08 15:56` - Initial HR module structure
- `2026-01-08 16:11` - Complete leave management tables with Core Employee references

**Created:** 2026-01-08
**Last Updated:** 2026-01-08
**Version:** 1.0
