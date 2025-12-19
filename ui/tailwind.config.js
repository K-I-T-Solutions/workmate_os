import defaultTheme from "tailwindcss/defaultTheme";

export default {
  content: [
  "./index.html",
  "./src/**/*.{vue,js,ts,css}",
],

  theme: {
    extend: {
      colors: {
        bg: {
          primary: "var(--color-bg-primary)",
        },
        panel: {
          glass: "var(--color-panel-glass)",
        },
        accent: {
          primary: "var(--color-accent-primary)",
        },
        text: {
          primary: "var(--color-text-primary)",
          secondary: "var(--color-text-secondary)",
        },
        border: {
          light: "var(--color-border-light)",
        },
      },

      fontFamily: {
        sans: ["var(--font-primary)", ...defaultTheme.fontFamily.sans],
        mono: ["var(--font-mono)", ...defaultTheme.fontFamily.mono],
      },

      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },

      boxShadow: {
        soft: "var(--shadow-soft)",
      },

      spacing: {
        xs: "var(--space-xs)",
        sm: "var(--space-sm)",
        md: "var(--space-md)",
        lg: "var(--space-lg)",
        xl: "var(--space-xl)",
      },

      backdropBlur: {
        glass: "var(--blur-glass)",
      },
    },
  },
  plugins: [],
};
