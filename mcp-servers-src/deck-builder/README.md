# @mozuma/deck-builder

An [MCP server](https://modelcontextprotocol.io) that generates styled, editable PowerPoint (.pptx) presentations. Give it structured slide data and a theme — get a professional deck back.

No Python, no LibreOffice, no external services. Pure JavaScript via [pptxgenjs](https://github.com/gitbrent/PptxGenJS).

## What is this?

This is a **tool server** that plugs into any AI assistant that supports the [Model Context Protocol](https://modelcontextprotocol.io) (MCP). Once connected, the AI can generate real `.pptx` files — not images, not PDFs — fully editable PowerPoint decks with charts, tables, styled cards, and proper typography.

### The problem it solves

AI assistants can write presentation *content* but can't create actual presentation *files*. You end up copy-pasting into Google Slides or PowerPoint manually. This server closes that gap: the AI calls `create_deck` with slide definitions, and a `.pptx` file appears on your machine.

### What makes it different

Existing PPTX tools are generic — they expose low-level "add text box at x,y" primitives. This server is **opinionated about structure**:

- 8 semantic slide types (cover, stats, cards, chart, etc.) with auto-layout
- 4 professional theme presets with consistent typography and colors
- The AI describes *what* goes on each slide, not *where* each element goes

## Where to use it

### Claude Code (CLI)

```bash
claude mcp add deck-builder -- npx -y @mozuma/deck-builder
```

Then in any Claude Code session:

> "Create a 5-slide pitch deck for my startup"

Claude will call `create_deck` and save a `.pptx` to your working directory.

### Claude Code with co-work (parallel agents)

When using Claude Code's co-work feature with multiple agents, each agent has access to the same MCP servers. This means:

- One agent can research and outline the deck content
- Another agent can call `create_deck` to generate the file
- An agent can use `add_slides` to append slides to an existing deck without regenerating the whole thing

The `add_slides` + `get_deck_status` workflow is specifically designed for this — decks are kept in memory for 30 minutes so multiple agents (or multiple turns) can collaborate on a single presentation.

### Any MCP-compatible client

This server uses standard MCP over stdio transport. It works with any client that implements the protocol:

- **Claude Desktop** — add to `claude_desktop_config.json`:
  ```json
  {
    "mcpServers": {
      "deck-builder": {
        "command": "npx",
        "args": ["-y", "@mozuma/deck-builder"]
      }
    }
  }
  ```
- **Cursor / Windsurf** — add as an MCP server in settings
- **Custom agents** — any agent built with the [MCP SDK](https://github.com/modelcontextprotocol/sdk) can connect

## Tools

### `create_deck`

Build an entire presentation in one call. This covers ~90% of use cases.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fileName` | string | `"presentation"` | Output name (without .pptx) |
| `outputDir` | string | cwd | Directory to save the file |
| `theme` | string \| object | `"dark"` | Preset name or custom theme |
| `slides` | array | *required* | Array of typed slide objects |

Returns `deckId`, `filePath`, and `slideCount`.

**Example:**

```json
{
  "fileName": "q1-review",
  "theme": "corporate",
  "slides": [
    {
      "type": "cover",
      "title": "Q1 2026 Review",
      "subtitle": "Engineering Team",
      "tagline": "Building faster, shipping more"
    },
    {
      "type": "stats",
      "title": "Key Metrics",
      "stats": [
        { "value": "99.9%", "label": "Uptime" },
        { "value": "2.3s", "label": "P95 Latency" },
        { "value": "142", "label": "PRs Merged" }
      ]
    },
    {
      "type": "chart",
      "title": "Revenue Growth",
      "chart": {
        "chartType": "bar",
        "categories": ["Jan", "Feb", "Mar"],
        "series": [{ "name": "Revenue", "values": [120, 145, 190] }],
        "valueFormat": "K"
      }
    }
  ]
}
```

### `add_slides`

Append slides to an existing deck (by `deckId` from `create_deck`). Re-renders and overwrites the file.

```json
{
  "deckId": "deck_abc123",
  "slides": [
    { "type": "section_break", "title": "Thank You", "subtitle": "Questions?" }
  ]
}
```

### `get_deck_status`

Check what's in a deck — slide count, types, file path, age.

```json
{ "deckId": "deck_abc123" }
```

## Slide Types

### `cover` — Title slide

```json
{ "type": "cover", "title": "ACME Corp", "subtitle": "Series A Pitch", "tagline": "Making widgets since 2020" }
```

### `content` — Text-heavy slide

```json
{ "type": "content", "title": "Our Approach", "subtitle": "Three pillars", "body": "Line one\nLine two\nLine three", "footnote": "Source: internal data" }
```

### `cards` — Feature cards (2-6)

```json
{ "type": "cards", "title": "Why Us", "cards": [
  { "heading": "Fast", "body": "Sub-second responses" },
  { "heading": "Reliable", "body": "99.99% uptime SLA" },
  { "heading": "Secure", "body": "SOC2 Type II certified" }
]}
```

### `stats` — KPI callouts (2-6)

```json
{ "type": "stats", "title": "Traction", "stats": [
  { "value": "$2.1M", "label": "ARR" },
  { "value": "340", "label": "Customers" },
  { "value": "127%", "label": "Net Revenue Retention" }
]}
```

### `table` — Data tables

```json
{ "type": "table", "title": "Competitive Landscape", "headers": ["Company", "Pricing", "Market"], "rows": [
  ["Us", "$99/mo", "SMB"],
  ["Competitor A", "$299/mo", "Enterprise"],
  ["Competitor B", "Free", "Consumer"]
]}
```

### `two_column` — Side-by-side comparison

```json
{ "type": "two_column", "title": "Before & After", "left": {
  "heading": "Before", "items": ["Manual process", "3 days turnaround", "Error-prone"]
}, "right": {
  "heading": "After", "items": ["Fully automated", "Real-time", "99.9% accuracy"]
}}
```

### `chart` — Bar, line, pie, or doughnut charts

```json
{ "type": "chart", "title": "Growth", "chart": {
  "chartType": "line",
  "categories": ["Q1", "Q2", "Q3", "Q4"],
  "series": [
    { "name": "2025", "values": [10, 25, 40, 55] },
    { "name": "2026", "values": [30, 50, 75, 110] }
  ],
  "valueFormat": "K"
}}
```

### `section_break` — Divider slide

```json
{ "type": "section_break", "title": "Next Steps", "subtitle": "What we need from you" }
```

## Themes

### Presets

| Preset | Background | Accent | Best for |
|--------|-----------|--------|----------|
| `"dark"` | Plum noir (#2B1D25) | Wasabi neon (#E9F056) | Pitch decks, creative |
| `"light"` | White (#FFFFFF) | Blue (#2563EB) | General business |
| `"corporate"` | Light gray (#F8FAFC) | Ocean blue (#0369A1) | Enterprise, formal |
| `"vibrant"` | Deep purple (#0F0A1A) | Coral (#FF6B6B) | Product launches, events |

### Custom themes

Pass an object instead of a preset name. All fields are optional — they merge with the dark preset defaults:

```json
{
  "theme": {
    "colors": {
      "background": "#0D1117",
      "text": "#F0F6FC",
      "accent": "#58A6FF",
      "surface": "#161B22",
      "surfaceBorder": "#30363D"
    },
    "fonts": {
      "heading": "SF Pro Display",
      "body": "SF Pro Text"
    },
    "layout": {
      "width": 13.333,
      "height": 7.5,
      "margin": 1.0
    }
  }
}
```

## How it works internally

1. AI calls `create_deck` with slide definitions + theme
2. Server validates input with Zod schemas (discriminated union on slide `type`)
3. Theme is resolved: preset name → full theme object, or custom merged with defaults
4. Each slide type has a dedicated renderer that uses pptxgenjs to add shapes, text, tables, and charts with proper positioning
5. The `.pptx` file is written to disk
6. Deck state is kept in memory (30min TTL) for `add_slides` follow-ups

## Development

```bash
git clone https://github.com/toontube/deck-builder.git
cd deck-builder
npm install
npm run build

# Test locally with Claude Code
claude mcp add --transport stdio deck-builder -- node /path/to/deck-builder/build/index.js
```

## License

MIT
