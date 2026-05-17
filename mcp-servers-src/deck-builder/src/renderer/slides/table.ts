import type { TableSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

export function renderTable(
  slide: any,
  data: TableSlide,
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

  const border = [
    { type: "solid", color: colors.surfaceBorder.replace("#", ""), pt: 0.5 },
    { type: "solid", color: colors.surfaceBorder.replace("#", ""), pt: 0.5 },
    { type: "solid", color: colors.surfaceBorder.replace("#", ""), pt: 0.5 },
    { type: "solid", color: colors.surfaceBorder.replace("#", ""), pt: 0.5 },
  ];

  const headerRow = data.headers.map((h) => ({
    text: h,
    options: {
      fontSize: 14,
      fontFace: fonts.heading,
      color: colors.accent.replace("#", ""),
      bold: true,
      fill: { color: colors.background.replace("#", "") },
      border,
      margin: [3, 6, 3, 6],
    },
  }));

  const bodyRows = data.rows.map((row, rowIdx) =>
    row.map((cell) => ({
      text: cell,
      options: {
        fontSize: 14,
        fontFace: fonts.body,
        color: colors.textSecondary.replace("#", ""),
        fill: {
          color: (rowIdx % 2 === 0 ? colors.surface : colors.background).replace("#", ""),
        },
        border,
        margin: [3, 6, 3, 6],
      },
    })),
  );

  const allRows = [headerRow, ...bodyRows];
  const colW = contentW / data.headers.length;

  slide.addTable(allRows, {
    x: layout.margin,
    y: 2.2,
    w: contentW,
    colW: Array(data.headers.length).fill(colW),
    rowH: 0.55,
    autoPage: false,
  });
}
