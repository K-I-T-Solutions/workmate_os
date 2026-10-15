# WorkmateOS — Aufgaben-Backlog

Offene Themen und Aufgaben die noch besprochen oder umgesetzt werden müssen.

---

## 📚 Dokumentation

- [ ] **Docs-Strategie überdenken** — Grundlegende Fragen zu Pflege, Zugang und Hosting → [Discussion #130](https://github.com/orgs/K-I-T-Solutions/discussions/130)
- [ ] **Debug-Logging deaktivieren** — `ACTIONS_STEP_DEBUG` Secret entfernen → [#126](https://github.com/K-I-T-Solutions/workmate_os/issues/126)

---

## 🔒 Security

- [ ] Nextcloud-Serviceuser `workmate-storage` Passwort durch sicheres ersetzen (aktuell `workmate123!`) → [#127](https://github.com/K-I-T-Solutions/workmate_os/issues/127)

---

## 🚀 Features (Phase 5)

- [ ] Banking API / Elster-Anbindung → [#129](https://github.com/K-I-T-Solutions/workmate_os/issues/129)
- [ ] Stripe Zahlungsstatus-Tracking und Webhook-Verarbeitung vervollständigen → [#128](https://github.com/K-I-T-Solutions/workmate_os/issues/128)
- [ ] Mobile App

---

## 🧾 v5.0 – Nacharbeiten

- [ ] n8n-Workflow `n8n/contracts_billing_workflow.json` importieren, API-Key (`contracts:billing,assets:read`) anlegen, Empfänger-Adresse setzen, aktivieren
- [ ] `PORTAL_BASE_URL` in `infra/.env.prod` setzen (Default: `https://workmate.kit-it-koblenz.de`)
- [ ] Inklusiv-Stunden aus Wartungsverträgen bei der Ticket-Abrechnung automatisch verrechnen (derzeit nur Info am Vertrag)
- [ ] Anteilige Abrechnung (Pro-rata) bei Vertragsende mitten im Zeitraum
- [ ] Kundenportal erweitern: Rechnungen, Verträge, Geräte (read-only)
- [ ] E-Mail an Support bei neuem Portal-Ticket / an Kunde bei Antwort im Ticket
- [ ] Rollen: `backoffice.contracts.*` / `backoffice.assets.*` für CTO/CFO in Keycloak-Rollenkonzept ergänzen (aktuell nur Admin & GF via `backoffice.*`)

## 👥 Organisation

- [ ] Zielbild-Rollen (CTO, CFO, Head of Events, Marketing) mit realen Personen besetzen sobald Team wächst

