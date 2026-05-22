<template>
  <section
    class="slide-frame-wrap"
    :aria-labelledby="`slide-title-${slide.id}`"
  >
    <article class="slide-frame">
      <div class="slide-frame__canvas">
        <header class="slide-frame__header">
          <div class="slide-frame__header-top">
            <span class="slide-frame__section-badge">
              <span class="badge-dot"></span>
              {{ slide.sectionLabel }}
            </span>
            <span class="slide-frame__counter">{{ slide.sectionIndex }} // {{ slideTotalPadded }}</span>
          </div>
          <div class="slide-frame__header-main">
            <h2 :id="`slide-title-${slide.id}`" class="slide-frame__title">
              {{ slide.title }}
            </h2>
            <div class="slide-frame__divider"></div>
            <p class="slide-frame__theme">{{ slide.theme }}</p>
          </div>
        </header>

        <DualCaseLayout
          :cases="slide.cases"
          :layout-ratio="slide.layoutRatio"
          :lazy-load="slide.id > 1"
        />

        <footer class="slide-frame__footer" aria-hidden="true">
          <span class="footer-left">{{ footerLeftText }}</span>
          <span class="footer-right">{{ footerText }}</span>
        </footer>

        <!-- Draft Alignment Grid Helper -->
        <div v-if="gridState && gridState.active" class="alignment-grid" aria-hidden="true">
          <!-- 12 Columns -->
          <div
            v-for="c in 11"
            :key="'col-' + c"
            class="grid-line grid-line--col"
            :style="{ left: (c * 100 / 12) + '%' }"
            :class="{ 'grid-line--thirds': c === 4 || c === 8 }"
          ></div>
          
          <!-- 8 Rows -->
          <div
            v-for="r in 7"
            :key="'row-' + r"
            class="grid-line grid-line--row"
            :style="{ top: (r * 100 / 8) + '%' }"
            :class="{ 'grid-line--thirds': r === 3 || r === 5 }"
          ></div>

          <!-- Exact Rule of Thirds Overlays (33.33% and 66.66%) -->
          <div class="grid-line grid-line--col grid-line--thirds-exact" style="left: 33.333%;"></div>
          <div class="grid-line grid-line--col grid-line--thirds-exact" style="left: 66.666%;"></div>
          <div class="grid-line grid-line--row grid-line--thirds-exact" style="top: 33.333%;"></div>
          <div class="grid-line grid-line--row grid-line--thirds-exact" style="top: 66.666%;"></div>

          <!-- 5% Safe Area Box -->
          <div class="grid-safe-area"></div>

          <!-- Micro specs labels -->
          <div class="grid-watermark">12x8 ALIGNMENT GRID / 5% SAFE ACTIVE</div>
        </div>
      </div>
    </article>
  </section>
</template>

<script>
import { projectConfig } from '../config/project.js'
import DualCaseLayout from './layouts/DualCaseLayout.vue'

export default {
  name: 'SlideFrame',
  components: {
    DualCaseLayout,
  },
  props: {
    slide: {
      type: Object,
      required: true,
    },
    slideTotal: {
      type: Number,
      default: 1,
    },
  },
  inject: {
    gridState: {
      from: 'gridState',
      default: () => ({ active: false }),
    },
  },
  computed: {
    footerText() {
      return projectConfig.footerText
    },
    footerLeftText() {
      return projectConfig.footerLeftText
    },
    slideTotalPadded() {
      return String(this.slideTotal).padStart(2, '0')
    },
  },
}
</script>

<style scoped>
.slide-frame-wrap {
  width: 100%;
}

.slide-frame {
  width: 100%;
  max-width: var(--slide-max-width);
  margin: 0 auto;
}

.slide-frame__canvas {
  position: relative; /* Necessary for absolute grid overlay */
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
  border-radius: var(--slide-radius);
  box-shadow: var(--slide-shadow);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-frame__canvas:hover {
  box-shadow: 0 40px 80px -20px rgba(27, 25, 24, 0.14), 0 0 0 1px rgba(27, 25, 24, 0.04);
}

.slide-frame__header {
  flex-shrink: 0;
  padding: 16px 24px 12px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border-light);
}

.slide-frame__header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.slide-frame__section-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--type-caption);
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.badge-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: var(--color-accent);
}

.slide-frame__counter {
  font-family: var(--font-heading);
  font-size: var(--type-caption);
  font-weight: 600;
  color: var(--color-secondary);
  letter-spacing: 0.05em;
}

.slide-frame__header-main {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.slide-frame__title {
  margin: 0;
  font-family: var(--font-heading);
  font-size: var(--type-display);
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.1;
  letter-spacing: -0.01em;
}

.slide-frame__divider {
  width: 1px;
  height: 14px;
  background-color: var(--color-border);
  align-self: center;
}

.slide-frame__theme {
  margin: 0;
  font-size: var(--type-body);
  color: var(--color-secondary);
  font-weight: 500;
  letter-spacing: 0.02em;
}

.slide-frame__footer {
  flex-shrink: 0;
  padding: 6px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.5625rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--color-muted-text);
  background: var(--color-background);
  border-top: 1px solid var(--color-border-light);
}

.footer-left {
  font-family: var(--font-body);
  opacity: 0.8;
}

.footer-right {
  font-family: var(--font-body);
}

/* Alignment Grid Styles */
.alignment-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 10;
}

.grid-line {
  position: absolute;
  background: none;
}

.grid-line--col {
  top: 0;
  bottom: 0;
  border-left: 1px dashed rgba(90, 103, 110, 0.15);
}

.grid-line--row {
  left: 0;
  right: 0;
  border-top: 1px dashed rgba(90, 103, 110, 0.15);
}

/* Rule of Thirds Overlays (Copper Gold Highlight) */
.grid-line--thirds {
  border-color: rgba(184, 144, 71, 0.25) !important;
}

.grid-line--thirds-exact {
  border-color: rgba(194, 65, 12, 0.22) !important;
}

.grid-line--col.grid-line--thirds-exact {
  top: 0;
  bottom: 0;
  border-left-style: dashed;
}

.grid-line--row.grid-line--thirds-exact {
  left: 0;
  right: 0;
  border-top-style: dashed;
}

/* 5% Safe Area Frame */
.grid-safe-area {
  position: absolute;
  top: 5%;
  left: 5%;
  right: 5%;
  bottom: 5%;
  border: 1px dashed rgba(184, 144, 71, 0.3);
  border-radius: 2px;
}

.grid-watermark {
  position: absolute;
  bottom: 3%;
  right: 6%;
  font-size: 8px;
  font-family: var(--font-body);
  font-weight: 700;
  letter-spacing: 0.1em;
  color: rgba(184, 144, 71, 0.6);
  background: rgba(252, 251, 249, 0.85);
  padding: 1px 4px;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
</style>
