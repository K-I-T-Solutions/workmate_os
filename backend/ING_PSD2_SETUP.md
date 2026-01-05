# ING PSD2 API Setup Guide

## Übersicht

WorkmateOS unterstützt jetzt die **ING PSD2 Open Banking API** mit mTLS-Authentifizierung!

**Was ist implementiert:**
- ✅ mTLS (mutual TLS) mit QWAC/QSealC Zertifikaten
- ✅ OAuth2 Authorization Code Flow
- ✅ Account Information Service (AIS)
- ✅ Automatische Transaction-Synchronisation
- ✅ Auto-Reconciliation mit Invoices

**API Endpoints:**
- `POST /api/backoffice/finance/psd2/consent/initiate` - OAuth2 Consent starten
- `POST /api/backoffice/finance/psd2/consent/callback` - Access Token holen
- `POST /api/backoffice/finance/psd2/accounts/sync` - Konten synchronisieren
- `POST /api/backoffice/finance/psd2/transactions/sync` - Transaktionen importieren

---

## Schritt 1: ING Developer Portal Setup

### 1.1 Account erstellen
1. Gehe zu https://developer.ing.com
2. Klicke auf **"Sign Up"**
3. Registriere dich mit E-Mail + Passwort
4. Bestätige deine E-Mail

### 1.2 Application registrieren
1. Login auf https://developer.ing.com
2. Gehe zu **"My Apps"**
3. Klicke **"Create new app"**
4. Fülle aus:
   - **App Name**: WorkmateOS (oder dein Wunschname)
   - **Redirect URI**: `http://localhost:5173/banking/callback` (für Development)
   - **Environment**: Sandbox
   - **API Products**: Account Information (PSD2)

5. Nach Erstellung erhältst du:
   - ✅ **Client ID** (z.B. `178e56d7-576a-43f0-a45e-c3e2d150ef4c`)
   - ℹ️  **Kein Client Secret** (wird durch Zertifikate ersetzt!)

---

## Schritt 2: Test-Zertifikate herunterladen

### 2.1 Zertifikate von ING Developer Portal
1. Gehe zu deiner App im Developer Portal
2. Klicke auf **"Certificates"** Tab
3. Download **Sandbox Certificates**:
   - `example_client_tls.cer` (QWAC - für TLS)
   - `example_client_tls.key` (Private Key für QWAC)
   - `example_client_signing.cer` (QSealC - für Signing)
   - `example_client_signing.key` (Private Key für QSealC)

### 2.2 Zertifikate in WorkmateOS speichern

Erstelle Verzeichnis:
```bash
mkdir -p backend/certificates/psd2
```

Kopiere Zertifikate:
```bash
# Sandbox Test-Zertifikate
cp ~/Downloads/example_client_tls.cer backend/certificates/psd2/
cp ~/Downloads/example_client_tls.key backend/certificates/psd2/
cp ~/Downloads/example_client_signing.cer backend/certificates/psd2/
cp ~/Downloads/example_client_signing.key backend/certificates/psd2/
```

**Wichtig:**
- Zertifikate NIE ins Git committen!
- `.gitignore` sollte `certificates/` enthalten

---

## Schritt 3: Konfiguration

### 3.1 Environment Variables (optional)
```bash
# .env
PSD2_CLIENT_ID=178e56d7-576a-43f0-a45e-c3e2d150ef4c
PSD2_ENVIRONMENT=sandbox
PSD2_CERT_PATH=/absolute/path/to/certificates/psd2
```

### 3.2 Zertifikat-Pfade prüfen
Die Pfade sind in `psd2_integration.py` konfiguriert:
```python
CERT_PATH_QWAC = "certificates/psd2/example_client_tls.cer"
CERT_PATH_QWAC_KEY = "certificates/psd2/example_client_tls.key"
CERT_PATH_QSEALC = "certificates/psd2/example_client_signing.cer"
CERT_PATH_QSEALC_KEY = "certificates/psd2/example_client_signing.key"
```

Falls abweichend, passe die Pfade an!

---

## Schritt 4: API Testen

### 4.1 Consent Flow starten
```bash
curl -X POST "http://localhost:8000/api/backoffice/finance/psd2/consent/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "178e56d7-576a-43f0-a45e-c3e2d150ef4c",
    "redirect_uri": "http://localhost:5173/banking/callback",
    "scope": "payment-accounts:balances:view payment-accounts:transactions:view"
  }'
```

**Response:**
```json
{
  "authorization_url": "https://api.sandbox.ing.com/oauth2/authorize?client_id=...",
  "state": "abc-123-xyz"
}
```

### 4.2 User Consent (manuell)
1. Öffne `authorization_url` im Browser
2. Login mit ING Sandbox-Testdaten:
   - **Username**: `ING_TEST_USER`
   - **Password**: `ING_TEST_PASS`
3. Gib Consent (Klick auf "Allow")
4. Du wirst zu `redirect_uri` weitergeleitet mit `?code=AUTHORIZATION_CODE`

### 4.3 Access Token holen
```bash
curl -X POST "http://localhost:8000/api/backoffice/finance/psd2/consent/callback" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "178e56d7-576a-43f0-a45e-c3e2d150ef4c",
    "authorization_code": "AUTHORIZATION_CODE_FROM_REDIRECT",
    "redirect_uri": "http://localhost:5173/banking/callback"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 7776000,
  "refresh_token": "...",
  "scope": "payment-accounts:balances:view payment-accounts:transactions:view"
}
```

**Wichtig:** `access_token` sicher speichern (gültig 90 Tage)!

### 4.4 Konten synchronisieren
```bash
curl -X POST "http://localhost:8000/api/backoffice/finance/psd2/accounts/sync?create_missing=true" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "178e56d7-576a-43f0-a45e-c3e2d150ef4c",
    "access_token": "eyJhbGc..."
  }'
```

**Response:**
```json
{
  "success": true,
  "accounts_synced": 2,
  "accounts": [
    {
      "account": {
        "id": "...",
        "iban": "DE33500105176000299030",
        "account_name": "ING Geschäftskonto",
        "bank_name": "ING",
        "currency": "EUR"
      },
      "created": true
    }
  ]
}
```

### 4.5 Transaktionen synchronisieren
```bash
curl -X POST "http://localhost:8000/api/backoffice/finance/psd2/transactions/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "178e56d7-576a-43f0-a45e-c3e2d150ef4c",
    "access_token": "eyJhbGc...",
    "account_id": "WORKMATEOS_ACCOUNT_UUID",
    "psd2_account_id": "ING_RESOURCE_ID",
    "date_from": "2025-01-01",
    "date_to": "2026-01-02",
    "skip_duplicates": true,
    "auto_reconcile": true
  }'
```

**Response:**
```json
{
  "success": true,
  "imported": 42,
  "skipped": 3,
  "auto_reconciled": 15,
  "total_fetched": 45
}
```

---

## Schritt 5: Production Setup (Optional)

Für **Production** (echte ING Konten) brauchst du:

### 5.1 Echte eIDAS-Zertifikate kaufen
**Anbieter (QTSP - Qualified Trust Service Providers):**
- **CERTEU** (https://certeu.com) - ~300€/Jahr
- **GlobalSign** - ~500€/Jahr
- **SwissSign** - ~400€/Jahr

**Was du brauchst:**
- Firmendaten (Handelsregister, USt-ID)
- 2 Zertifikate:
  - QWAC (Qualified Web Authentication Certificate)
  - QSealC (Qualified Electronic Seal Certificate)

### 5.2 Zertifikate bei ING registrieren
1. ING Developer Portal → App → Production
2. Upload QWAC + QSealC Zertifikate
3. Warte auf Freigabe (~1-2 Werktage)

### 5.3 Environment auf Production umstellen
```python
# In psd2_integration.py oder via ENV
credentials = PSD2Credentials(
    client_id=your_client_id,
    environment="production",  # <- Hier umstellen
)
```

---

## Troubleshooting

### Problem: "Certificate error: [Errno 2] No such file or directory"
**Lösung:** Zertifikate wurden nicht heruntergeladen oder Pfad ist falsch.
```bash
# Prüfe ob Zertifikate existieren
ls -la backend/certificates/psd2/
```

### Problem: "SSL: CERTIFICATE_VERIFY_FAILED"
**Lösung:** QWAC-Zertifikat ist nicht von ING signiert (nur für Sandbox).
- Sandbox: ING stellt Test-Zertifikate bereit
- Production: Kaufe echte eIDAS-Zertifikate

### Problem: "Invalid authorization_code"
**Lösung:** Code ist abgelaufen (10 Minuten Gültigkeit).
- Starte Consent Flow neu
- Rufe Callback schneller auf

### Problem: "Token expired"
**Lösung:** Access Token ist abgelaufen (90 Tage Gültigkeit).
- Nutze Refresh Token: `POST /oauth2/token` mit `grant_type=refresh_token`
- Oder: Starte Consent Flow neu

---

## Weitere Infos

**ING Developer Portal:**
- https://developer.ing.com

**PSD2 Standards:**
- https://www.berlin-group.org/nextgenpsd2-downloads

**Support:**
- ING Developer Support: developer-support@ing.com
- WorkmateOS: GitHub Issues

---

## Nächste Schritte

1. ✅ Backend PSD2 Integration - FERTIG!
2. ⏳ Banking Module UI erstellen
3. ⏳ Consent Flow in UI einbauen
4. ⏳ Transaction-Sync-UI mit Auto-Reconciliation

Happy Banking! 🏦
