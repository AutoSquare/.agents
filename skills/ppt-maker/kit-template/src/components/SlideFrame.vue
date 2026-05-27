<template>
  <section
    class="slide-frame-wrap"
    :aria-labelledby="`slide-title-${slide.id}`"
  >
    <article class="slide-frame">
      <div class="slide-frame__canvas">
        <div
          class="export-layer-bg slide-canvas-backdrop mesh-bg"
          aria-hidden="true"
        ></div>
        <header
          class="slide-frame__header export-layer-fg"
          v-if="!['cover', 'catalog', 'statement'].includes(slide.layout)"
        >
          <div class="slide-frame__header-top">
            <span class="slide-frame__section-badge">
              <span class="badge-dot"></span>
              {{ sectionBadge }}
            </span>
          </div>
        </header>
        <component
          :is="layoutComponent"
          :slide="slide"
          :lazy-load="slide.layout !== 'cover'"
        />
        <footer
          class="slide-frame__footer export-layer-fg"
          aria-hidden="true"
          v-if="!['cover', 'catalog'].includes(slide.layout)"
        >
          <span class="footer-left">{{ footerLeftText }}</span>
          <span class="footer-right">{{ footerText }}</span>
        </footer>
      </div>
    </article>
  </section>
</template>

<script>
import { projectConfig } from '../config/project.js'
import CoverLayout from './layouts/CoverLayout.vue'
import CatalogLayout from './layouts/CatalogLayout.vue'
import StatementLayout from './layouts/StatementLayout.vue'
import FeaturesLayout from './layouts/FeaturesLayout.vue'
import SplitLayout from './layouts/SplitLayout.vue'
import DualCaseLayout from './layouts/DualCaseLayout.vue'
import EvidenceLayout from './layouts/EvidenceLayout.vue'

export default {
  name: 'SlideFrame',
  components: {
    CoverLayout,
    CatalogLayout,
    StatementLayout,
    FeaturesLayout,
    SplitLayout,
    DualCaseLayout,
    EvidenceLayout,
  },
  props: {
    slide: {
      type: Object,
      required: true,
    },
  },
  computed: {
    layoutComponent() {
      const map = {
        cover: 'CoverLayout',
        catalog: 'CatalogLayout',
        statement: 'StatementLayout',
        features: 'FeaturesLayout',
        split: 'SplitLayout',
        dual: 'DualCaseLayout',
        evidence: 'EvidenceLayout',
      }
      return map[this.slide.layout] || 'DualCaseLayout'
    },
    footerText() {
      return projectConfig.footerText
    },
    footerLeftText() {
      return projectConfig.footerLeftText
    },
    sectionBadge() {
      return projectConfig.sectionBadge || projectConfig.appSubtitle
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
  position: relative;
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  border-radius: var(--slide-radius);
  box-shadow: var(--slide-shadow);
  border: 1px solid rgba(37, 99, 235, 0.14);
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-frame__canvas:hover {
  box-shadow: 0 40px 100px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(37, 99, 235, 0.18);
}

.slide-canvas-backdrop {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.slide-canvas-backdrop::after {
  content: '';
  position: absolute;
  inset: 12px;
  border: 1px solid rgba(255, 255, 255, 0.62);
  border-radius: calc(var(--slide-radius) - 8px);
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.05);
  pointer-events: none;
}

.slide-frame__canvas > :not(.slide-canvas-backdrop) {
  position: relative;
  z-index: 1;
}

.slide-frame__header {
  flex-shrink: 0;
  padding: 24px 40px 0;
  background: transparent;
}

.slide-frame__header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.slide-frame__section-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: 0.15em;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-accent);
  box-shadow: 0 0 8px var(--color-accent);
}

.slide-frame__footer {
  flex-shrink: 0;
  padding: 16px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--color-muted-text);
  background: transparent;
}

.footer-left,
.footer-right {
  font-family: var(--font-body);
}
</style>
