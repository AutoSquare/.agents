import type { StatsSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

export function renderStats(
  slide: any,
  data: StatsSlide,
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

  const count = data.stats.length;
  const gap = 0.4;
  const cardW = (contentW - (count - 1) * gap) / count;
  const cardH = 1.8;
  const totalW = count * cardW + (count - 1) * gap;
  const startX = (layout.width - totalW) / 2;
  const y = 2.8;

  data.stats.forEach((stat, i) => {
    const x = startX + i * (cardW + gap);

    slide.addShape("roundRect", {
      x,
      y,
      w: cardW,
      h: cardH,
      fill: { color: colors.surface.replace("#", "") },
      line: { color: colors.surfaceBorder.replace("#", ""), width: 1 },
      rectRadius: 0.1,
    });

    slide.addText(stat.value, {
      x: x + 0.2,
      y: y + 0.2,
      w: cardW - 0.4,
      h: 0.8,
      fontSize: 36,
      fontFace: fonts.heading,
      color: colors.accent.replace("#", ""),
      bold: true,
      align: "center",
      valign: "middle",
    });

    slide.addText(stat.label, {
      x: x + 0.2,
      y: y + 1.0,
      w: cardW - 0.4,
      h: 0.6,
      fontSize: 14,
      fontFace: fonts.body,
      color: colors.textMuted.replace("#", ""),
      align: "center",
      valign: "top",
    });
  });
}
