# GitHub Actions CI/CD Setup

## Übersicht

Dieses Repository nutzt GitHub Actions für automatisches Deployment:

- **main Branch**: Automatisches Deployment zu Production (workmate-01)
- **Pull Requests**: Build-Tests ohne Deployment
- **dev Branch**: Entwicklungs-Branch für neue Features

## GitHub Secrets konfigurieren

Gehe zu: **Settings → Secrets and variables → Actions → New repository secret**

### Erforderliche Secrets:

#### 1. SSH_PRIVATE_KEY
SSH-Schlüssel für Deployment auf workmate-01:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCxfQ8u8GwiNP0nMnKyGdyloO2aXxzQyuI272X3aMo5SQAAAKh/LObAfyzm
wAAAAAtzc2gtZWQyNTUxOQAAACCxfQ8u8GwiNP0nMnKyGdyloO2aXxzQyuI272X3aMo5SQ
AAAECMCw3PGnBrdLm1EL9XjLJaUZiaPDNzUSx0vJ3i33qNZrF9Dy7wbCI0/ScycrIZ3KWg
7ZpfHNDK4jbvZfdoyjlJAAAAHmdpdGh1Yi1hY3Rpb25zQHdvcmttYXRlLWRlcGxveQECAw
QFBgc=
-----END OPENSSH PRIVATE KEY-----
```

#### 2. POSTGRES_PASSWORD
```
XgCEMufwJIO9o9rEyH3QwEUaXa4rSC/NdTK81MvaG/A=
```

#### 3. SECRET_KEY
```
zNEb8xEHnldn4rfDhyQfhEXavxXz6Q9uc4p5lDy5h7E=
```

#### 4. JWT_SECRET_KEY
```
BoWDURcg1ADir8WiGvfmhxY4E9nzIWQPGVs/17WJGCM=
```

#### 5. NEXTCLOUD_URL
```
https://cloud.kit-it-koblenz.de/remote.php/dav/files/workmate-storage
```

#### 6. NEXTCLOUD_USER
```
workmate-storage
```

#### 7. NEXTCLOUD_PASSWORD
```
workmate123!
```

#### 8. ACME_EMAIL
```
admin@kit-it-koblenz.de
```

#### 9. TRAEFIK_DASHBOARD_AUTH
```
admin:$$2y$$05$$gturxsFaCJQKllmsXQCghO4wovoF7FJSHr0sOAE4kLFUaTzn9baZW
```

**WICHTIG**: Bei `TRAEFIK_DASHBOARD_AUTH` müssen alle `$` als `$$` geschrieben werden für GitHub Actions!

## Workflow-Beschreibung

### Production Deployment (`.github/workflows/deploy-production.yml`)

Wird ausgeführt bei:
- Push auf `main` Branch
- Manueller Trigger über GitHub UI

Schritte:
1. Code auschecken
2. SSH-Verbindung einrichten
3. Files auf workmate-01 syncen
4. `.env.prod` aus Secrets erstellen
5. Docker Images bauen
6. Container neu starten
7. Health-Check durchführen

### Pull Request Tests (`.github/workflows/test-pr.yml`)

Wird ausgeführt bei:
- Pull Requests zu `main`

Schritte:
1. Backend Docker Build testen
2. Frontend Build testen
3. Ergebnis-Summary

## Workflow verwenden

### Neues Feature entwickeln:
```bash
# Dev-Branch auschecken
git checkout dev

# Feature entwickeln
git add .
git commit -m "feat: new feature"
git push origin dev

# Pull Request erstellen: dev → main
# Nach Merge: Automatisches Deployment!
```

### Hotfix:
```bash
# Direkt auf main (nur für Notfälle!)
git checkout main
git add .
git commit -m "fix: critical bug"
git push origin main
# → Automatisches Deployment
```

### Manuelles Deployment triggern:
1. Gehe zu **Actions** Tab auf GitHub
2. Wähle **Deploy to Production**
3. Klicke **Run workflow**

## SSH-Key auf Server

Der Public Key wurde bereits auf workmate-01 hinzugefügt:
```
~/.ssh/authorized_keys
```

Falls nötig, kann der Key überprüft werden mit:
```bash
ssh workmate-01 "tail -1 ~/.ssh/authorized_keys"
```

## Troubleshooting

### Deployment schlägt fehl
1. Prüfe GitHub Actions Logs
2. SSH auf workmate-01 und prüfe Docker logs:
   ```bash
   cd /opt/workmate/infra
   docker compose -f docker-compose.prod.yml logs
   ```

### Health-Check schlägt fehl
- Backend: `ssh workmate-01 "docker logs workmate_backend"`
- Frontend: `ssh workmate-01 "docker logs workmate_frontend"`
- Traefik: `ssh workmate-01 "docker logs workmate_traefik"`

### SSH-Verbindung schlägt fehl
- Prüfe ob SSH_PRIVATE_KEY korrekt in GitHub Secrets eingetragen ist
- Prüfe Server-Erreichbarkeit: `ssh workmate-01`
