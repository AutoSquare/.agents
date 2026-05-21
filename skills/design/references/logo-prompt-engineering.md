# Logo AI 提示词工程

## 核心提示词结构

```
Professional logo design for [brand/industry]:
[Visual description]
Style: [style keywords]
Colors: [color palette]
Requirements: [technical specs]
```

## 按风格的有效关键词

### Minimalist
```
minimalist, clean lines, simple geometric shapes, essential elements only,
high white space, flat design, single color, modern, uncluttered,
negative space, subtle, refined
```

### Vintage/Retro
```
vintage, retro, heritage, established, classic, nostalgic, weathered,
distressed texture, badge style, hand-lettered, craft, artisan,
sepia tones, muted colors, aged paper effect
```

### Luxury/Premium
```
luxury, elegant, sophisticated, premium, refined, exclusive, high-end,
gold accents, metallic, minimal, tasteful, upscale, prestige,
thin lines, serif typography, foil effect
```

### Modern/Tech
```
modern, innovative, digital, tech-forward, sleek, futuristic,
gradient colors, geometric, abstract, dynamic, cutting-edge,
clean sans-serif, circuit-like, data visualization
```

### Playful/Fun
```
playful, fun, colorful, friendly, approachable, cheerful, whimsical,
bouncy, rounded shapes, bright colors, cartoon-like, energetic,
bubbly, hand-drawn elements
```

### Organic/Natural
```
organic, natural, flowing, botanical, eco-friendly, sustainable,
earth tones, leaf elements, hand-drawn, imperfect lines, growth,
green, nature-inspired, biophilic
```

## 负向提示词（应避免）

始终加入以排除不良结果：
```
NOT: photorealistic, 3D render with realistic textures, photograph,
stock image, clip art, multiple logos, busy background, text watermarks,
low quality, blurry, distorted, complex detailed patterns
```

## 按行业的提示词

### Tech Startup
```
Modern tech company logo, abstract geometric mark, gradient blue to purple,
clean minimal design, innovative feel, scalable vector style,
professional quality, silicon valley aesthetic
```

### Healthcare
```
Healthcare medical logo, clean professional design, cross or heart symbol,
calming blue and teal colors, trustworthy appearance, caring feel,
simple scalable mark, HIPAA-appropriate conservative style
```

### Restaurant/Food
```
Restaurant logo, warm inviting colors, appetizing feel, vintage badge style,
chef or utensil iconography, friendly welcoming design, rustic charm,
established look, readable at small sizes
```

### Fashion Brand
```
Fashion brand logo, elegant sophisticated wordmark, luxury aesthetic,
black and gold color scheme, thin refined typography, haute couture feel,
minimal exclusive design, high-end positioning
```

### Eco/Sustainable
```
Eco-friendly sustainable brand logo, organic natural elements, leaf motif,
earth green and brown colors, growth symbolism, environmental awareness,
clean modern yet natural feel, recyclable-look design
```

## 应包含的技术要求

### Scalability
```
vector-style, scalable at any size, clear silhouette,
works as favicon, recognizable small scale, simple shapes
```

### Versatility
```
works on light and dark backgrounds, single color version possible,
horizontal and stacked layouts, brand mark can stand alone
```

### Quality
```
professional quality, print-ready, high resolution,
crisp edges, balanced composition, centered design
```

## 提示词模板

### 快速生成
```
Professional [industry] logo, [style] design, [color] colors,
clean modern aesthetic, scalable vector style
```

### 详细简报
```
Professional logo design for [brand name], a [industry] company.

Visual style: [style keywords]
Primary colors: [hex codes]
Mood: [emotional keywords]
Symbols: [iconography hints]

Technical: Vector-style illustration, scalable, works in single color,
centered on plain background, no text unless specified.
```

### 变体请求
```
Alternative version of [brand] logo:
Keep: [elements to preserve]
Change: [elements to modify]
Style direction: [new style keywords]
```

## 常见陷阱

1. **过于复杂** — AI 易生成细节；应要求 "simple"
2. **背景不清** — 指定 "plain white background"
3. **文字问题** — AI 不擅文字；可单独生成图形标
4. **宽高比错误** — 指定 "1:1 square" 或 "horizontal"
5. **写实风格** — 加入 "illustration, vector-style, not photorealistic"
