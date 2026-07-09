import type { ReactNode } from "react"
import Link from "@docusaurus/Link"
import useDocusaurusContext from "@docusaurus/useDocusaurusContext"
import Layout from "@theme/Layout"
import Heading from "@theme/Heading"

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext()
  return (
    <Layout title="Home" description="WorkmateOS interne Entwicklerdokumentation">
      <main style={{ padding: "4rem 2rem", maxWidth: 900, margin: "0 auto" }}>
        <Heading as="h1">{siteConfig.title}</Heading>
        <p style={{ fontSize: "1.2rem", marginBottom: "2rem" }}>
          {siteConfig.tagline}
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem" }}>
          <Card
            title="Backend"
            description="FastAPI, Auth, Module, RBAC"
            to="/backend/AUTHENTICATION"
          />
          <Card
            title="Frontend"
            description="Next.js 14, Auth-Provider, Permissions"
            to="/frontend/"
          />
          <Card
            title="Module"
            description="Alle Backend-Module im Überblick"
            to="/backend/MODULE_UEBERSICHT"
          />
          <Card
            title="Backoffice"
            description="CRM, Projekte, Zeiterfassung, Invoices"
            to="/backoffice/"
          />
        </div>
        <hr style={{ margin: "3rem 0" }} />
        <p style={{ color: "var(--ifm-color-secondary)" }}>
          Stack: FastAPI · PostgreSQL · SQLAlchemy 2.0 · Next.js 14 · Keycloak OIDC · Nextcloud
        </p>
      </main>
    </Layout>
  )
}

function Card({ title, description, to }: { title: string; description: string; to: string }) {
  return (
    <Link
      to={to}
      style={{
        display: "block",
        padding: "1.25rem",
        border: "1px solid var(--ifm-color-emphasis-300)",
        borderRadius: 8,
        textDecoration: "none",
        transition: "border-color 0.2s",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--ifm-color-primary)")}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--ifm-color-emphasis-300)")}
    >
      <strong style={{ fontSize: "1.1rem" }}>{title}</strong>
      <p style={{ margin: "0.5rem 0 0", color: "var(--ifm-color-secondary)", fontSize: "0.9rem" }}>
        {description}
      </p>
    </Link>
  )
}
