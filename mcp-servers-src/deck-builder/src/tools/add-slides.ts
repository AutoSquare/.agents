import { z } from "zod";
import { SlideSchema } from "../schemas/slides.js";
import { addSlides } from "../state/deck-store.js";

export const AddSlidesInputSchema = z.object({
  deckId: z.string().describe("Deck ID from create_deck"),
  slides: z.array(SlideSchema).min(1).describe("Slides to append"),
});

export type AddSlidesInput = z.infer<typeof AddSlidesInputSchema>;

export async function handleAddSlides(input: AddSlidesInput): Promise<{
  deckId: string;
  filePath: string;
  slideCount: number;
}> {
  const state = addSlides(input.deckId, input.slides);

  await state.pptx.writeFile({ fileName: state.filePath });

  return {
    deckId: state.id,
    filePath: state.filePath,
    slideCount: state.slides.length,
  };
}
