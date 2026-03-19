"""
Tests für das Email Intake Modul
----------------------------------
Testet POST /api/v1/email/ingest:
- Neuer Kontakt → Ticket + Contact angelegt
- Bekannte E-Mail → Contact gematcht (kein Duplikat)
- Falscher API-Key → 401
- Pro Mailbox-Typ → korrekter ticket_type
"""
from __future__ import annotations

import json
import uuid
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.settings.database import Base, get_db
from app.main import app
from app.modules.email_intake.models import ApiKey, EmailContact, EmailTicket
from app.modules.email_intake.service import generate_api_key, hash_api_key

# ---------------------------------------------------------------------------
# Test-Datenbank (SQLite In-Memory)
# ---------------------------------------------------------------------------

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(bind=engine_test, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Erstellt alle Tabellen in der Test-DB."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """Stellt eine Test-DB-Session bereit und rollt nach jedem Test zurück."""
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db: Session) -> TestClient:
    """FastAPI TestClient mit overridem get_db (Test-DB)."""
    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _seed_api_key(db: Session, scopes: list[str] | None = None) -> str:
    """Legt einen API-Key in der Test-DB an und gibt den Klartext zurück."""
    plain_key = generate_api_key()
    api_key = ApiKey(
        id=uuid.uuid4(),
        name="test-n8n-key",
        key_hash=hash_api_key(plain_key),
        scopes=scopes or ["email:ingest"],
        active=True,
    )
    db.add(api_key)
    db.commit()
    return plain_key


def _ingest_payload(mailbox: str = "support", email: str = "test@example.com") -> dict:
    return {
        "subject": f"Test via {mailbox}",
        "body": "Hallo, das ist ein Test.",
        "from_email": email,
        "from_name": "Test User",
        "mailbox": mailbox,
    }


# ---------------------------------------------------------------------------
# Tests: POST /api/v1/email/ingest
# ---------------------------------------------------------------------------

class TestEmailIngest:
    ENDPOINT = "/api/v1/email/ingest"

    def test_new_contact_creates_ticket_and_contact(self, client: TestClient, db: Session):
        """Neuer Kontakt: Ticket UND Kontakt werden angelegt, contact_created=True."""
        key = _seed_api_key(db)
        resp = client.post(
            self.ENDPOINT,
            json=_ingest_payload(mailbox="support", email="neu@example.com"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()

        assert data["contact_created"] is True
        assert data["ticket_type"] == "support"
        assert data["status"] == "open"
        assert data["ticket_id"] is not None
        assert data["contact_id"] is not None

        # DB-Check
        ticket = db.query(EmailTicket).filter(EmailTicket.id == data["ticket_id"]).first()
        assert ticket is not None
        assert ticket.from_email == "neu@example.com"

        contact = db.query(EmailContact).filter(
            EmailContact.id == uuid.UUID(data["contact_id"])
        ).first()
        assert contact is not None
        assert contact.email == "neu@example.com"

    def test_known_email_matches_existing_contact(self, client: TestClient, db: Session):
        """Bekannte E-Mail: Kein Duplikat – contact_created=False."""
        key = _seed_api_key(db)

        # Erster Ingest: Kontakt anlegen
        resp1 = client.post(
            self.ENDPOINT,
            json=_ingest_payload(email="wiederkehrend@example.com"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp1.status_code == 201
        contact_id_1 = resp1.json()["contact_id"]

        # Zweiter Ingest: gleiche E-Mail
        resp2 = client.post(
            self.ENDPOINT,
            json=_ingest_payload(email="wiederkehrend@example.com"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp2.status_code == 201
        data2 = resp2.json()

        assert data2["contact_created"] is False
        assert data2["contact_id"] == contact_id_1  # gleicher Kontakt!

        # Nur ein Contact in der DB
        count = db.query(EmailContact).filter(
            EmailContact.email == "wiederkehrend@example.com"
        ).count()
        assert count == 1

    def test_invalid_api_key_returns_401(self, client: TestClient, db: Session):
        """Falscher API-Key → HTTP 401."""
        resp = client.post(
            self.ENDPOINT,
            json=_ingest_payload(),
            headers={"Authorization": "Bearer ungueltig_xyz123"},
        )
        assert resp.status_code == 401

    def test_missing_api_key_returns_401(self, client: TestClient, db: Session):
        """Kein Authorization-Header → HTTP 401."""
        resp = client.post(self.ENDPOINT, json=_ingest_payload())
        assert resp.status_code == 401

    def test_mailbox_support_creates_support_ticket(self, client: TestClient, db: Session):
        """mailbox=support → ticket_type='support'."""
        key = _seed_api_key(db)
        resp = client.post(
            self.ENDPOINT,
            json=_ingest_payload(mailbox="support", email="a@example.com"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 201
        assert resp.json()["ticket_type"] == "support"

    def test_mailbox_kontakt_creates_anfrage_ticket(self, client: TestClient, db: Session):
        """mailbox=kontakt → ticket_type='anfrage'."""
        key = _seed_api_key(db)
        resp = client.post(
            self.ENDPOINT,
            json=_ingest_payload(mailbox="kontakt", email="b@example.com"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 201
        assert resp.json()["ticket_type"] == "anfrage"

    def test_mailbox_info_creates_info_ticket(self, client: TestClient, db: Session):
        """mailbox=info → ticket_type='info'."""
        key = _seed_api_key(db)
        resp = client.post(
            self.ENDPOINT,
            json=_ingest_payload(mailbox="info", email="c@example.com"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 201
        assert resp.json()["ticket_type"] == "info"

    def test_invalid_mailbox_returns_422(self, client: TestClient, db: Session):
        """Ungültige mailbox → HTTP 422 (Validierungsfehler)."""
        key = _seed_api_key(db)
        payload = _ingest_payload()
        payload["mailbox"] = "unbekannt"
        resp = client.post(
            self.ENDPOINT,
            json=payload,
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 422

    def test_api_key_without_scope_returns_401(self, client: TestClient, db: Session):
        """API-Key ohne 'email:ingest'-Scope → HTTP 401."""
        # Key mit anderem Scope
        key = _seed_api_key(db, scopes=["other:scope"])
        resp = client.post(
            self.ENDPOINT,
            json=_ingest_payload(email="d@example.com"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 401

    def test_html_body_is_converted_to_plaintext(self, client: TestClient, db: Session):
        """HTML-Body wird zu Plaintext konvertiert (kein roher HTML im Ticket)."""
        key = _seed_api_key(db)
        html_body = "<p>Hallo <strong>Welt</strong>, das ist <a href='#'>ein Link</a>.</p>"
        payload = {
            "subject": "HTML-Test",
            "body": html_body,
            "from_email": "html@example.com",
            "from_name": "HTML User",
            "mailbox": "support",
        }
        resp = client.post(
            self.ENDPOINT,
            json=payload,
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 201
        ticket_id = resp.json()["ticket_id"]

        ticket = db.query(EmailTicket).filter(EmailTicket.id == ticket_id).first()
        assert ticket is not None
        # Kein HTML-Tag im gespeicherten Body
        assert "<p>" not in (ticket.body or "")
        assert "<strong>" not in (ticket.body or "")
