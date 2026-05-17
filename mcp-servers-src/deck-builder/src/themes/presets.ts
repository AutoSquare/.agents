import type { ResolvedTheme } from "../schemas/theme.js";

export const darkTheme: ResolvedTheme = {
  colors: {
    background: "#2B1D25",
    text: "#FFFFFF",
    textSecondary: "#E2E8F0",
    textMuted: "#9CA3AF",
    accent: "#E9F056",
    surface: "#352830",
    surfaceBorder: "#4A3A42",
  },
  fonts: {
    heading: "Space Grotesk",
    body: "Inter",
  },
  layout: {
    width: 13.333,
    height: 7.5,
    margin: 0.9,
  },
};

export const lightTheme: ResolvedTheme = {
  colors: {
    background: "#FFFFFF",
    text: "#1A1A2E",
    textSecondary: "#374151",
    textMuted: "#6B7280",
    accent: "#2563EB",
    surface: "#F3F4F6",
    surfaceBorder: "#D1D5DB",
  },
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  layout: {
    width: 13.333,
    height: 7.5,
    margin: 0.9,
  },
};

export const corporateTheme: ResolvedTheme = {
  colors: {
    background: "#F8FAFC",
    text: "#0F172A",
    textSecondary: "#334155",
    textMuted: "#64748B",
    accent: "#0369A1",
    surface: "#E2E8F0",
    surfaceBorder: "#CBD5E1",
  },
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  layout: {
    width: 13.333,
    height: 7.5,
    margin: 0.9,
  },
};

export const vibrantTheme: ResolvedTheme = {
  colors: {
    background: "#0F0A1A",
    text: "#FFFFFF",
    textSecondary: "#D4D4F7",
    textMuted: "#8B8BAE",
    accent: "#FF6B6B",
    surface: "#1A1330",
    surfaceBorder: "#2D2447",
  },
  fonts: {
    heading: "Arial",
    body: "Arial",
  },
  layout: {
    width: 13.333,
    height: 7.5,
    margin: 0.9,
  },
};

export const presets: Record<string, ResolvedTheme> = {
  dark: darkTheme,
  light: lightTheme,
  corporate: corporateTheme,
  vibrant: vibrantTheme,
};
