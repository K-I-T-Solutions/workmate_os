"""
Script: n8n API-Key erstellen
------------------------------
Legt einen neuen API-Key für n8n mit dem Scope 'email:ingest' in der DB an
und gibt den Klartext-Key einmalig auf der Konsole aus.

Ausführung (aus dem backend/-Verzeichnis):
    python scripts/create_n8n_api_key.py

Der Klartext-Key wird NUR einmal angezeigt – sicher in n8n als Credential speichern!
"""
import sys
import os
import uuid

# Projekt-Root zum PYTHONPATH hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.settings.database import SessionLocal
from app.modules.email_intake.models import ApiKey
from app.modules.email_intake.service import generate_api_key, hash_api_key


def main():
    key_name = "n8n-email-intake"
    scopes = ["email:ingest"]

    plain_key = generate_api_key()
    key_hash = hash_api_key(plain_key)

    db = SessionLocal()
    try:
        api_key = ApiKey(
            id=uuid.uuid4(),
            name=key_name,
            key_hash=key_hash,
            scopes=scopes,
            active=True,
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        print("=" * 60)
        print("API-Key erfolgreich erstellt!")
        print("=" * 60)
        print(f"Name  : {api_key.name}")
        print(f"ID    : {api_key.id}")
        print(f"Scopes: {api_key.scopes}")
        print()
        print("KLARTEXT-KEY (nur einmal sichtbar!):")
        print(f"  {plain_key}")
        print()
        print("In n8n als HTTP Header Credential hinterlegen:")
        print(f"  Name : WorkmateOS API Key")
        print(f"  Header Name  : Authorization")
        print(f"  Header Value : Bearer {plain_key}")
        print("=" * 60)
    except Exception as exc:
        db.rollback()
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
