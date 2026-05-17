import PptxGenJS from "pptxgenjs";
import type { SlideDefinition } from "../schemas/slides.js";
import type { ResolvedTheme } from "../schemas/theme.js";
import { renderCover } from "./slides/cover.js";
import { renderContent } from "./slides/content.js";
import { renderCards } from "./slides/cards.js";
import { renderStats } from "./slides/stats.js";
import { renderTable } from "./slides/table.js";
import { renderTwoColumn } from "./slides/two-column.js";
import { renderChart } from "./slides/chart.js";
import { renderSectionBreak } from "./slides/section-break.js";

const renderers: Record<
  SlideDefinition["type"],
  (slide: any, data: any, theme: ResolvedTheme) => void
> = {
  cover: renderCover,
  content: renderContent,
  cards: renderCards,
  stats: renderStats,
  table: renderTable,
  two_column: renderTwoColumn,
  chart: renderChart,
  section_break: renderSectionBreak,
};

export function renderSlide(
  pptx: any,
  slideDef: SlideDefinition,
  theme: ResolvedTheme,
): void {
  const slide = pptx.addSlide();
  const renderer = renderers[slideDef.type];
  if (!renderer) {
    throw new Error(`Unknown slide type: ${slideDef.type}`);
  }
  renderer(slide, slideDef, theme);
}

export function createPresentation(theme: ResolvedTheme): any {
  const pptx = new (PptxGenJS as any)();
  pptx.defineLayout({
    name: "CUSTOM",
    width: theme.layout.width,
    height: theme.layout.height,
  });
  pptx.layout = "CUSTOM";
  pptx.author = "deck-builder MCP";
  return pptx;
}
