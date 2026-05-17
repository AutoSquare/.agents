import type { ResolvedTheme, ThemeInput, CustomTheme } from "../schemas/theme.js";
import { presets, darkTheme } from "./presets.js";

export function resolveTheme(input?: ThemeInput): ResolvedTheme {
  if (!input) return darkTheme;

  if (typeof input === "string") {
    return presets[input] ?? darkTheme;
  }

  const custom = input as CustomTheme;
  const base = darkTheme;

  return {
    colors: {
      ...base.colors,
      ...(custom.colors ?? {}),
    },
    fonts: {
      ...base.fonts,
      ...(custom.fonts ?? {}),
    },
    layout: {
      ...base.layout,
      ...(custom.layout ?? {}),
    },
  };
}
