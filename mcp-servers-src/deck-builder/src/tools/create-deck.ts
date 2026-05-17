import { z } from "zod";
import path from "path";
import { SlideSchema } from "../schemas/slides.js";
import { ThemeInputSchema } from "../schemas/theme.js";
import { resolveTheme } from "../themes/resolve-theme.js";
import { createDeck } from "../state/deck-store.js";

export const CreateDeckInputSchema = z.object({
  fileName: z.string().default("presentation").describe("Output file name (without .pptx extension)"),
  outputDir: z.string().default(process.cwd()).describe("Directory to save the file"),
  theme: ThemeInputSchema.optional().describe('Preset name ("dark"|"light"|"corporate"|"vibrant") or custom theme object'),
  slides: z.array(SlideSchema).min(1).describe("Array of slide definitions"),
});

export type CreateDeckInput = z.infer<typeof CreateDeckInputSchema>;

export async function handleCreateDeck(input: CreateDeckInput): Promise<{
  deckId: string;
  filePath: string;
  slideCount: number;
}> {
  const theme = resolveTheme(input.theme);
  const fileName = input.fileName.replace(/\.pptx$/i, "");
  const filePath = path.resolve(input.outputDir, `${fileName}.pptx`);

  const state = createDeck(theme, input.slides, filePath);

  await state.pptx.writeFile({ fileName: filePath });

  return {
    deckId: state.id,
    filePath,
    slideCount: state.slides.length,
  };
}
