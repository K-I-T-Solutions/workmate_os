---
layout: default
title: Phase 3 Implementation Plan
parent: Roadmap
nav_order: 6
---

# Phase 3: SSO & Admin - Implementierungsplan

**Status:** 80% Complete → 100% Complete
**Zeitraum:** Januar 2026
**Ziel:** Fertigstellung von Audit Log Backend und System Settings Backend

---

## Executive Summary

Phase 3 ist bereits zu **80% abgeschlossen**. Die verbleibenden 20% umfassen:

1. **Audit Log Backend API** (10%) - Ermöglicht Abruf von Audit-Logs aus dem Admin Panel
2. **System Settings Backend** (10%) - Persistente Speicherung von System-Einstellungen

**Geschätzter Aufwand:** 8-12 Stunden
**Geschätzte Dauer:** 2-3 Arbeitstage

---

## Aktueller Stand (80%)

### ✅ Bereits implementiert

1. **Zitadel SSO Integration** (100%)
   - OAuth2 Authorization Code Flow
   - Token Validation
   - User Info Extraction
   - Session Management

2. **Role Mapping** (100%)
   - Zitadel Role → WorkmateOS Role Synchronisation
   - Automatic Permission Inheritance
   - `keycloak_id` (eigentlich Zitadel Role ID) Verknüpfung

3. **Wildcard Permissions** (100%)
   - `*` - Voller Zugriff
   - `module.*` - Modul-weiter Zugriff
   - `module.resource.*` - Ressourcen-spezifischer Zugriff
   - `module.resource.action` - Granulare Berechtigung

4. **Admin Panel Frontend** (100%)
   - AdminApp Container mit Tab-Navigation
   - EmployeesPage (Tabelle mit CRUD)
   - DepartmentsPage (Cards mit CRUD)
   - RolesPage (Cards mit Permissions)
   - AuditLogPage (UI fertig, Mock-Daten)
   - SystemSettingsPage (UI fertig, localStorage-Fallback)

5. **Admin Panel Backend APIs** (100%)
   - Employees API (CRUD, Suche, Filterung, Pagination)
   - Departments API (CRUD)
   - Roles API (CRUD, Permission Management)

6. **Audit Log Foundation** (50%)
   - ✅ Datenbank-Tabelle `audit_logs` existiert
   - ✅ Finance-spezifisches Audit-Logging implementiert
   - ✅ Helper-Funktionen für Invoice/Payment/Expense Logging
   - ❌ Kein API-Endpoint zum Abrufen der Logs

---

## Was fehlt noch? (20%)

### 1. Audit Log Backend API (10%)

**Status:** Frontend fertig, Backend fehlt

**Vorhandene Infrastruktur:**
- ✅ Datenbank-Modell: `app/modules/backoffice/invoices/models.py::AuditLog`
- ✅ Migration: `2026_01_02_1525-8c8325d750e6_add_audit_logs_and_soft_delete`
- ✅ Helper-Funktionen: `app/modules/backoffice/invoices/audit.py`
- ✅ Schemas: `app/modules/backoffice/invoices/schemas.py::AuditLogResponse`
- ✅ Frontend UI: `ui/src/modules/admin/pages/AuditLogPage.vue` (mit Mock-Daten)

**Was fehlt:**
- ❌ API Router für `/api/audit-logs`
- ❌ CRUD Service für Audit Logs
- ❌ Filterung & Pagination
- ❌ Integration ins Admin Panel

**Datenbank-Schema (bereits vorhanden):**
```sql
audit_logs (
  id UUID PRIMARY KEY,
  entity_type VARCHAR(50) NOT NULL,  -- "Invoice", "Payment", "Employee", etc.
  entity_id UUID NOT NULL,
  action VARCHAR(50) NOT NULL,       -- "create", "update", "delete", "status_change"
  old_values JSON,
  new_values JSON,
  user_id VARCHAR(100),
  timestamp TIMESTAMP DEFAULT NOW(),
  ip_address VARCHAR(45)
)
```

**Geplante API-Endpoints:**

#### `GET /api/audit-logs`

Liste aller Audit-Logs mit umfangreicher Filterung.

**Query-Parameter:**
- `skip` (int, default=0) - Pagination offset
- `limit` (int, default=50, max=500) - Anzahl Einträge
- `user_id` (str, optional) - Filter nach User
- `action` (str, optional) - Filter nach Aktion (create, update, delete, status_change)
- `entity_type` (str, optional) - Filter nach Entitätstyp (Invoice, Payment, Employee, etc.)
- `date_from` (datetime, optional) - Von Datum (ISO 8601)
- `date_to` (datetime, optional) - Bis Datum (ISO 8601)

**Response:**
```json
{
  "total": 250,
  "items": [
    {
      "id": "uuid",
      "entity_type": "Invoice",
      "entity_id": "uuid",
      "action": "update",
      "old_values": {"status": "draft"},
      "new_values": {"status": "sent"},
      "user_id": "user@example.com",
      "timestamp": "2026-01-05T14:30:00Z",
      "ip_address": "192.168.1.100"
    }
  ],
  "skip": 0,
  "limit": 50
}
```

**Berechtigungen:**
- Erforderlich: `admin.audit.*` oder `admin.*` oder `*`

**Implementierungs-Schritte:**

1. **Router erstellen** (`backend/app/modules/admin/audit_routes.py`)
   ```python
   from fastapi import APIRouter, Depends, Query
   from sqlalchemy.orm import Session
   from typing import Optional
   from datetime import datetime

   router = APIRouter(prefix="/api/audit-logs", tags=["Audit"])

   @router.get("", response_model=schemas.AuditLogListResponse)
   async def list_audit_logs(
       skip: int = Query(0, ge=0),
       limit: int = Query(50, ge=1, le=500),
       user_id: Optional[str] = None,
       action: Optional[str] = None,
       entity_type: Optional[str] = None,
       date_from: Optional[datetime] = None,
       date_to: Optional[datetime] = None,
       db: Session = Depends(get_db),
       current_user = Depends(require_permissions("admin.audit.*", "admin.*", "*"))
   ):
       logs, total = await service.get_audit_logs(
           db, skip, limit, user_id, action, entity_type, date_from, date_to
       )
       return {"items": logs, "total": total, "skip": skip, "limit": limit}
   ```

2. **Service erstellen** (`backend/app/modules/admin/audit_service.py`)
   ```python
   from sqlalchemy.orm import Session
   from sqlalchemy import and_
   from app.modules.backoffice.invoices.models import AuditLog

   async def get_audit_logs(
       db: Session,
       skip: int,
       limit: int,
       user_id: Optional[str],
       action: Optional[str],
       entity_type: Optional[str],
       date_from: Optional[datetime],
       date_to: Optional[datetime]
   ):
       query = db.query(AuditLog)

       # Filter anwenden
       filters = []
       if user_id:
           filters.append(AuditLog.user_id == user_id)
       if action:
           filters.append(AuditLog.action == action)
       if entity_type:
           filters.append(AuditLog.entity_type == entity_type)
       if date_from:
           filters.append(AuditLog.timestamp >= date_from)
       if date_to:
           filters.append(AuditLog.timestamp <= date_to)

       if filters:
           query = query.filter(and_(*filters))

       # Count total
       total = query.count()

       # Pagination & Sortierung
       logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

       return logs, total
   ```

3. **Router in main.py registrieren**
   ```python
   from app.modules.admin import audit_routes

   app.include_router(audit_routes.router)
   ```

4. **Frontend anpassen** (`ui/src/modules/admin/pages/AuditLogPage.vue`)
   - Mock-Daten entfernen
   - Echte API-Calls implementieren
   - Error Handling hinzufügen

**Zeitaufwand:** 3-4 Stunden

---

### 2. System Settings Backend (10%)

**Status:** Frontend fertig (localStorage), Backend fehlt komplett

**Vorhandene Infrastruktur:**
- ✅ Frontend UI: `ui/src/modules/admin/pages/SystemSettingsPage.vue`
- ✅ localStorage-Fallback für Settings
- ❌ Keine Backend-Implementierung

**Was fehlt:**
- ❌ Datenbank-Modell für System Settings
- ❌ Alembic Migration
- ❌ API Router für `/api/settings`
- ❌ CRUD Service
- ❌ Validation & Caching

**Geplante Implementierung:**

#### Datenbank-Modell

**Datei:** `backend/app/modules/admin/models.py`

```python
from sqlalchemy import Column, String, Integer, Boolean
from app.core.database import Base
from app.core.mixins import UUIDMixin

class SystemSettings(Base, UUIDMixin):
    """
    Globale System-Einstellungen.

    Es gibt nur einen Datensatz in dieser Tabelle (Singleton-Pattern).
    """
    __tablename__ = "system_settings"

    # Firmeninformationen
    company_name = Column(String(200), nullable=False, default="WorkmateOS")
    company_legal = Column(String(50), default="")
    tax_number = Column(String(50), default="")
    registration_number = Column(String(50), default="")
    address_street = Column(String(200), default="")
    address_zip = Column(String(10), default="")
    address_city = Column(String(100), default="")
    address_country = Column(String(100), default="Deutschland")
    company_email = Column(String(100), default="")
    company_phone = Column(String(50), default="")
    company_website = Column(String(200), default="")

    # Lokalisierung
    default_timezone = Column(String(50), nullable=False, default="Europe/Berlin")
    default_language = Column(String(10), nullable=False, default="de")
    default_currency = Column(String(10), nullable=False, default="EUR")
    date_format = Column(String(20), nullable=False, default="DD.MM.YYYY")

    # Arbeitszeiten
    working_hours_per_day = Column(Integer, nullable=False, default=8)
    working_days_per_week = Column(Integer, nullable=False, default=5)
    vacation_days_per_year = Column(Integer, nullable=False, default=30)
    weekend_saturday = Column(Boolean, nullable=False, default=True)
    weekend_sunday = Column(Boolean, nullable=False, default=True)

    # System
    maintenance_mode = Column(Boolean, nullable=False, default=False)
    allow_registration = Column(Boolean, nullable=False, default=False)
    require_email_verification = Column(Boolean, nullable=False, default=True)
```

#### Alembic Migration

**Datei:** `backend/alembic/versions/XXXX_add_system_settings.py`

```python
"""add system settings table

Revision ID: XXXX
Revises: [PREVIOUS_REVISION]
Create Date: 2026-01-XX XX:XX:XX
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    op.create_table('system_settings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False, server_default='WorkmateOS'),
        sa.Column('company_legal', sa.String(length=50), server_default=''),
        sa.Column('tax_number', sa.String(length=50), server_default=''),
        sa.Column('registration_number', sa.String(length=50), server_default=''),
        sa.Column('address_street', sa.String(length=200), server_default=''),
        sa.Column('address_zip', sa.String(length=10), server_default=''),
        sa.Column('address_city', sa.String(length=100), server_default=''),
        sa.Column('address_country', sa.String(length=100), server_default='Deutschland'),
        sa.Column('company_email', sa.String(length=100), server_default=''),
        sa.Column('company_phone', sa.String(length=50), server_default=''),
        sa.Column('company_website', sa.String(length=200), server_default=''),

        sa.Column('default_timezone', sa.String(length=50), nullable=False, server_default='Europe/Berlin'),
        sa.Column('default_language', sa.String(length=10), nullable=False, server_default='de'),
        sa.Column('default_currency', sa.String(length=10), nullable=False, server_default='EUR'),
        sa.Column('date_format', sa.String(length=20), nullable=False, server_default='DD.MM.YYYY'),

        sa.Column('working_hours_per_day', sa.Integer(), nullable=False, server_default='8'),
        sa.Column('working_days_per_week', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('vacation_days_per_year', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('weekend_saturday', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('weekend_sunday', sa.Boolean(), nullable=False, server_default='true'),

        sa.Column('maintenance_mode', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('allow_registration', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('require_email_verification', sa.Boolean(), nullable=False, server_default='true'),

        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),

        sa.PrimaryKeyConstraint('id')
    )

    # Initial Settings-Eintrag erstellen (Singleton)
    op.execute("""
        INSERT INTO system_settings (id, company_name)
        VALUES (gen_random_uuid(), 'WorkmateOS')
    """)

def downgrade() -> None:
    op.drop_table('system_settings')
```

#### Pydantic Schemas

**Datei:** `backend/app/modules/admin/schemas.py`

```python
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator
from typing import Optional

class SystemSettingsResponse(BaseModel):
    """System Settings Response."""
    # Firmeninformationen
    company_name: str
    company_legal: Optional[str] = ""
    tax_number: Optional[str] = ""
    registration_number: Optional[str] = ""
    address_street: Optional[str] = ""
    address_zip: Optional[str] = ""
    address_city: Optional[str] = ""
    address_country: str = "Deutschland"
    company_email: Optional[str] = ""
    company_phone: Optional[str] = ""
    company_website: Optional[str] = ""

    # Lokalisierung
    default_timezone: str = "Europe/Berlin"
    default_language: str = "de"
    default_currency: str = "EUR"
    date_format: str = "DD.MM.YYYY"

    # Arbeitszeiten
    working_hours_per_day: int = Field(ge=1, le=24, default=8)
    working_days_per_week: int = Field(ge=1, le=7, default=5)
    vacation_days_per_year: int = Field(ge=0, le=365, default=30)
    weekend_saturday: bool = True
    weekend_sunday: bool = True

    # System
    maintenance_mode: bool = False
    allow_registration: bool = False
    require_email_verification: bool = True

    model_config = ConfigDict(from_attributes=True)


class SystemSettingsUpdate(BaseModel):
    """System Settings Update (alle Felder optional)."""
    company_name: Optional[str] = None
    company_legal: Optional[str] = None
    tax_number: Optional[str] = None
    registration_number: Optional[str] = None
    address_street: Optional[str] = None
    address_zip: Optional[str] = None
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    company_website: Optional[str] = None

    default_timezone: Optional[str] = None
    default_language: Optional[str] = None
    default_currency: Optional[str] = None
    date_format: Optional[str] = None

    working_hours_per_day: Optional[int] = Field(None, ge=1, le=24)
    working_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    vacation_days_per_year: Optional[int] = Field(None, ge=0, le=365)
    weekend_saturday: Optional[bool] = None
    weekend_sunday: Optional[bool] = None

    maintenance_mode: Optional[bool] = None
    allow_registration: Optional[bool] = None
    require_email_verification: Optional[bool] = None

    @field_validator('company_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @field_validator('company_website')
    def validate_url(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
```

#### API Router

**Datei:** `backend/app/modules/admin/settings_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth.permissions import require_permissions
from app.modules.admin import models, schemas, service

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=schemas.SystemSettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    current_user = Depends(require_permissions("admin.settings.*", "admin.*", "*"))
):
    """
    Abrufen der System-Einstellungen.

    Berechtigungen: admin.settings.*, admin.*, *
    """
    settings = await service.get_or_create_settings(db)
    return settings


@router.put("", response_model=schemas.SystemSettingsResponse)
async def update_settings(
    settings_update: schemas.SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permissions("admin.settings.*", "admin.*", "*"))
):
    """
    Aktualisieren der System-Einstellungen.

    Alle Felder sind optional. Nur angegebene Felder werden aktualisiert.

    Berechtigungen: admin.settings.*, admin.*, *
    """
    settings = await service.update_settings(db, settings_update)
    return settings
```

#### Service

**Datei:** `backend/app/modules/admin/service.py`

```python
from sqlalchemy.orm import Session
from app.modules.admin import models, schemas
from datetime import datetime

async def get_or_create_settings(db: Session) -> models.SystemSettings:
    """
    Holt die System-Einstellungen oder erstellt sie, falls sie nicht existieren.

    Singleton-Pattern: Es gibt nur einen Datensatz.
    """
    settings = db.query(models.SystemSettings).first()

    if not settings:
        # Erstelle Default-Settings
        settings = models.SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


async def update_settings(
    db: Session,
    settings_update: schemas.SystemSettingsUpdate
) -> models.SystemSettings:
    """
    Aktualisiert die System-Einstellungen.

    Nur angegebene Felder werden aktualisiert (PATCH-Semantik).
    """
    settings = await get_or_create_settings(db)

    # Update nur die angegebenen Felder
    update_data = settings_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(settings, field, value)

    settings.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(settings)

    return settings
```

#### Frontend anpassen

**Datei:** `ui/src/modules/admin/pages/SystemSettingsPage.vue`

```typescript
// localStorage-Fallback entfernen
// Echte API-Calls implementieren

async function loadSettings() {
  loading.value = true;
  try {
    const response = await apiClient.get('/api/settings');
    settings.value = response.data;
  } catch (error) {
    console.error('Failed to load settings:', error);
    // Fallback zu Default-Werten
  } finally {
    loading.value = false;
  }
}

async function saveSettings() {
  saving.value = true;
  try {
    const response = await apiClient.put('/api/settings', settings.value);
    settings.value = response.data;
    showSuccess.value = true;
    setTimeout(() => showSuccess.value = false, 3000);
  } catch (error) {
    console.error('Failed to save settings:', error);
    alert('Fehler beim Speichern der Einstellungen');
  } finally {
    saving.value = false;
  }
}
```

**Implementierungs-Schritte:**

1. ✅ Datenbank-Modell erstellen
2. ✅ Alembic Migration erstellen und ausführen
3. ✅ Pydantic Schemas definieren
4. ✅ Service-Funktionen implementieren
5. ✅ API Router erstellen
6. ✅ Router in main.py registrieren
7. ✅ Frontend anpassen (localStorage entfernen, API anbinden)
8. ✅ Testen (CRUD-Operationen, Validierung)

**Zeitaufwand:** 4-5 Stunden

---

## Implementierungs-Reihenfolge

### Empfohlene Vorgehensweise:

1. **Tag 1: System Settings Backend** (4-5h)
   - Datenbank-Modell erstellen
   - Migration erstellen & ausführen
   - Schemas definieren
   - Service implementieren
   - Router erstellen & registrieren
   - Testen mit Postman/curl

2. **Tag 2: Audit Log Backend** (3-4h)
   - Service für Audit Logs erstellen
   - Router implementieren
   - Filterung & Pagination testen
   - Integration testen

3. **Tag 3: Frontend-Integration & Testing** (2-3h)
   - SystemSettingsPage anpassen (API statt localStorage)
   - AuditLogPage anpassen (API statt Mock-Daten)
   - End-to-End Testing
   - Error Handling verfeinern
   - Dokumentation aktualisieren

---

## Testing-Checkliste

### System Settings

- [ ] GET /api/settings liefert Default-Werte beim ersten Aufruf
- [ ] PUT /api/settings aktualisiert Werte korrekt
- [ ] Validierung funktioniert (Email, URL, numerische Bereiche)
- [ ] Nur berechtigte User können zugreifen (admin.settings.*, admin.*, *)
- [ ] Frontend zeigt aktuelle Werte korrekt an
- [ ] Frontend speichert Änderungen erfolgreich
- [ ] Success-Message wird nach Speichern angezeigt

### Audit Log

- [ ] GET /api/audit-logs liefert alle Logs
- [ ] Filterung nach user_id funktioniert
- [ ] Filterung nach action funktioniert
- [ ] Filterung nach entity_type funktioniert
- [ ] Datum-Range-Filterung funktioniert
- [ ] Pagination funktioniert korrekt
- [ ] Sortierung nach timestamp DESC funktioniert
- [ ] Nur berechtigte User können zugreifen (admin.audit.*, admin.*, *)
- [ ] Frontend lädt Logs korrekt
- [ ] Filter im Frontend funktionieren
- [ ] Detail-Dialog zeigt vollständige Informationen

---

## Dokumentations-Updates

Nach Implementierung folgende Dokumente aktualisieren:

1. **docs/roadmap/README.md**
   - Phase 3 Status auf 100% setzen
   - Audit Log Backend & System Settings Backend als completed markieren

2. **docs/wiki/backend/ADMIN_PANEL.md**
   - "Coming Soon" Marker entfernen
   - API-Dokumentation für beide Endpoints hinzufügen
   - Code-Beispiele ergänzen

3. **docs/roadmap/phase2_status_2026_01_06.md** → **phase3_status_2026_01_XX.md**
   - Neuen Status-Report für Phase 3 Abschluss erstellen
   - Lessons Learned dokumentieren

4. **Daily Report erstellen**
   - `docs/daily_reports/2026-01-XX_phase3_completion.md`

---

## Erfolgskriterien

Phase 3 gilt als abgeschlossen, wenn:

- [x] Zitadel SSO Integration funktioniert
- [x] Role Mapping funktioniert
- [x] Wildcard Permissions funktionieren
- [x] Admin Panel Frontend ist vollständig
- [ ] **Audit Log Backend API ist implementiert und getestet**
- [ ] **System Settings Backend ist implementiert und getestet**
- [ ] Admin Panel ist vollständig funktional (keine Mock-Daten, kein localStorage)
- [ ] Dokumentation ist aktualisiert
- [ ] Tests sind geschrieben und bestehen

---

## Risiken & Mitigationen

### Risiko 1: Audit-Log-Schema-Konflikte

**Problem:** Es existieren zwei verschiedene Audit-Log-Implementierungen:
- Finance-spezifisches Audit-Log (entity_type, entity_id, ...)
- Core Audit-Log (user_email, role, action, resource, ...)

**Mitigation:**
- Zunächst das bestehende Finance Audit-Log für Admin Panel verwenden
- Später: Core Audit-Log System harmonisieren oder für andere Module erweitern
- Für Phase 3: Finance Audit-Log ist ausreichend für Admin Panel Anzeige

### Risiko 2: Performance bei vielen Audit-Logs

**Problem:** Audit-Logs können sehr groß werden (1000+ Einträge)

**Mitigation:**
- Effiziente Indizes sind bereits vorhanden (entity, timestamp, user_id, action)
- Pagination mit max. 500 Einträgen pro Request
- Optional: Retention-Policy implementieren (Logs > 1 Jahr löschen)

### Risiko 3: Singleton-Pattern für System Settings

**Problem:** Nur ein Datensatz in system_settings Tabelle

**Mitigation:**
- Migration erstellt automatisch den ersten Eintrag
- Service-Funktion erstellt Eintrag, falls nicht vorhanden (get_or_create)
- Frontend hat Error Handling für fehlende Settings

---

## Ausblick: Phase 4

Nach Abschluss von Phase 3 (SSO & Admin) folgt **Phase 4: Enterprise Features**.

**Geplante Features (Q1-Q2 2026):**

1. **Multi-Tenancy**
   - Mehrere Firmen in einer Installation
   - Tenant-isolierte Datenbank
   - Subdomain-basiertes Routing

2. **Advanced Reporting**
   - Custom Reports Builder
   - Export zu Excel/PDF
   - Scheduled Reports (E-Mail)

3. **Mobile App**
   - React Native oder Flutter
   - Zeiterfassung unterwegs
   - Push-Notifications

4. **API Versioning**
   - `/api/v1/...` und `/api/v2/...`
   - Deprecation Warnings
   - Breaking Changes Management

5. **Webhooks**
   - Event-basierte Webhooks
   - Retry-Mechanismus
   - Webhook-Management UI

6. **Rate Limiting**
   - Pro User/API-Key
   - Unterschiedliche Limits für verschiedene Endpunkte
   - Rate Limit Headers

**Geschätzter Aufwand Phase 4:** 6-8 Wochen

---

## Zusammenfassung

**Phase 3 Completion Plan:**
- ✅ 80% bereits fertig (Zitadel SSO, Role Mapping, Permissions, Admin Panel UI)
- 🔄 20% verbleibend (Audit Log API + System Settings API)
- ⏱️ Geschätzter Aufwand: 8-12 Stunden
- 📅 Geschätzte Dauer: 2-3 Arbeitstage
- 🎯 Ziel: Phase 3 auf 100% bringen und für Production freigeben

**Priorität:**
1. System Settings Backend (kritisch für produktiven Betrieb)
2. Audit Log Backend (wichtig für Compliance & Debugging)

**Nächste Schritte:**
1. Diesen Plan mit dem Team reviewen
2. Implementierung starten (System Settings zuerst)
3. Testing & Integration
4. Dokumentation aktualisieren
5. Phase 3 als abgeschlossen markieren
6. Release v3.0 vorbereiten

---

**Erstellt:** 05. Januar 2026
**Autor:** Claude Code & Joshua Phu Kuhrau
**Version:** 1.0
**Status:** Ready for Implementation

🚀 **Let's finish Phase 3!**
