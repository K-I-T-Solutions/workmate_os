import defaultTheme from "tailwindcss/defaultTheme";

export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,css}",
  ],

  theme: {
    screens: {
      'xs': '480px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1200px',
      '2xl': '1920px',
    },

    extend: {
      colors: {
        // Keep default colors but add theme-aware colors
        bg: {
          primary: "var(--color-bg-primary)",
          secondary: "var(--color-bg-secondary)",
          tertiary: "var(--color-bg-tertiary)",
        },
        panel: {
          glass: "var(--color-panel-glass)",
          'glass-hover': "var(--color-panel-glass-hover)",
        },
        accent: {
          primary: "var(--color-accent-primary)",
          'primary-hover': "var(--color-accent-primary-hover)",
          secondary: "var(--color-accent-secondary)",
        },
        text: {
          primary: "var(--color-text-primary)",
          secondary: "var(--color-text-secondary)",
          tertiary: "var(--color-text-tertiary)",
          muted: "var(--color-text-muted)",
        },
        border: {
          light: "var(--color-border-light)",
          medium: "var(--color-border-medium)",
          strong: "var(--color-border-strong)",
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

      minHeight: {
        'touch': 'var(--touch-target-min)',
      },

      minWidth: {
        'touch': 'var(--touch-target-min)',
      },
    },
  },
  plugins: [],
};
