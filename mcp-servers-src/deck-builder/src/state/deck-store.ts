import type { SlideDefinition } from "../schemas/slides.js";
import type { ResolvedTheme } from "../schemas/theme.js";
import { createPresentation, renderSlide } from "../renderer/slide-renderer.js";

export interface DeckState {
  id: string;
  theme: ResolvedTheme;
  slides: SlideDefinition[];
  pptx: any;
  filePath: string;
  createdAt: number;
}

const TTL_MS = 30 * 60 * 1000; // 30 minutes
const store = new Map<string, DeckState>();

let cleanupTimer: ReturnType<typeof setInterval> | null = null;

function startCleanup(): void {
  if (cleanupTimer) return;
  cleanupTimer = setInterval(() => {
    const now = Date.now();
    for (const [id, deck] of store) {
      if (now - deck.createdAt > TTL_MS) {
        store.delete(id);
      }
    }
    if (store.size === 0 && cleanupTimer) {
      clearInterval(cleanupTimer);
      cleanupTimer = null;
    }
  }, 60_000);
}

function generateId(): string {
  return `deck_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

export function createDeck(
  theme: ResolvedTheme,
  slides: SlideDefinition[],
  filePath: string,
): DeckState {
  const id = generateId();
  const pptx = createPresentation(theme);

  for (const slideDef of slides) {
    renderSlide(pptx, slideDef, theme);
  }

  const state: DeckState = {
    id,
    theme,
    slides: [...slides],
    pptx,
    filePath,
    createdAt: Date.now(),
  };

  store.set(id, state);
  startCleanup();
  return state;
}

export function addSlides(
  deckId: string,
  newSlides: SlideDefinition[],
): DeckState {
  const state = store.get(deckId);
  if (!state) {
    throw new Error(`Deck not found: ${deckId}. It may have expired (30min TTL).`);
  }

  state.slides.push(...newSlides);
  const pptx = createPresentation(state.theme);
  for (const slideDef of state.slides) {
    renderSlide(pptx, slideDef, state.theme);
  }
  state.pptx = pptx;
  state.createdAt = Date.now();

  return state;
}

export function getDeckStatus(deckId: string): {
  id: string;
  slideCount: number;
  slideTypes: string[];
  filePath: string;
  ageSeconds: number;
} | null {
  const state = store.get(deckId);
  if (!state) return null;

  return {
    id: state.id,
    slideCount: state.slides.length,
    slideTypes: state.slides.map((s) => s.type),
    filePath: state.filePath,
    ageSeconds: Math.round((Date.now() - state.createdAt) / 1000),
  };
}
