# Branch Protection Setup - Business Level

## 🔒 Empfohlene Branch Protection Rules

**Hinweis:** Branch Protection Rules für private Repos erfordern GitHub Pro oder ein Public Repository.

---

## Option 1: Repository Public machen (Kostenlos)

Wenn das Projekt Open Source werden soll:

```bash
# Via GitHub Web UI:
Settings → General → Danger Zone → Change repository visibility → Public
```

**Vorteile:**
- ✅ Kostenlose Branch Protection
- ✅ Mehr Visibility für K.I.T. Solutions
- ✅ Community Contributions möglich

**Nachteile:**
- ⚠️ Code ist öffentlich sichtbar
- ⚠️ Secrets müssen noch besser geschützt werden

---

## Option 2: GitHub Pro Upgrade ($4/Monat)

```bash
# Via GitHub Web UI:
Settings → Billing → Change plan → GitHub Pro
```

**Vorteile:**
- ✅ Privates Repo bleibt privat
- ✅ Advanced Security Features
- ✅ Protected Branches
- ✅ Code Owners
- ✅ Multiple Reviewers

---

## 🛡️ Empfohlene Branch Protection Settings

### Main Branch (Production)

Nach Aktivierung über GitHub UI: **Settings → Branches → Add branch protection rule**

**Branch name pattern:** `main`

**Settings:**
```
☑ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Dismiss stale pull request approvals when new commits are pushed
  ☑ Require review from Code Owners (optional)

☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
  Status checks:
    - ☑ Test Pull Request (workflow)
    - ☑ Build Backend
    - ☑ Build Frontend

☑ Require conversation resolution before merging

☑ Require linear history (optional - bevorzugt merge commits)

☐ Allow force pushes (DEAKTIVIERT für main!)
☐ Allow deletions (DEAKTIVIERT für main!)

☐ Do not allow bypassing the above settings (für Teams mit mehreren Devs)
```

---

### Dev Branch (Development)

**Branch name pattern:** `dev`

**Settings (lockerer):**
```
☑ Require a pull request before merging (optional)
  ☑ Require approvals: 0 (oder 1 für Teams)

☐ Require status checks (optional für dev)

☐ Allow force pushes (nur wenn nötig)
☐ Allow deletions
```

---

## 📋 Git Workflow - Business Standard

### Branch-Struktur

```
main (protected)
  ├─ Production Branch
  ├─ Automatisches Deployment zu workmate.kit-it-koblenz.de
  └─ Nur via Pull Request von dev

dev
  ├─ Development Branch
  ├─ Sammelt Features vor Production-Release
  └─ Basis für Feature-Branches

feature/*
  ├─ Neue Features entwickeln
  ├─ Beispiel: feature/user-notifications
  └─ Pull Request zu dev

hotfix/*
  ├─ Kritische Bugfixes für Production
  ├─ Beispiel: hotfix/security-patch
  └─ Pull Request direkt zu main (Notfall)

release/*
  ├─ Release-Vorbereitung
  ├─ Beispiel: release/v1.1.0
  └─ Pull Request zu main + tag
```

---

## 🚀 Workflow-Beispiele

### 1. Neues Feature entwickeln

```bash
# Feature-Branch von dev erstellen
git checkout dev
git pull origin dev
git checkout -b feature/user-profile

# Entwickeln, committen, pushen
git add .
git commit -m "feat: add user profile page"
git push origin feature/user-profile

# Pull Request erstellen: feature/user-profile → dev
gh pr create --base dev --head feature/user-profile \
  --title "Add user profile page" \
  --body "Implements user profile with settings"

# Nach Approval: Merge
# Nach Merge: Feature-Branch löschen
git branch -d feature/user-profile
git push origin --delete feature/user-profile
```

---

### 2. Release zu Production

```bash
# Von dev zu main mergen
git checkout dev
git pull origin dev

# Pull Request erstellen: dev → main
gh pr create --base main --head dev \
  --title "Release v1.1.0" \
  --body "$(cat <<EOF
## Release v1.1.0

### Features
- User profile page
- Notification system
- Export functionality

### Bugfixes
- Fixed login timeout
- Corrected date formatting

### Deployment
This PR will trigger automatic deployment to production.
EOF
)"

# Nach Approval: Merge
# Automatisches Deployment startet!

# Release-Tag erstellen
git checkout main
git pull origin main
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# Dev mit main synchronisieren
git checkout dev
git merge main
git push origin dev
```

---

### 3. Hotfix für Production

```bash
# Hotfix-Branch von main erstellen
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# Fix entwickeln
git add .
git commit -m "fix: patch critical security vulnerability"
git push origin hotfix/critical-security-fix

# Pull Request direkt zu main (Notfall!)
gh pr create --base main --head hotfix/critical-security-fix \
  --title "🚨 CRITICAL: Security patch" \
  --body "Security vulnerability fix - needs immediate deployment"

# Nach Approval: Merge zu main
# Automatisches Deployment!

# Hotfix auch in dev mergen
git checkout dev
git merge main
git push origin dev
```

---

## 🔐 Code Review Guidelines

### Für Reviewer:

**Prüfen:**
- ✅ Code-Qualität und Lesbarkeit
- ✅ Tests vorhanden und erfolgreich
- ✅ Keine Secrets im Code
- ✅ Keine Breaking Changes (ohne Migration)
- ✅ Dokumentation aktualisiert
- ✅ Performance-Implikationen

**Ablehnen wenn:**
- ❌ Tests schlagen fehl
- ❌ Code-Style nicht eingehalten
- ❌ Sicherheitslücken erkennbar
- ❌ Keine Beschreibung im PR

### Für PR Ersteller:

**PR Template (empfohlen):**
```markdown
## Beschreibung
Was ändert dieser PR?

## Art der Änderung
- [ ] Bugfix
- [ ] Neues Feature
- [ ] Breaking Change
- [ ] Dokumentation

## Checklist
- [ ] Tests hinzugefügt/aktualisiert
- [ ] Dokumentation aktualisiert
- [ ] Keine Secrets im Code
- [ ] Lokal getestet
- [ ] CI/CD Tests erfolgreich

## Screenshots (falls UI-Änderungen)
[Screenshots hier]
```

---

## 📊 Monitoring & Rollback

### Deployment überwachen

```bash
# GitHub Actions Status checken
gh run list --limit 5

# Logs vom letzten Run
gh run view --log

# Production Health Check
curl https://api.workmate.kit-it-koblenz.de/system/health
```

### Rollback bei Problemen

```bash
# Option 1: Revert Commit auf main
git checkout main
git revert HEAD
git push origin main
# → Automatisches Deployment mit altem Stand

# Option 2: Zu vorherigem Tag zurück
git checkout main
git reset --hard v1.0.0
git push origin main --force
# ⚠️ Nur im Notfall! Force-Push sollte vermieden werden
```

---

## 🎯 Best Practices

### Commit Messages

Folge [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user profile page
fix: correct date formatting in dashboard
docs: update API documentation
chore: bump version to 1.1.0
refactor: simplify authentication logic
test: add tests for user service
style: format code with prettier
perf: optimize database queries
```

### Branch Naming

```
feature/user-profile
feature/notification-system
bugfix/login-timeout
hotfix/security-patch
release/v1.1.0
docs/api-documentation
```

### Pull Request Size

- ✅ Klein: 1-200 Zeilen (ideal)
- ⚠️ Mittel: 200-500 Zeilen (ok)
- ❌ Groß: 500+ Zeilen (aufteilen!)

**Regel:** Ein PR = Ein Feature/Fix

---

## 🔄 Automatisierung

### GitHub Actions Workflows

**Bereits vorhanden:**
- ✅ `deploy-production.yml` - Auto-Deploy bei Push auf main
- ✅ `test-pr.yml` - Build-Tests für PRs

**Empfohlen:**
- [ ] `auto-sync-dev.yml` - Auto-Sync dev mit main nach Merge
- [ ] `label-pr.yml` - Automatisches Labeling von PRs
- [ ] `stale.yml` - Alte PRs/Issues automatisch schließen
- [ ] `release.yml` - Automatische Release Notes generieren

---

## 📚 Weitere Ressourcen

- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

## 🎓 Team Onboarding

Für neue Team-Mitglieder:

1. **Repository clonen**
   ```bash
   git clone git@github.com:K-I-T-Solutions/workmate_os.git
   cd workmate_os
   ```

2. **Development Setup**
   ```bash
   # README.md Entwicklungs-Sektion folgen
   make dev-up
   ```

3. **Ersten Feature-Branch erstellen**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/mein-erstes-feature
   ```

4. **Workflow lernen**
   - Diese Dokumentation lesen
   - Einen Test-PR erstellen
   - Code Review Prozess durchlaufen

---

*Erstellt: 24.12.2024*
*K.I.T. Solutions - Professional Git Workflow*
