import type { TwoColumnSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

function renderColumn(
  slide: any,
  col: { heading?: string; body?: string; items?: string[] },
  x: number,
  w: number,
  theme: ResolvedTheme,
): void {
  const { colors, fonts } = theme;
  let y = 2.5;

  slide.addShape("roundRect", {
    x,
    y,
    w,
    h: 4.0,
    fill: { color: colors.surface.replace("#", "") },
    line: { color: colors.surfaceBorder.replace("#", ""), width: 1 },
    rectRadius: 0.1,
  });

  const innerX = x + 0.3;
  const innerW = w - 0.6;

  if (col.heading) {
    slide.addText(col.heading, {
      x: innerX,
      y: y + 0.2,
      w: innerW,
      h: 0.45,
      fontSize: 18,
      fontFace: fonts.heading,
      color: colors.accent.replace("#", ""),
      bold: true,
      valign: "top",
    });
    y += 0.65;
  }

  if (col.body) {
    slide.addText(col.body, {
      x: innerX,
      y: y + 0.2,
      w: innerW,
      h: 1.5,
      fontSize: 16,
      fontFace: fonts.body,
      color: colors.textSecondary.replace("#", ""),
      valign: "top",
      wrap: true,
    });
  }

  if (col.items && col.items.length > 0) {
    const itemTop = col.body ? y + 1.6 : y + 0.2;
    const textParts = col.items.map((item, i) => ({
      text: `\u2022  ${item}`,
      options: {
        fontSize: 15,
        fontFace: fonts.body,
        color: colors.textSecondary.replace("#", ""),
        breakType: i < col.items!.length - 1 ? "break" : undefined,
        lineSpacingMultiple: 1.4,
      },
    }));

    slide.addText(textParts, {
      x: innerX,
      y: itemTop,
      w: innerW,
      h: 2.5,
      valign: "top",
    });
  }
}

export function renderTwoColumn(
  slide: any,
  data: TwoColumnSlide,
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

  const gap = 0.5;
  const colW = (contentW - gap) / 2;

  renderColumn(slide, data.left, layout.margin, colW, theme);
  renderColumn(slide, data.right, layout.margin + colW + gap, colW, theme);
}
