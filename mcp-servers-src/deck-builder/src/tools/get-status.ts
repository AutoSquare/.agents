import { z } from "zod";
import { getDeckStatus } from "../state/deck-store.js";

export const GetStatusInputSchema = z.object({
  deckId: z.string().describe("Deck ID to check"),
});

export type GetStatusInput = z.infer<typeof GetStatusInputSchema>;

export function handleGetStatus(input: GetStatusInput): {
  found: boolean;
  id?: string;
  slideCount?: number;
  slideTypes?: string[];
  filePath?: string;
  ageSeconds?: number;
} {
  const status = getDeckStatus(input.deckId);
  if (!status) {
    return { found: false };
  }
  return { found: true, ...status };
}
