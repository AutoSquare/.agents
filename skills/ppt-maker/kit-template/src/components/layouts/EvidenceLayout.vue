<template>
  <div class="evidence-layout">
    <section class="evidence-main">
      <div class="evidence-heading export-layer-fg">
        <h2 class="evidence-title">{{ slide.title }}</h2>
        <p class="evidence-subtitle text-gradient" v-if="slide.subtitle">{{ slide.subtitle }}</p>
        <p class="evidence-summary" v-if="slide.summary">{{ slide.summary }}</p>
      </div>

      <div class="evidence-stats" v-if="slide.stats && slide.stats.length">
        <article class="evidence-stat glass-card export-layer-fg" v-for="stat in slide.stats" :key="stat.label">
          <strong>{{ stat.value }}</strong>
          <span>{{ stat.label }}</span>
        </article>
      </div>

      <div class="evidence-table glass-card export-layer-fg" v-if="slide.table && slide.table.length">
        <div class="evidence-row evidence-row--head">
          <span v-for="head in slide.tableHeaders" :key="head">{{ head }}</span>
        </div>
        <div class="evidence-row" v-for="(row, idx) in slide.table" :key="idx">
          <span v-for="(cell, key) in row" :key="key">{{ cell }}</span>
        </div>
      </div>
    </section>

    <section class="evidence-visual">
      <div class="evidence-stack export-layer-fg" :style="stackStyle">
        <figure
          class="evidence-doc glass-card"
          v-for="(src, idx) in resolvedImages"
          :key="src"
          :style="docStyle(idx)"
        >
          <img :src="src" :alt="`${slide.imageAlt || '成果材料'} ${idx + 1}`" />
        </figure>
      </div>
      <p class="evidence-caption export-layer-fg" v-if="slide.caption">{{ slide.caption }}</p>
    </section>
  </div>
</template>

<script>
import { imageUrl } from '../../data/slides'

export default {
  name: 'EvidenceLayout',
  props: {
    slide: { type: Object, required: true }
  },
  computed: {
    resolvedImages() {
      return (this.slide.images || []).map((file) => imageUrl(file))
    },
    stackStyle() {
      return {
        '--doc-count': this.resolvedImages.length
      }
    }
  },
  methods: {
    docStyle(idx) {
      const count = this.resolvedImages.length
      const mid = (count - 1) / 2
      const offset = idx - mid
      const rotation = offset * 4
      const centerWeight = count - Math.round(Math.abs(offset) * 2)
      return {
        '--doc-index': idx,
        '--doc-x': `${offset * 30}px`,
        '--doc-y': `${Math.abs(offset) * 10}px`,
        '--doc-rotate': `${rotation}deg`,
        zIndex: centerWeight
      }
    }
  }
}
</script>

<style scoped>
.evidence-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 0.92fr 1.08fr;
  gap: 24px;
  padding: 8px 40px 0;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.evidence-main,
.evidence-visual {
  min-width: 0;
  min-height: 0;
}

.evidence-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.evidence-title {
  margin: 0 0 6px;
  font-size: 1.72rem;
  line-height: 1.02;
  font-weight: 800;
  letter-spacing: -0.045em;
  color: var(--color-primary);
}

.evidence-subtitle {
  margin: 0 0 8px;
  font-size: 0.92rem;
  font-weight: 700;
}

.evidence-summary {
  margin: 0;
  max-width: 34em;
  color: var(--color-secondary);
  font-size: 0.72rem;
  line-height: 1.5;
}

.evidence-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.evidence-stat {
  padding: 10px 12px;
  min-width: 0;
}

.evidence-stat strong {
  display: block;
  color: var(--color-accent);
  font-family: var(--font-heading);
  font-size: 1.15rem;
  line-height: 1;
  letter-spacing: -0.04em;
}

.evidence-stat span {
  display: block;
  margin-top: 4px;
  color: var(--color-muted-text);
  font-size: 0.62rem;
  font-weight: 700;
}

.evidence-table {
  overflow: hidden;
}

.evidence-row {
  display: grid;
  grid-template-columns: 1.05fr 1.2fr 0.72fr;
  gap: 8px;
  padding: 8px 12px;
  border-top: 1px solid rgba(37, 99, 235, 0.1);
  color: var(--color-secondary);
  font-size: 0.64rem;
  line-height: 1.34;
}

.evidence-row:first-child {
  border-top: 0;
}

.evidence-row--head {
  background: rgba(37, 99, 235, 0.08);
  color: var(--color-primary);
  font-size: 0.6rem;
  font-weight: 800;
}

.evidence-visual {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  gap: 10px;
}

.evidence-stack {
  position: relative;
  flex: 1;
  min-height: 0;
  max-height: 346px;
  border-radius: var(--card-radius);
  background:
    radial-gradient(circle at 18% 12%, rgba(37, 99, 235, 0.16), transparent 34%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(239, 246, 255, 0.72));
  border: 1px solid rgba(37, 99, 235, 0.14);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.evidence-doc {
  position: absolute;
  left: 50%;
  top: 50%;
  margin: 0;
  width: min(42%, 198px);
  height: 84%;
  padding: 7px;
  transform: translate(calc(-50% + var(--doc-x)), calc(-50% + var(--doc-y))) rotate(var(--doc-rotate));
  transform-origin: center;
  overflow: hidden;
}

.evidence-doc img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  display: block;
  border-radius: 10px;
}

.evidence-doc:nth-child(3n + 1) img {
  object-position: center top;
}

.evidence-caption {
  margin: 0;
  padding: 8px 12px;
  border-radius: 12px;
  background: var(--pill-bg);
  border: 1px solid var(--pill-border);
  color: var(--color-primary);
  font-size: 0.66rem;
  font-weight: 700;
  line-height: 1.4;
}
</style>
