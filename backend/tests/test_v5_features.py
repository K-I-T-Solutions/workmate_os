"""
Tests für die v5.0-Module (gegen echtes PostgreSQL – JSONB, FOR UPDATE, Partial Indexes).

Ausführen:
    TEST_DATABASE_URL=postgresql+psycopg2://user:pw@host:5432/test_db pytest tests/test_v5_features.py -v

Die Datenbank muss auf `alembic upgrade head` stehen. ACHTUNG: Die Tests leeren
die betroffenen Tabellen (TRUNCATE) – niemals gegen Prod/Dev-Daten laufen lassen.
"""
from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest

TEST_DB = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_DB, reason="TEST_DATABASE_URL nicht gesetzt")

if TEST_DB:
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    from app.core.auth.auth import get_current_user
    from app.core.settings.database import get_db
    from app.main import app
    from app.modules.backoffice.contracts.billing import run_billing
    from app.modules.backoffice.contracts.models import Contract, ContractItem
    from app.modules.backoffice.crm.models import Contact, Customer
    from app.modules.backoffice.invoices.models import Invoice
    from app.modules.backoffice.time_tracking.models import TimeEntry
    from app.modules.employees.models import Employee
    from app.modules.portal.models import PortalLoginToken
    from app.modules.portal.security import create_session_token, hash_link_token
    from app.modules.support.models import Ticket, TicketComment

    engine = create_engine(TEST_DB)
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

TABLES = [
    "portal_login_tokens", "software_licenses", "customer_assets", "time_entries",
    "invoice_line_items", "payments", "invoices", "contract_items", "contracts",
    "support_ticket_comments", "ticket_events", "support_tickets", "number_sequences",
    "contacts", "customers",
]

ADMIN = {"id": "test-admin", "email": "admin@test.local", "role": "Admin", "permissions": ["*"]}


@pytest.fixture()
def db():
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(TABLES)} RESTART IDENTITY CASCADE"))
    session = TestingSession()
    yield session
    session.close()


@pytest.fixture()
def client(db):
    def _db():
        s = TestingSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = lambda: ADMIN
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _customer(db, name="Musterfirma GmbH") -> Customer:
    c = Customer(customer_number=f"KIT-CUS-{uuid.uuid4().hex[:6]}", name=name, type="business", status="active")
    db.add(c)
    db.commit()
    return c


def _contract(db, customer, start: date, interval="monthly", **kw) -> Contract:
    c = Contract(
        contract_number=f"VT-T-{uuid.uuid4().hex[:6]}",
        title="Wartung Server",
        customer_id=customer.id,
        start_date=start,
        next_billing_date=start,
        billing_interval=interval,
        status=kw.pop("status", "active"),
        **kw,
    )
    c.items.append(ContractItem(position=1, description="Serverwartung", quantity=Decimal("1"), unit="Monat", unit_price=Decimal("100.00")))
    db.add(c)
    db.commit()
    return c


# ─── Verträge ────────────────────────────────────────────────

class TestContractBilling:
    def test_creates_draft_per_due_period_and_advances(self, db):
        cust = _customer(db)
        c = _contract(db, cust, start=date(2026, 8, 1))

        result = run_billing(db, run_date=date(2026, 10, 15))

        assert len(result.invoices_created) == 3  # Aug, Sep, Okt
        assert result.errors == []
        db.expire_all()
        c = db.get(Contract, c.id)
        assert c.next_billing_date == date(2026, 11, 1)
        assert c.last_billed_date == date(2026, 10, 1)

        invoices = db.query(Invoice).filter(Invoice.contract_id == c.id).all()
        assert len(invoices) == 3
        assert all(i.status == "draft" for i in invoices)
        assert all(i.total == Decimal("119.00") for i in invoices)
        assert any("01.10.2026 – 31.10.2026" in li.description for i in invoices for li in i.line_items)

    def test_second_run_is_idempotent(self, db):
        cust = _customer(db)
        _contract(db, cust, start=date(2026, 10, 1))
        assert len(run_billing(db, run_date=date(2026, 10, 15)).invoices_created) == 1
        assert len(run_billing(db, run_date=date(2026, 10, 15)).invoices_created) == 0

    def test_quarterly_interval(self, db):
        cust = _customer(db)
        c = _contract(db, cust, start=date(2026, 7, 1), interval="quarterly")
        result = run_billing(db, run_date=date(2026, 10, 15))
        assert [r["period_start"] for r in result.invoices_created] == ["2026-07-01", "2026-10-01"]
        db.expire_all()
        assert db.get(Contract, c.id).next_billing_date == date(2027, 1, 1)

    def test_expires_without_auto_renew(self, db):
        cust = _customer(db)
        c = _contract(db, cust, start=date(2026, 9, 1), end_date=date(2026, 9, 30), auto_renew=False)
        result = run_billing(db, run_date=date(2026, 10, 15))
        assert len(result.invoices_created) == 1
        assert result.contracts_expired == [c.contract_number]
        db.expire_all()
        assert db.get(Contract, c.id).status == "expired"

    def test_auto_renews(self, db):
        cust = _customer(db)
        c = _contract(db, cust, start=date(2026, 9, 1), end_date=date(2026, 9, 30), auto_renew=True, renewal_months=12)
        result = run_billing(db, run_date=date(2026, 10, 15))
        assert len(result.invoices_created) == 2
        assert result.contracts_renewed == [c.contract_number]
        db.expire_all()
        assert db.get(Contract, c.id).end_date == date(2027, 9, 30)

    def test_paused_and_draft_not_billed(self, db):
        cust = _customer(db)
        _contract(db, cust, start=date(2026, 10, 1), status="paused")
        _contract(db, cust, start=date(2026, 10, 1), status="draft")
        assert run_billing(db, run_date=date(2026, 10, 15)).invoices_created == []

    def test_api_create_and_stats(self, client, db):
        cust = _customer(db)
        r = client.post("/api/backoffice/contracts/", json={
            "title": "Managed Backup", "customer_id": str(cust.id), "contract_type": "subscription",
            "start_date": "2026-10-01", "status": "active", "billing_interval": "yearly",
            "items": [{"description": "Backup 1 TB", "unit_price": "1200.00", "unit": "Jahr"}],
        })
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["contract_number"].startswith("VT-2026-")
        assert Decimal(body["monthly_recurring_revenue"]) == Decimal("100.00")

        stats = client.get("/api/backoffice/contracts/stats").json()
        assert stats["active_contracts"] == 1

    def test_delete_with_invoices_refused(self, client, db):
        cust = _customer(db)
        c = _contract(db, cust, start=date(2026, 10, 1))
        run_billing(db, run_date=date(2026, 10, 15))
        assert client.delete(f"/api/backoffice/contracts/{c.id}").status_code == 409

    def test_job_endpoint_requires_api_key(self, client):
        r = client.post("/api/backoffice/contracts/jobs/billing", json={})
        assert r.status_code == 401


# ─── Assets ──────────────────────────────────────────────────

class TestAssets:
    def test_create_asset_and_expiring(self, client, db):
        cust = _customer(db)
        soon = (date.today() + timedelta(days=10)).isoformat()
        r = client.post("/api/backoffice/assets/", json={
            "name": "Fileserver", "asset_type": "server", "customer_id": str(cust.id),
            "serial_number": "SN123", "warranty_until": soon,
        })
        assert r.status_code == 201, r.text
        assert r.json()["asset_tag"] == "AS-00001"

        r = client.post("/api/backoffice/assets/licenses", json={
            "product_name": "Microsoft 365 Business", "customer_id": str(cust.id),
            "seats": 5, "valid_until": soon,
        })
        assert r.status_code == 201, r.text

        exp = client.get("/api/backoffice/assets/expiring?within_days=30").json()
        assert {i["kind"] for i in exp["items"]} == {"warranty", "license"}

    def test_cross_customer_reference_rejected(self, client, db):
        a, b = _customer(db, "A"), _customer(db, "B")
        c = _contract(db, a, start=date(2026, 10, 1))
        r = client.post("/api/backoffice/assets/", json={
            "name": "PC", "customer_id": str(b.id), "contract_id": str(c.id),
        })
        assert r.status_code == 422


# ─── Ticket-Zeiten → Rechnung ────────────────────────────────

class TestTicketTimeBilling:
    def _setup(self, db):
        cust = _customer(db)
        emp = Employee(employee_code=f"T-{uuid.uuid4().hex[:6]}", email=f"{uuid.uuid4().hex[:6]}@t.local", first_name="Max", last_name="Muster")
        db.add(emp)
        ticket = Ticket(ticket_number=f"TKT-{uuid.uuid4().hex[:6]}", title="Drucker offline", customer_id=cust.id)
        db.add(ticket)
        db.commit()
        return cust, emp, ticket

    def test_time_entry_inherits_customer_from_ticket(self, client, db):
        cust, emp, ticket = self._setup(db)
        r = client.post("/api/backoffice/time-tracking/", json={
            "employee_id": str(emp.id), "ticket_id": str(ticket.id),
            "start_time": "2026-10-14T09:00:00", "end_time": "2026-10-14T10:30:00",
        })
        assert r.status_code == 201, r.text
        assert r.json()["customer_id"] == str(cust.id)

        summary = client.get(f"/api/support/tickets/{ticket.id}/time-entries").json()
        assert summary["total_hours"] == 1.5
        assert summary["unbilled_hours"] == 1.5

    def test_invoice_grouped_by_ticket(self, client, db):
        cust, emp, ticket = self._setup(db)
        ids = []
        for h in (9, 13):
            r = client.post("/api/backoffice/time-tracking/", json={
                "employee_id": str(emp.id), "ticket_id": str(ticket.id),
                "start_time": f"2026-10-14T{h:02d}:00:00", "end_time": f"2026-10-14T{h + 1:02d}:00:00",
            })
            ids.append(r.json()["id"])

        r = client.post("/api/backoffice/time-tracking/create-invoice", json={
            "time_entry_ids": ids, "customer_id": str(cust.id),
            "hourly_rate": "95.00", "group_by": "ticket",
        })
        assert r.status_code == 201, r.text
        inv = r.json()
        assert len(inv["line_items"]) == 1
        assert inv["line_items"][0]["description"] == f"[{ticket.ticket_number}] Drucker offline"
        assert Decimal(inv["line_items"][0]["quantity"]) == Decimal("2.00")

        db.expire_all()
        entries = db.query(TimeEntry).filter(TimeEntry.id.in_(ids)).all()
        assert all(e.is_invoiced and str(e.invoice_id) == inv["id"] for e in entries)

        # Doppelte Abrechnung verhindert
        r = client.post("/api/backoffice/time-tracking/create-invoice", json={
            "time_entry_ids": ids, "customer_id": str(cust.id), "hourly_rate": "95.00",
        })
        assert r.status_code == 422

    def test_foreign_customer_rejected(self, client, db):
        cust, emp, ticket = self._setup(db)
        other = _customer(db, "Fremdfirma")
        r = client.post("/api/backoffice/time-tracking/", json={
            "employee_id": str(emp.id), "ticket_id": str(ticket.id),
            "start_time": "2026-10-14T09:00:00", "end_time": "2026-10-14T10:00:00",
        })
        r = client.post("/api/backoffice/time-tracking/create-invoice", json={
            "time_entry_ids": [r.json()["id"]], "customer_id": str(other.id), "hourly_rate": "95.00",
        })
        assert r.status_code == 422


# ─── Kundenportal ────────────────────────────────────────────

class TestPortal:
    def _contact(self, db, cust, enabled=True, email="kunde@firma.de") -> Contact:
        c = Contact(customer_id=cust.id, firstname="Erika", lastname="Kunde", email=email, portal_enabled=enabled)
        db.add(c)
        db.commit()
        return c

    def _auth(self, contact):
        token, _ = create_session_token(contact)
        return {"Authorization": f"Bearer {token}"}

    def test_request_link_does_not_leak_existence(self, client, db):
        cust = _customer(db)
        self._contact(db, cust)
        with patch("app.modules.portal.service.send_link_mail", return_value=True) as send:
            known = client.post("/api/portal/auth/request-link", json={"email": "KUNDE@firma.de"})
            unknown = client.post("/api/portal/auth/request-link", json={"email": "nobody@x.de"})
        assert known.status_code == unknown.status_code == 202
        assert known.json() == unknown.json()
        assert send.call_count == 1
        assert "#token=" in send.call_args.args[3]

    def test_disabled_contact_gets_no_link(self, client, db):
        cust = _customer(db)
        self._contact(db, cust, enabled=False)
        with patch("app.modules.portal.service.send_link_mail") as send:
            client.post("/api/portal/auth/request-link", json={"email": "kunde@firma.de"})
        send.assert_not_called()

    def test_rate_limit(self, client, db):
        cust = _customer(db)
        self._contact(db, cust)
        with patch("app.modules.portal.service.send_link_mail", return_value=True) as send:
            for _ in range(5):
                client.post("/api/portal/auth/request-link", json={"email": "kunde@firma.de"})
        assert send.call_count == 3

    def test_verify_is_single_use_and_expires(self, client, db):
        cust = _customer(db)
        contact = self._contact(db, cust)
        db.add(PortalLoginToken(contact_id=contact.id, token_hash=hash_link_token("a" * 43),
                                expires_at=datetime.utcnow() + timedelta(minutes=5), created_at=datetime.utcnow()))
        db.add(PortalLoginToken(contact_id=contact.id, token_hash=hash_link_token("b" * 43),
                                expires_at=datetime.utcnow() - timedelta(minutes=1), created_at=datetime.utcnow()))
        db.commit()

        ok = client.post("/api/portal/auth/verify", json={"token": "a" * 43})
        assert ok.status_code == 200, ok.text
        assert ok.json()["me"]["customer_name"] == "Musterfirma GmbH"
        assert client.post("/api/portal/auth/verify", json={"token": "a" * 43}).status_code == 401
        assert client.post("/api/portal/auth/verify", json={"token": "b" * 43}).status_code == 401

    def test_portal_token_rejected_by_internal_api(self, db):
        cust = _customer(db)
        contact = self._contact(db, cust)
        app.dependency_overrides.clear()  # echte Mitarbeiter-Auth
        with TestClient(app) as c:
            r = c.get("/api/support/tickets", headers=self._auth(contact))
        assert r.status_code == 401

    def test_ticket_isolation_and_internal_comments(self, client, db):
        mine, other = _customer(db, "Meine"), _customer(db, "Andere")
        contact = self._contact(db, mine)
        t_mine = Ticket(ticket_number="TKT-000001", title="Mein Ticket", customer_id=mine.id)
        t_other = Ticket(ticket_number="TKT-000002", title="Fremd", customer_id=other.id)
        t_internal = Ticket(ticket_number="TKT-000003", title="Intern", customer_id=mine.id, type="strategic_decision")
        db.add_all([t_mine, t_other, t_internal])
        db.flush()
        db.add_all([
            TicketComment(ticket_id=t_mine.id, content="öffentlich", is_internal=False, author_id="staff"),
            TicketComment(ticket_id=t_mine.id, content="GEHEIM", is_internal=True, author_id="staff"),
        ])
        db.commit()
        h = self._auth(contact)

        items = client.get("/api/portal/tickets", headers=h).json()["items"]
        assert [t["ticket_number"] for t in items] == ["TKT-000001"]
        assert client.get(f"/api/portal/tickets/{t_other.id}", headers=h).status_code == 404
        assert client.get(f"/api/portal/tickets/{t_internal.id}", headers=h).status_code == 404

        detail = client.get(f"/api/portal/tickets/{t_mine.id}", headers=h).json()
        assert [c["content"] for c in detail["comments"]] == ["öffentlich"]

    def test_create_ticket_and_reopen_on_reply(self, client, db):
        cust = _customer(db)
        contact = self._contact(db, cust)
        h = self._auth(contact)
        r = client.post("/api/portal/tickets", headers=h, json={"title": "VPN geht nicht", "description": "Seit heute früh"})
        assert r.status_code == 201, r.text
        tid = r.json()["id"]

        db.expire_all()
        t = db.get(Ticket, uuid.UUID(tid))
        assert t.channel == "portal" and t.customer_id == cust.id and t.reporter_id == f"portal:{contact.id}"
        t.status = "resolved"
        db.commit()

        r = client.post(f"/api/portal/tickets/{tid}/comments", headers=h, json={"content": "Geht wieder nicht"})
        assert r.status_code == 201
        assert r.json()["status"] == "open"
        assert r.json()["comments"][-1]["from_customer"] is True

    def test_revoked_access_takes_effect_immediately(self, client, db):
        cust = _customer(db)
        contact = self._contact(db, cust)
        h = self._auth(contact)
        assert client.get("/api/portal/me", headers=h).status_code == 200
        contact.portal_enabled = False
        db.commit()
        assert client.get("/api/portal/me", headers=h).status_code == 401
