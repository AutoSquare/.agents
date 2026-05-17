import type { ContentSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

export function renderContent(
  slide: any,
  data: ContentSlide,
  theme: ResolvedTheme,
): void {
  const { colors, fonts, layout } = theme;
  const contentW = layout.width - 2 * layout.margin;

  slide.background = { color: colors.background.replace("#", "") };

  slide.addText(data.title, {
    x: layout.margin,
    y: 0.7,
    w: contentW,
    h: 0.8,
    fontSize: 40,
    fontFace: fonts.heading,
    color: colors.text.replace("#", ""),
    bold: true,
  });

  if (data.subtitle) {
    slide.addText(data.subtitle, {
      x: layout.margin,
      y: 1.5,
      w: contentW,
      h: 0.6,
      fontSize: 22,
      fontFace: fonts.body,
      color: colors.textMuted.replace("#", ""),
    });
  }

  const bodyTop = data.subtitle ? 2.5 : 2.0;
  const bodyParts = data.body.split("\n").map((line, i, arr) => ({
    text: line,
    options: {
      fontSize: 18,
      fontFace: fonts.body,
      color: colors.textSecondary.replace("#", ""),
      breakType: i < arr.length - 1 ? "break" : undefined,
      lineSpacingMultiple: 1.5,
    },
  }));

  slide.addText(bodyParts, {
    x: layout.margin,
    y: bodyTop,
    w: contentW,
    h: 3.5,
    valign: "top",
  });

  if (data.footnote) {
    slide.addText(data.footnote, {
      x: layout.margin,
      y: layout.height - 1.2,
      w: contentW,
      h: 0.5,
      fontSize: 14,
      fontFace: fonts.body,
      color: colors.textMuted.replace("#", ""),
      align: "center",
    });
  }
}
