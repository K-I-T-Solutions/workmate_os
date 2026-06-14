# Daily Report — 2026-06-14

**Projekt:** WorkmateOS / Infrastruktur  
**Autor:** Joshua Kuhrau  
**Server:** file-01 (Nextcloud), workmate-01 (WorkmateOS)

---

## Zusammenfassung

Nextcloud auf file-01 von Version 31 auf 33 aktualisiert (zweistufig via 32). Anschließend WorkmateOS auf Nextcloud als Dokument-Storage umgestellt und erfolgreich getestet.

---

## Erledigte Aufgaben

### Nextcloud Update: 31 → 32 → 33

Nextcloud lief als Docker-Container mit `nextcloud:stable`. Beim direkten Pull auf `stable` (33.0.5) schlug der Start fehl:

> `Can't start Nextcloud because upgrading from 31.0.9.1 to 33.0.5.1 is not supported.`

Nextcloud erlaubt nur ein Major-Version-Upgrade auf einmal. Lösung: Zweistufiges Upgrade.

**Schritt 1 — 31 → 32:**
- `docker-compose.yml` auf `nextcloud:32` geändert
- `docker compose up -d --pull always app`
- `occ upgrade` ausgeführt → erfolgreich auf **32.0.11**

**Schritt 2 — 32 → 33:**
- `docker-compose.yml` zurück auf `nextcloud:stable`
- `docker compose up -d --pull always app`
- `occ upgrade` ausgeführt → erfolgreich auf **33.0.5**

**Seiteneffekt:** App `mail` wurde beim Upgrade auf 33 deaktiviert (inkompatibel laut Upgrade-Log). Nach `occ app:disable mail && occ app:enable mail` wieder aktiv (Version 5.9.2, kompatibel mit NC 33).

**Alle Apps aktuell:** `occ app:update --all` — keine Updates verfügbar.

---

### Verbindungscheck workmate-01 ↔ file-01

| Richtung | Latenz | HTTP |
|---|---|---|
| file-01 → workmate-01 | ~24ms | 307 OK |
| workmate-01 → file-01 | ~10ms | 200 OK |

0% Paketverlust, beide Server im gleichen Hetzner-RZ. ICMP direkt auf IP geblockt (Firewall), HTTP/HTTPS einwandfrei.

---

### WorkmateOS — Nextcloud Storage-Integration aktiviert

Die Nextcloud-Storage-Integration war bereits vollständig im Backend implementiert (`backend/app/core/storage/nextcloud.py`, WebDAV via `webdav3`). In Production war jedoch `STORAGE_BACKEND=local` gesetzt.

**Geprüft:**
- Nextcloud-Serviceuser `workmate-storage` auf `cloud.kit-it-koblenz.de` existiert
- WebDAV-Verbindung mit Credentials funktioniert (HTTP 200)
- Verzeichnis `workmate/` im User-Root vorhanden

**Änderungen in `/srv/workmate/env/.env.prod`:**
```
STORAGE_BACKEND=nextcloud
NEXTCLOUD_URL=https://cloud.kit-it-koblenz.de/remote.php/dav/files/workmate-storage
NEXTCLOUD_USER=workmate-storage
NEXTCLOUD_PASSWORD=workmate123!
NEXTCLOUD_BASE_PATH=workmate
```

**Deployment:** Backend-Container neu gestartet via `docker compose --env-file ../env/.env.prod up -d backend`

**Integrationstest erfolgreich:**
- Upload: `workmate/test/connection-check.txt` → OK
- Download: Inhalt korrekt zurückgegeben → OK
- Delete: Datei entfernt → OK

**Hinweis:** Bestehende lokal gespeicherte Dokumente wurden nicht migriert — sie bleiben auf workmate-01. Nur neue Uploads gehen ab sofort nach Nextcloud.

---

## Offene Punkte

- Passwort `workmate123!` für `workmate-storage` sollte durch ein sicheres Passwort ersetzt werden
- Migration bestehender lokaler Dokumente nach Nextcloud (falls gewünscht)

---

## Status

**Nextcloud:** 33.0.5 — live auf `cloud.kit-it-koblenz.de`  
**WorkmateOS Storage:** Nextcloud aktiv — neue Dokumente werden auf `cloud.kit-it-koblenz.de/workmate/` gespeichert
