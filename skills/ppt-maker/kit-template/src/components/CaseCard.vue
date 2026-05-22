<template>
  <article class="case-card">
    <!-- Title Meta Stack (Always at the top) -->
    <header class="case-card__header">
      <div class="case-card__meta">
        <span class="case-card__index">CASE // {{ caseItem.index }}</span>
        <div class="case-card__title-group">
          <h3 class="case-card__name">{{ caseItem.name }}</h3>
          <p class="case-card__subtitle">{{ caseItem.subtitle }}</p>
        </div>
      </div>
    </header>

    <!-- Media Container -->
    <div class="case-card__media">
      <AssetImage
        :images="caseItem.images.map(imageUrl)"
        :alt-base="caseItem.name"
        :lazy="lazyLoad"
        :failed="imageFailed"
        :fit="caseItem.imageFit || 'contain'"
        :frame-type="caseItem.imageFrameType || 'paper'"
        @error="imageFailed = true"
      />
    </div>

    <!-- Description (In the body) -->
    <div class="case-card__body">
      <p v-if="caseItem.description" class="case-card__desc">{{ caseItem.description }}</p>

      <!-- Technical Specifications dot-leader Grid (Metadata Matrix) -->
      <section v-if="caseItem.metadata && caseItem.metadata.length" class="case-card__specs" aria-label="技术指标矩阵">
        <div v-for="spec in caseItem.metadata" :key="spec.label" class="spec-row">
          <span class="spec-label">{{ spec.label }}</span>
          <span class="spec-dot-leader"></span>
          <span class="spec-value">{{ spec.value }}</span>
        </div>
      </section>

      <!-- Pill Tags -->
      <CaseTags :tags="caseItem.tags" />
    </div>
  </article>
</template>

<script>
import CaseTags from './CaseTags.vue'
import AssetImage from './AssetImage.vue'
import { imageUrl } from '../data/slides'

export default {
  name: 'CaseCard',
  components: {
    CaseTags,
    AssetImage,
  },
  props: {
    caseItem: {
      type: Object,
      required: true,
    },
    lazyLoad: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      imageFailed: false,
    }
  },
  methods: {
    imageUrl,
  },
}
</script>

<style scoped>
.case-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: transparent; /* Seamlessly integrated with canvas */
}

.case-card__header {
  flex-shrink: 0;
  margin-bottom: 12px;
}

.case-card__meta {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.case-card__index {
  flex-shrink: 0;
  font-family: var(--font-body);
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--color-accent);
  background: var(--color-accent-light);
  border: 1px solid rgba(184, 144, 71, 0.15);
  padding: 3px 6px;
  border-radius: 2px;
}

.case-card__title-group {
  display: flex;
  flex-direction: column;
}

.case-card__name {
  margin: 0;
  font-family: var(--font-heading);
  font-size: var(--type-title);
  font-weight: 700;
  color: var(--color-foreground);
  line-height: 1.15;
}

.case-card__subtitle {
  margin: 2px 0 0;
  font-family: var(--font-body);
  font-size: var(--type-caption);
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.case-card__media {
  flex: 1;
  min-height: 0;
  display: flex;
  position: relative;
  margin-bottom: 12px;
}

.case-card__body {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.case-card__desc {
  margin: 0 0 12px;
  font-size: var(--type-caption);
  color: var(--color-secondary);
  line-height: 1.45;
  font-weight: 500;
}

/* Metadata matrix with elegant dot-leaders */
.case-card__specs {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
  border-top: 1px dashed var(--color-border-light);
  padding-top: 10px;
}

.spec-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  font-size: 0.6875rem; /* Micro size */
}

.spec-label {
  color: var(--color-muted-text);
  font-weight: 500;
  letter-spacing: 0.01em;
}

.spec-dot-leader {
  flex: 1;
  border-bottom: 1px dotted var(--color-border);
  margin: 0 6px;
  opacity: 0.5;
}

.spec-value {
  color: var(--color-foreground);
  font-family: var(--font-body);
  font-weight: 700;
  text-align: right;
  letter-spacing: 0.01em;
}
</style>
