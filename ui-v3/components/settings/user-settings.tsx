"use client"

import { useAuth } from "@/components/providers/auth-provider"
import { ExternalLinkIcon, KeyRoundIcon, MailIcon, UserIcon, ShieldIcon, PaletteIcon } from "lucide-react"
import { useState } from "react"
import { useTheme, THEMES, type ThemeId } from "@/lib/theme/use-theme"

const KEYCLOAK_ACCOUNT_URL =
  process.env.NEXT_PUBLIC_KEYCLOAK_URL && process.env.NEXT_PUBLIC_KEYCLOAK_REALM
    ? `${process.env.NEXT_PUBLIC_KEYCLOAK_URL}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM}/account`
    : null

type Tab = "profile" | "security" | "appearance"
const TABS: { id: Tab; label: string }[] = [
  { id: "profile", label: "Profil" },
  { id: "security", label: "Sicherheit" },
  { id: "appearance", label: "Erscheinungsbild" },
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

function AppearanceTab() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="space-y-6 max-w-lg">
      <p className="text-sm text-muted-foreground">
        Wähle ein Farbschema für WorkmateOS. Die Einstellung wird lokal gespeichert.
      </p>

      <div className="grid grid-cols-2 gap-3">
        {THEMES.map(t => {
          const isActive = theme === t.id
          return (
            <button
              key={t.id}
              onClick={() => setTheme(t.id as ThemeId)}
              className={`group relative rounded-xl border-2 p-4 text-left transition-all ${
                isActive
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/40 hover:bg-secondary/50"
              }`}
            >
              <div
                className="mb-3 h-16 w-full rounded-lg overflow-hidden"
                style={{
                  background: `linear-gradient(135deg, ${t.preview[0]} 0%, ${t.preview[1]} 100%)`,
                }}
              >
                <div className="flex h-full items-end p-2 gap-1">
                  <div
                    className="h-2 w-8 rounded-full opacity-80"
                    style={{ backgroundColor: t.accent }}
                  />
                  <div className="h-1.5 w-5 rounded-full bg-white/20" />
                  <div className="h-1.5 w-4 rounded-full bg-white/15" />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold">{t.name}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{t.description}</p>
                </div>
                {isActive && (
                  <div
                    className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full"
                    style={{ backgroundColor: t.accent }}
                  >
                    <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </div>
            </button>
          )
        })}
      </div>

      <div className="flex items-center gap-3 rounded-lg border bg-card px-4 py-3">
        <PaletteIcon className="h-4 w-4 text-muted-foreground shrink-0" />
        <div>
          <p className="text-xs text-muted-foreground">Aktives Theme</p>
          <p className="text-sm font-medium">
            {THEMES.find(t => t.id === theme)?.name ?? "Standard"}
          </p>
        </div>
      </div>
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
      {tab === "appearance" && <AppearanceTab />}
    </div>
  )
}
