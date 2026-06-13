"use client"

import { useAuth } from "@/components/providers/auth-provider"
import { ExternalLinkIcon, KeyRoundIcon, MailIcon, UserIcon, ShieldIcon } from "lucide-react"
import { useState } from "react"

const KEYCLOAK_ACCOUNT_URL =
  process.env.NEXT_PUBLIC_KEYCLOAK_URL && process.env.NEXT_PUBLIC_KEYCLOAK_REALM
    ? `${process.env.NEXT_PUBLIC_KEYCLOAK_URL}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM}/account`
    : null

type Tab = "profile" | "security"
const TABS: { id: Tab; label: string }[] = [
  { id: "profile", label: "Profil" },
  { id: "security", label: "Sicherheit" },
]

function InfoRow({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="flex items-start gap-4 rounded-lg border bg-card px-4 py-3">
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="mt-0.5 text-sm font-medium">{value || "–"}</p>
      </div>
    </div>
  )
}

function ProfileTab() {
  const { user } = useAuth()

  if (!user) return null

  return (
    <div className="space-y-4 max-w-lg">
      <p className="text-sm text-muted-foreground">
        Diese Informationen stammen aus deinem Keycloak-Konto und können dort geändert werden.
      </p>

      <div className="space-y-2">
        <InfoRow icon={UserIcon} label="Name" value={user.name} />
        <InfoRow icon={MailIcon} label="E-Mail-Adresse" value={user.email} />
        <InfoRow icon={UserIcon} label="Benutzername" value={user.username} />
        <InfoRow icon={KeyRoundIcon} label="Benutzer-ID" value={user.sub} />
      </div>

      {KEYCLOAK_ACCOUNT_URL && (
        <a
          href={KEYCLOAK_ACCOUNT_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-lg border bg-card px-4 py-2.5 text-sm font-medium transition-colors hover:bg-secondary"
        >
          Profil in Keycloak bearbeiten
          <ExternalLinkIcon className="h-4 w-4" />
        </a>
      )}
    </div>
  )
}

function SecurityTab() {
  return (
    <div className="space-y-4 max-w-lg">
      <div className="rounded-lg border bg-card p-5 space-y-4">
        <div className="flex items-center gap-3">
          <ShieldIcon className="h-5 w-5 text-primary" />
          <div>
            <p className="text-sm font-medium">Passwortverwaltung</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              Passwörter und Sicherheitseinstellungen werden über Keycloak verwaltet.
            </p>
          </div>
        </div>

        {KEYCLOAK_ACCOUNT_URL ? (
          <a
            href={`${KEYCLOAK_ACCOUNT_URL}/password`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg border bg-secondary px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
          >
            Passwort ändern
            <ExternalLinkIcon className="h-4 w-4" />
          </a>
        ) : (
          <p className="text-sm text-muted-foreground">Keycloak-URL nicht konfiguriert.</p>
        )}
      </div>

      <div className="rounded-lg border bg-card p-5 space-y-4">
        <div className="flex items-center gap-3">
          <ShieldIcon className="h-5 w-5 text-primary" />
          <div>
            <p className="text-sm font-medium">Zwei-Faktor-Authentifizierung</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              2FA kann im Keycloak-Konto aktiviert werden.
            </p>
          </div>
        </div>
        {KEYCLOAK_ACCOUNT_URL && (
          <a
            href={`${KEYCLOAK_ACCOUNT_URL}/totp`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg border bg-secondary px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
          >
            2FA verwalten
            <ExternalLinkIcon className="h-4 w-4" />
          </a>
        )}
      </div>

      {KEYCLOAK_ACCOUNT_URL && (
        <div className="rounded-lg border bg-card p-5">
          <div className="flex items-center gap-3">
            <ShieldIcon className="h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium">Aktive Sitzungen</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Alle Geräte einsehen und Sitzungen beenden.
              </p>
            </div>
          </div>
          <a
            href={`${KEYCLOAK_ACCOUNT_URL}/sessions`}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-flex items-center gap-2 rounded-lg border bg-secondary px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
          >
            Sitzungen verwalten
            <ExternalLinkIcon className="h-4 w-4" />
          </a>
        </div>
      )}
    </div>
  )
}

export function UserSettings() {
  const [tab, setTab] = useState<Tab>("profile")

  return (
    <div className="space-y-6 px-8 py-6">
      <h1 className="text-xl font-semibold">Einstellungen</h1>

      <div className="flex gap-1 border-b">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === t.id
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "profile" && <ProfileTab />}
      {tab === "security" && <SecurityTab />}
    </div>
  )
}
