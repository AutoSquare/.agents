import { z } from "zod";

const CoverSlideSchema = z.object({
  type: z.literal("cover"),
  title: z.string(),
  subtitle: z.string().optional(),
  tagline: z.string().optional(),
});

const ContentSlideSchema = z.object({
  type: z.literal("content"),
  title: z.string(),
  subtitle: z.string().optional(),
  body: z.string(),
  footnote: z.string().optional(),
});

const CardItemSchema = z.object({
  heading: z.string(),
  body: z.string(),
});

const CardsSlideSchema = z.object({
  type: z.literal("cards"),
  title: z.string(),
  cards: z.array(CardItemSchema).min(2).max(6),
});

const StatItemSchema = z.object({
  value: z.string(),
  label: z.string(),
});

const StatsSlideSchema = z.object({
  type: z.literal("stats"),
  title: z.string(),
  stats: z.array(StatItemSchema).min(2).max(6),
});

const TableSlideSchema = z.object({
  type: z.literal("table"),
  title: z.string(),
  headers: z.array(z.string()),
  rows: z.array(z.array(z.string())),
});

const ColumnContentSchema = z.object({
  heading: z.string().optional(),
  body: z.string().optional(),
  items: z.array(z.string()).optional(),
});

const TwoColumnSlideSchema = z.object({
  type: z.literal("two_column"),
  title: z.string(),
  left: ColumnContentSchema,
  right: ColumnContentSchema,
});

const ChartSeriesSchema = z.object({
  name: z.string(),
  values: z.array(z.number()),
});

const ChartDataSchema = z.object({
  chartType: z.enum(["bar", "line", "pie", "doughnut"]),
  categories: z.array(z.string()),
  series: z.array(ChartSeriesSchema),
  valueFormat: z.string().optional().describe("Suffix like '%' or '$'"),
});

const ChartSlideSchema = z.object({
  type: z.literal("chart"),
  title: z.string(),
  chart: ChartDataSchema,
});

const SectionBreakSlideSchema = z.object({
  type: z.literal("section_break"),
  title: z.string(),
  subtitle: z.string().optional(),
});

export const SlideSchema = z.discriminatedUnion("type", [
  CoverSlideSchema,
  ContentSlideSchema,
  CardsSlideSchema,
  StatsSlideSchema,
  TableSlideSchema,
  TwoColumnSlideSchema,
  ChartSlideSchema,
  SectionBreakSlideSchema,
]);

export type SlideDefinition = z.infer<typeof SlideSchema>;
export type CoverSlide = z.infer<typeof CoverSlideSchema>;
export type ContentSlide = z.infer<typeof ContentSlideSchema>;
export type CardsSlide = z.infer<typeof CardsSlideSchema>;
export type StatsSlide = z.infer<typeof StatsSlideSchema>;
export type TableSlide = z.infer<typeof TableSlideSchema>;
export type TwoColumnSlide = z.infer<typeof TwoColumnSlideSchema>;
export type ChartSlide = z.infer<typeof ChartSlideSchema>;
export type SectionBreakSlide = z.infer<typeof SectionBreakSlideSchema>;

export {
  CoverSlideSchema,
  ContentSlideSchema,
  CardsSlideSchema,
  StatsSlideSchema,
  TableSlideSchema,
  TwoColumnSlideSchema,
  ChartSlideSchema,
  SectionBreakSlideSchema,
};
