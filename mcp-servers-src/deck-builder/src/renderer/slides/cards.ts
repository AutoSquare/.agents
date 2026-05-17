import type { CardsSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

export function renderCards(
  slide: any,
  data: CardsSlide,
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

  const count = data.cards.length;
  const cols = count <= 3 ? count : Math.ceil(count / 2);
  const rows = count <= 3 ? 1 : 2;
  const gap = 0.3;
  const cardW = (contentW - (cols - 1) * gap) / cols;
  const cardH = rows === 1 ? 3.5 : 2.0;
  const startY = 2.0;

  data.cards.forEach((card, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = layout.margin + col * (cardW + gap);
    const y = startY + row * (cardH + gap);

    slide.addShape("roundRect", {
      x,
      y,
      w: cardW,
      h: cardH,
      fill: { color: colors.surface.replace("#", "") },
      line: { color: colors.surfaceBorder.replace("#", ""), width: 1 },
      rectRadius: 0.1,
    });

    slide.addText(card.heading, {
      x: x + 0.2,
      y: y + 0.15,
      w: cardW - 0.4,
      h: 0.5,
      fontSize: 18,
      fontFace: fonts.heading,
      color: colors.accent.replace("#", ""),
      bold: true,
      valign: "top",
    });

    slide.addText(card.body, {
      x: x + 0.2,
      y: y + 0.7,
      w: cardW - 0.4,
      h: cardH - 0.9,
      fontSize: 14,
      fontFace: fonts.body,
      color: colors.textSecondary.replace("#", ""),
      valign: "top",
      wrap: true,
    });
  });
}
