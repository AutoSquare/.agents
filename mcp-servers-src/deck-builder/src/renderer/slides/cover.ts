import type { CoverSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

// pptxgenjs namespace types don't resolve under Node16 moduleResolution,
// so we type the slide as `any`. The API works correctly at runtime.

export function renderCover(
  slide: any,
  data: CoverSlide,
  theme: ResolvedTheme,
): void {
  const { colors, fonts, layout } = theme;
  const contentW = layout.width - 2 * layout.margin;

  slide.background = { color: colors.background.replace("#", "") };

  slide.addText(data.title, {
    x: layout.margin,
    y: 2.2,
    w: contentW,
    h: 1.2,
    fontSize: 72,
    fontFace: fonts.heading,
    color: colors.text.replace("#", ""),
    bold: true,
    align: "center",
    valign: "middle",
  });

  if (data.subtitle) {
    slide.addText(data.subtitle, {
      x: layout.margin,
      y: 3.5,
      w: contentW,
      h: 0.7,
      fontSize: 26,
      fontFace: fonts.body,
      color: colors.textSecondary.replace("#", ""),
      align: "center",
      valign: "middle",
    });
  }

  if (data.tagline) {
    slide.addText(data.tagline, {
      x: layout.margin,
      y: data.subtitle ? 4.5 : 3.5,
      w: contentW,
      h: 1.0,
      fontSize: 18,
      fontFace: fonts.body,
      color: colors.textMuted.replace("#", ""),
      align: "center",
      valign: "top",
    });
  }
}
