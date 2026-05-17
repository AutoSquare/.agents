import type { SectionBreakSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

export function renderSectionBreak(
  slide: any,
  data: SectionBreakSlide,
  theme: ResolvedTheme,
): void {
  const { colors, fonts, layout } = theme;
  const contentW = layout.width - 2 * layout.margin;

  slide.background = { color: colors.background.replace("#", "") };

  // Accent line
  slide.addShape("rect", {
    x: layout.width / 2 - 1.5,
    y: 2.5,
    w: 3.0,
    h: 0.04,
    fill: { color: colors.accent.replace("#", "") },
  });

  slide.addText(data.title, {
    x: layout.margin,
    y: 2.8,
    w: contentW,
    h: 1.2,
    fontSize: 48,
    fontFace: fonts.heading,
    color: colors.text.replace("#", ""),
    bold: true,
    align: "center",
    valign: "middle",
  });

  if (data.subtitle) {
    slide.addText(data.subtitle, {
      x: layout.margin,
      y: 4.2,
      w: contentW,
      h: 0.7,
      fontSize: 22,
      fontFace: fonts.body,
      color: colors.textMuted.replace("#", ""),
      align: "center",
      valign: "middle",
    });
  }
}
