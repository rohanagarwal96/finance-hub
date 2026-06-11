import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        background: "#0f172a",
        foreground: "#f8fafc",
        card: { DEFAULT: "#1e293b", foreground: "#f8fafc" },
        border: "#334155",
        input: "#1e293b",
        primary: { DEFAULT: "#3b82f6", foreground: "#ffffff" },
        secondary: { DEFAULT: "#1e293b", foreground: "#94a3b8" },
        muted: { DEFAULT: "#1e293b", foreground: "#64748b" },
        accent: { DEFAULT: "#3b82f6", foreground: "#ffffff" },
        positive: "#10b981",
        warning: "#f59e0b",
        danger: "#f43f5e",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
