import { z } from "zod";

export const ColorSchema = z
  .string()
  .regex(/^#[0-9a-fA-F]{6}$/, "Must be a hex color like #FF0000");

export const ThemeColorsSchema = z.object({
  background: ColorSchema.optional(),
  text: ColorSchema.optional(),
  textSecondary: ColorSchema.optional(),
  textMuted: ColorSchema.optional(),
  accent: ColorSchema.optional(),
  surface: ColorSchema.optional(),
  surfaceBorder: ColorSchema.optional(),
});

export const ThemeFontsSchema = z.object({
  heading: z.string().optional(),
  body: z.string().optional(),
});

export const ThemeLayoutSchema = z.object({
  width: z.number().optional().describe("Slide width in inches"),
  height: z.number().optional().describe("Slide height in inches"),
  margin: z.number().optional().describe("Slide margin in inches"),
});

export const CustomThemeSchema = z.object({
  colors: ThemeColorsSchema.optional(),
  fonts: ThemeFontsSchema.optional(),
  layout: ThemeLayoutSchema.optional(),
});

export const ThemePresetName = z.enum(["dark", "light", "corporate", "vibrant"]);

export const ThemeInputSchema = z.union([ThemePresetName, CustomThemeSchema]);

export type ThemeColors = Required<z.infer<typeof ThemeColorsSchema>>;
export type ThemeFonts = Required<z.infer<typeof ThemeFontsSchema>>;
export type ThemeLayout = Required<z.infer<typeof ThemeLayoutSchema>>;
export type CustomTheme = z.infer<typeof CustomThemeSchema>;
export type ThemePreset = z.infer<typeof ThemePresetName>;
export type ThemeInput = z.infer<typeof ThemeInputSchema>;

export interface ResolvedTheme {
  colors: ThemeColors;
  fonts: ThemeFonts;
  layout: ThemeLayout;
}
