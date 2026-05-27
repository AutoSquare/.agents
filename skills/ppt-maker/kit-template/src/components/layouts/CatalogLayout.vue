<template>
  <div class="catalog-layout">
    <div class="catalog-header export-layer-fg">
      <h2 class="catalog-title">{{ slide.title }}</h2>
      <p class="catalog-subtitle text-gradient">{{ slide.subtitle }}</p>
    </div>

    <div class="catalog-body">
      <div class="catalog-list">
        <div class="catalog-item export-layer-fg" v-for="item in slide.items" :key="item.number">
          <div class="item-number">{{ item.number }}</div>
          <div class="item-title">{{ item.title }}</div>
          <div class="item-line"></div>
        </div>
      </div>

      <div class="catalog-preview" v-if="slide.catalogPreview && previewTiles.length">
        <div class="catalog-preview-grid" :class="previewGridClass">
          <div
            class="preview-card glass-card export-layer-fg"
            v-for="(item, idx) in previewTiles"
            :key="`${item.label}-${idx}`"
          >
            <img v-if="item.image" :src="imageUrl(item.image)" :alt="item.label" class="preview-image" loading="lazy" />
            <span class="preview-label">{{ item.label }}</span>
          </div>
          <div class="preview-hub pill-badge export-layer-fg" v-if="hubLabel">{{ hubLabel }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { imageUrl } from '../../data/slides'

export default {
  name: 'CatalogLayout',
  props: {
    slide: { type: Object, required: true }
  },
  computed: {
    previewTiles() {
      if (!this.slide.catalogPreview) return []
      return this.slide.catalogPreview.filter((item) => item.image)
    },
    hubLabel() {
      if (!this.slide.catalogPreview) return ''
      const hub = this.slide.catalogPreview.find((item) => item.hub)
      return hub ? hub.hub : ''
    },
    previewGridClass() {
      const count = this.previewTiles.length
      if (count >= 4) return 'catalog-preview-grid--quad'
      return `catalog-preview-grid--count-${count}`
    },
  },
  methods: { imageUrl }
}
</script>

<style scoped>
.catalog-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 32px 56px 28px;
  position: relative;
  z-index: 1;
  min-height: 0;
  overflow: hidden;
}

.catalog-header {
  flex-shrink: 0;
  margin-bottom: 18px;
}

.catalog-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--color-primary);
  margin: 0 0 6px 0;
  letter-spacing: -0.055em;
  line-height: 1;
}

.catalog-subtitle {
  font-size: 0.875rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.1em;
}

.catalog-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  align-items: center;
  min-height: 0;
  overflow: hidden;
}

.catalog-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.catalog-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(37, 99, 235, 0.16);
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  border-left: 3px solid var(--color-accent);
}

.item-number {
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-accent);
  width: 28px;
  flex-shrink: 0;
}

.item-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.25;
}

.item-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--color-border) 0%, transparent 100%);
}

.catalog-preview {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  height: 100%;
}

.catalog-preview-grid {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  flex: 1;
  min-height: 0;
  align-content: center;
}

.catalog-preview-grid--quad {
  grid-template-rows: 1fr 1fr;
}

.catalog-preview-grid--count-3 {
  grid-template-rows: 1fr 1fr;
}

.catalog-preview-grid--count-3 .preview-card:nth-child(3) {
  grid-column: 1 / -1;
  max-width: calc(50% - 6px);
  justify-self: center;
}

.catalog-preview-grid--count-2 {
  grid-template-rows: 1fr;
}

.preview-card {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  flex: 1;
  min-height: 0;
  max-height: 76px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid rgba(37, 99, 235, 0.12);
}

.catalog-preview-grid--quad .preview-image {
  max-height: 82px;
}

.preview-label {
  flex-shrink: 0;
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.2;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-hub {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 8px 16px;
  white-space: nowrap;
  max-width: calc(100% - 24px);
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.14);
  border: 1px solid rgba(37, 99, 235, 0.2);
}

.catalog-preview-grid--count-3 .preview-hub {
  position: static;
  grid-column: 2;
  grid-row: 2;
  transform: none;
  justify-self: center;
  align-self: center;
}
</style>
