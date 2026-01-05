#!/usr/bin/env python3
"""
Import Script: K.I.T. Solutions Produkte/Dienste

Importiert die Standardprodukte und -dienste von kit-it-koblenz.de/preise
in die Products-Tabelle.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from decimal import Decimal
from app.core.settings.database import SessionLocal
from app.modules.backoffice.products.models import Product, ProductCategory, PriceType


# ============================================================================
# PRODUKTDEFINITIONEN (basierend auf kit-it-koblenz.de/preise)
# ============================================================================

PRODUCTS = [
    # ====================
    # PRIVATKUNDEN
    # ====================
    {
        "name": "PC- und Laptop-Service",
        "short_description": "Reparatur, Wartung und Optimierung von PCs und Laptops",
        "description": "Professioneller Service für Computer und Notebooks: Hardware-Reparaturen, Software-Installation, Virenentfernung, Performance-Optimierung, Datenrettung und mehr.",
        "category": ProductCategory.PRIVATE_CUSTOMER,
        "is_service": True,
        "price_type": PriceType.HOURLY,
        "unit_price": Decimal("59.00"),
        "unit": "Stunde",
        "default_tax_rate": Decimal("19.00"),
        "sku": "PRIV-PC-SERVICE",
    },
    {
        "name": "WLAN-Einrichtung",
        "short_description": "Professionelle WLAN-Installation und -Konfiguration",
        "description": "Komplette Einrichtung Ihres WLAN-Netzwerks: Router-Installation, optimale Platzierung, Sicherheitseinstellungen, Mesh-Systeme, Reichweitenoptimierung.",
        "category": ProductCategory.PRIVATE_CUSTOMER,
        "is_service": True,
        "price_type": PriceType.FIXED,
        "unit_price": Decimal("69.00"),
        "unit": "Pauschal",
        "default_tax_rate": Decimal("19.00"),
        "sku": "PRIV-WLAN-SETUP",
    },
    {
        "name": "Datensicherung & Wiederherstellung",
        "short_description": "Backup-Lösungen und Datenrettung",
        "description": "Einrichtung automatischer Backup-Systeme, Wiederherstellung verlorener Daten, Cloud-Backup-Integration, lokale Speicherlösungen (NAS).",
        "category": ProductCategory.PRIVATE_CUSTOMER,
        "is_service": True,
        "price_type": PriceType.PROJECT,
        "unit_price": Decimal("89.00"),
        "unit": "Projekt",
        "default_tax_rate": Decimal("19.00"),
        "sku": "PRIV-DATA-BACKUP",
        "internal_notes": "Preis ab 89€, abhängig vom Umfang",
    },
    {
        "name": "Smart-Home & Streaming-Setup",
        "short_description": "Einrichtung von Smart-Home-Geräten und Streaming-Systemen",
        "description": "Installation und Konfiguration von Smart-Home-Komponenten (Beleuchtung, Heizung, Sicherheit), Streaming-Geräte (Fire TV, Apple TV, etc.), Sprachassistenten (Alexa, Google Home).",
        "category": ProductCategory.PRIVATE_CUSTOMER,
        "is_service": True,
        "price_type": PriceType.PROJECT,
        "unit_price": Decimal("79.00"),
        "unit": "Projekt",
        "default_tax_rate": Decimal("19.00"),
        "sku": "PRIV-SMARTHOME",
        "internal_notes": "Preis ab 79€",
    },
    {
        "name": "Creator-IT (Streaming, Podcasting)",
        "short_description": "IT-Setup für Content Creator",
        "description": "Spezialisierte IT-Lösungen für Content Creator: Streaming-Setup (OBS, Streamlabs), Podcast-Equipment-Konfiguration, Video-Editing-Workstations, Audio-Interface-Setup.",
        "category": ProductCategory.PRIVATE_CUSTOMER,
        "is_service": True,
        "price_type": PriceType.PROJECT,
        "unit_price": Decimal("89.00"),
        "unit": "Setup",
        "default_tax_rate": Decimal("19.00"),
        "sku": "PRIV-CREATOR-IT",
        "internal_notes": "Preis ab 89€ pro Setup",
    },

    # ====================
    # KLEINE UNTERNEHMEN
    # ====================
    {
        "name": "IT-Beratung & Netzwerkbetreuung",
        "short_description": "Professionelle IT-Beratung für kleine Unternehmen",
        "description": "Umfassende IT-Beratung: Netzwerk-Design und -Wartung, Sicherheitskonzepte, Hardware-Empfehlungen, Software-Auswahl, IT-Infrastruktur-Planung.",
        "category": ProductCategory.SMALL_BUSINESS,
        "is_service": True,
        "price_type": PriceType.HOURLY,
        "unit_price": Decimal("79.00"),
        "unit": "Stunde",
        "default_tax_rate": Decimal("19.00"),
        "sku": "SMB-IT-CONSULTING",
    },
    {
        "name": "NAS / Server Einrichtung",
        "short_description": "Installation und Konfiguration von NAS-Systemen und Servern",
        "description": "Professionelle Einrichtung von Network Attached Storage (NAS) und Servern: Hardware-Installation, RAID-Konfiguration, Benutzer-Management, Backup-Strategien, Remote-Zugriff.",
        "category": ProductCategory.SMALL_BUSINESS,
        "is_service": True,
        "price_type": PriceType.PER_UNIT,
        "unit_price": Decimal("249.00"),
        "unit": "System",
        "default_tax_rate": Decimal("19.00"),
        "sku": "SMB-NAS-SETUP",
        "internal_notes": "Preis ab 249€ pro System",
    },
    {
        "name": "Cloud / Open-Source Lösungen",
        "short_description": "Nextcloud, Vaultwarden und weitere Open-Source-Cloud-Lösungen",
        "description": "Installation und Konfiguration von Open-Source-Cloud-Plattformen: Nextcloud (Dateifreigabe, Kalender, Kontakte), Vaultwarden (Passwort-Manager), OnlyOffice, weitere Collaboration-Tools.",
        "category": ProductCategory.SMALL_BUSINESS,
        "is_service": True,
        "price_type": PriceType.PROJECT,
        "unit_price": Decimal("299.00"),
        "unit": "Projekt",
        "default_tax_rate": Decimal("19.00"),
        "sku": "SMB-CLOUD-SETUP",
        "internal_notes": "Preis ab 299€ (Nextcloud, Vaultwarden, etc.)",
    },
    {
        "name": "Creator-IT & Content-Workflows",
        "short_description": "IT-Lösungen für Content-Produktion und Workflows",
        "description": "Professionelle IT-Infrastruktur für Content-Produktion: Video-Editing-Netzwerke, Asset-Management-Systeme, Render-Farmen, Collaboration-Workflows, Streaming-Server.",
        "category": ProductCategory.SMALL_BUSINESS,
        "is_service": True,
        "price_type": PriceType.PROJECT,
        "unit_price": Decimal("149.00"),
        "unit": "Projekt",
        "default_tax_rate": Decimal("19.00"),
        "sku": "SMB-CREATOR-WORKFLOW",
        "internal_notes": "Preis ab 149€ pro Projekt",
    },
    {
        "name": "Wartung & Monitoring (monatlich)",
        "short_description": "Monatliche IT-Betreuung und Systemüberwachung",
        "description": "Kontinuierliche IT-Betreuung: Proaktives Monitoring, regelmäßige Updates, Backup-Überprüfung, Performance-Optimierung, Remote-Support, Priorisierter Support bei Störungen.",
        "category": ProductCategory.SUPPORT,
        "is_service": True,
        "price_type": PriceType.MONTHLY,
        "unit_price": Decimal("49.00"),
        "unit": "Monat",
        "default_tax_rate": Decimal("19.00"),
        "sku": "SMB-MONITORING-MONTHLY",
        "internal_notes": "Monatliche Betreuung ab 49€, nach Absprache",
    },
]


def import_products(dry_run: bool = False):
    """
    Importiert K.I.T. Solutions Standardprodukte in die Datenbank.

    Args:
        dry_run: Wenn True, werden Produkte nur angezeigt, aber nicht importiert
    """
    db = SessionLocal()

    print("=" * 80)
    print("K.I.T. SOLUTIONS - PRODUKTIMPORT")
    print("=" * 80)
    print(f"Dry Run: {dry_run}")
    print(f"Anzahl Produkte: {len(PRODUCTS)}")
    print("=" * 80)
    print()

    created_count = 0
    updated_count = 0
    skipped_count = 0

    try:
        for product_data in PRODUCTS:
            sku = product_data.get("sku")
            name = product_data.get("name")

            print(f"Verarbeite: {name} ({sku})")

            # Prüfe ob Product bereits existiert
            existing = db.query(Product).filter(Product.sku == sku).first()

            if existing:
                print(f"  ⚠️  Produkt existiert bereits (ID: {existing.id})")
                print(f"     Aktualisiere Preis: {existing.unit_price} -> {product_data['unit_price']}")

                if not dry_run:
                    # Update existing product
                    for key, value in product_data.items():
                        if key != "sku":  # SKU nicht ändern
                            setattr(existing, key, value)
                    updated_count += 1
                else:
                    print(f"  [DRY RUN] Würde aktualisieren")
                skipped_count += 1
            else:
                print(f"  ✓ Neu erstellt")
                print(f"     Preis: {product_data['unit_price']} € ({product_data['price_type'].value})")
                print(f"     Kategorie: {product_data['category'].value}")

                if not dry_run:
                    product = Product(**product_data)
                    db.add(product)
                    created_count += 1
                else:
                    print(f"  [DRY RUN] Würde erstellen")

            print()

        if not dry_run:
            db.commit()
            print("✅ Datenbank-Commit erfolgreich")
        else:
            print("ℹ️  DRY RUN - Keine Änderungen in der Datenbank")

        print()
        print("=" * 80)
        print("ZUSAMMENFASSUNG")
        print("=" * 80)
        print(f"Neu erstellt: {created_count}")
        print(f"Aktualisiert: {updated_count}")
        print(f"Übersprungen: {skipped_count}")
        print("=" * 80)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Importiert K.I.T. Solutions Standardprodukte"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Zeigt nur an, was importiert würde, ohne Änderungen vorzunehmen",
    )

    args = parser.parse_args()

    import_products(dry_run=args.dry_run)
