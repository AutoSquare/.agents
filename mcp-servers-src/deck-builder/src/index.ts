#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { SlideSchema } from "./schemas/slides.js";
import { ThemeInputSchema } from "./schemas/theme.js";
import { handleCreateDeck } from "./tools/create-deck.js";
import { handleAddSlides } from "./tools/add-slides.js";
import { handleGetStatus } from "./tools/get-status.js";

const server = new McpServer({
  name: "deck-builder",
  version: "1.0.0",
});

// Tool 1: create_deck
server.tool(
  "create_deck",
  "Build an entire PPTX presentation in one call. Supports 8 slide types (cover, content, cards, stats, table, two_column, chart, section_break) and 4 theme presets (dark, light, corporate, vibrant) or custom themes.",
  {
    fileName: z.string().optional().default("presentation").describe("Output file name (without .pptx)"),
    outputDir: z.string().optional().default(process.cwd()).describe("Directory to save the file"),
    theme: ThemeInputSchema.optional().describe('Theme preset ("dark"|"light"|"corporate"|"vibrant") or custom theme object with colors/fonts/layout'),
    slides: z.array(SlideSchema).min(1).describe("Array of typed slide objects"),
  },
  async (args) => {
    try {
      const result = await handleCreateDeck({
        fileName: args.fileName ?? "presentation",
        outputDir: args.outputDir ?? process.cwd(),
        theme: args.theme,
        slides: args.slides,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: true,
                deckId: result.deckId,
                filePath: result.filePath,
                slideCount: result.slideCount,
                message: `Created ${result.slideCount}-slide presentation at ${result.filePath}`,
              },
              null,
              2,
            ),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              error: error instanceof Error ? error.message : String(error),
            }),
          },
        ],
        isError: true,
      };
    }
  },
);

// Tool 2: add_slides
server.tool(
  "add_slides",
  "Append slides to an existing deck (created by create_deck). Re-renders the full presentation and overwrites the file.",
  {
    deckId: z.string().describe("Deck ID returned by create_deck"),
    slides: z.array(SlideSchema).min(1).describe("Slides to append"),
  },
  async (args) => {
    try {
      const result = await handleAddSlides({
        deckId: args.deckId,
        slides: args.slides,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: true,
                deckId: result.deckId,
                filePath: result.filePath,
                slideCount: result.slideCount,
                message: `Deck now has ${result.slideCount} slides. Updated at ${result.filePath}`,
              },
              null,
              2,
            ),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              error: error instanceof Error ? error.message : String(error),
            }),
          },
        ],
        isError: true,
      };
    }
  },
);

// Tool 3: get_deck_status
server.tool(
  "get_deck_status",
  "Check the status and slide list of an in-progress deck.",
  {
    deckId: z.string().describe("Deck ID to check"),
  },
  async (args) => {
    const result = handleGetStatus({ deckId: args.deckId });

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  },
);

// Start
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
