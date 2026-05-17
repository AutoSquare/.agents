import type { ChartSlide } from "../../schemas/slides.js";
import type { ResolvedTheme } from "../../schemas/theme.js";

const CHART_TYPE_MAP: Record<string, string> = {
  bar: "bar",
  line: "line",
  pie: "pie",
  doughnut: "doughnut",
};

export function renderChart(
  slide: any,
  data: ChartSlide,
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

  const chartType = CHART_TYPE_MAP[data.chart.chartType] ?? "bar";

  const chartData = data.chart.series.map((s) => ({
    name: s.name,
    labels: data.chart.categories,
    values: s.values,
  }));

  const suffix = data.chart.valueFormat ?? "";
  const isPieType = data.chart.chartType === "pie" || data.chart.chartType === "doughnut";

  slide.addChart(chartType, chartData, {
    x: layout.margin,
    y: 2.2,
    w: contentW,
    h: 4.5,
    showTitle: false,
    showLegend: data.chart.series.length > 1,
    legendPos: "b",
    legendFontSize: 12,
    legendColor: colors.textMuted.replace("#", ""),

    showValue: true,
    dataLabelPosition: "outEnd",
    dataLabelColor: colors.accent.replace("#", ""),
    dataLabelFontSize: 13,
    dataLabelFontBold: true,
    dataLabelFormatCode: suffix ? `0"${suffix}"` : "0",

    ...(isPieType
      ? {
          chartColors: [
            colors.accent.replace("#", ""),
            colors.text.replace("#", ""),
            colors.textSecondary.replace("#", ""),
            colors.textMuted.replace("#", ""),
            colors.surface.replace("#", ""),
            colors.surfaceBorder.replace("#", ""),
          ],
        }
      : {
          catAxisLabelColor: colors.textSecondary.replace("#", ""),
          catAxisLabelFontSize: 12,
          catAxisLabelFontFace: fonts.body,
          catAxisLineShow: false,
          valAxisLabelColor: colors.textMuted.replace("#", ""),
          valAxisLabelFontSize: 11,
          valAxisLabelFontFace: fonts.body,
          valAxisLineShow: false,
          valAxisMajorGridColor: colors.surfaceBorder.replace("#", ""),
          chartColors: [
            colors.accent.replace("#", ""),
            colors.textSecondary.replace("#", ""),
            colors.textMuted.replace("#", ""),
          ],
        }),

    plotArea: {
      fill: { color: colors.background.replace("#", "") },
    },
  });
}
