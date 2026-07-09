import { themes as prismThemes } from "prism-react-renderer"
import type { Config } from "@docusaurus/types"
import type * as Preset from "@docusaurus/preset-classic"

const config: Config = {
  title: "WorkmateOS Docs",
  tagline: "Interne Entwicklerdokumentation — K.I.T. Solutions",
  favicon: "img/favicon.ico",

  url: "https://K-I-T-Solutions.github.io",
  baseUrl: "/workmate_os/",

  organizationName: "K-I-T-Solutions",
  projectName: "workmate_os",
  trailingSlash: false,

  onBrokenLinks: "warn",
  onBrokenMarkdownLinks: "warn",

  markdown: {
    format: "md",
  },

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          path: "../docs/wiki",
          routeBasePath: "/",
          sidebarPath: "./sidebars.ts",
          editUrl:
            "https://github.com/K-I-T-Solutions/workmate_os/edit/main/docs/wiki/",
          exclude: ["**/ui/**", "**/design/**"],
        },
        blog: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: "img/workmate-social.png",
    colorMode: {
      defaultMode: "dark",
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "WorkmateOS",
      logo: {
        alt: "K.I.T. Solutions Logo",
        src: "img/logo.png",
      },
      items: [
        {
          type: "docSidebar",
          sidebarId: "backendSidebar",
          position: "left",
          label: "Backend",
        },
        {
          type: "docSidebar",
          sidebarId: "frontendSidebar",
          position: "left",
          label: "Frontend",
        },
        {
          type: "docSidebar",
          sidebarId: "backofficeAndCoreSidebar",
          position: "left",
          label: "Backoffice & Core",
        },
        {
          to: "/finance/",
          position: "left",
          label: "Finance",
        },
        {
          href: "https://api.workmate.kit-it-koblenz.de/docs",
          label: "API (Swagger)",
          position: "right",
        },
        {
          href: "https://github.com/K-I-T-Solutions/workmate_os",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Dokumentation",
          items: [
            { label: "Backend", to: "/backend/AUTHENTICATION" },
            { label: "Frontend", to: "/frontend/" },
            { label: "Module", to: "/backend/MODULE_UEBERSICHT" },
            { label: "Backoffice", to: "/backoffice/" },
          ],
        },
        {
          title: "Links",
          items: [
            { label: "WorkmateOS", href: "https://workmate.kit-it-koblenz.de" },
            { label: "API Docs", href: "https://api.workmate.kit-it-koblenz.de/docs" },
            { label: "GitHub", href: "https://github.com/K-I-T-Solutions/workmate_os" },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} K.I.T. Solutions · Built with Docusaurus`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ["python", "bash", "sql", "typescript", "yaml", "json"],
    },
    algolia: undefined,
  } satisfies Preset.ThemeConfig,
}

export default config
