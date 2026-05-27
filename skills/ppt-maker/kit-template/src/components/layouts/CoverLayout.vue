<template>
  <div class="cover-layout">
    <div class="export-layer-bg cover-glow cover-glow--tr" aria-hidden="true"></div>
    <div class="export-layer-bg cover-glow cover-glow--bl" aria-hidden="true"></div>
    <div class="cover-kicker export-layer-fg">{{ slide.kicker || sectionBadge }}</div>
    <div class="cover-partner export-layer-fg" v-if="slide.partnerLogo">
      <img :src="imageUrl(slide.partnerLogo)" :alt="slide.partnerLogoAlt || 'Partner logo'" class="cover-partner-logo" />
    </div>
    <div class="cover-content export-layer-fg">
      <div class="cover-logo-wrap" v-if="slide.image">
        <AssetImage
          :images="[imageUrl(slide.image)]"
          :alt-base="slide.imageAlt"
          fit="contain"
          frame-type="none"
          :lazy="false"
          hero-logo
          class="cover-logo"
        />
      </div>
      <h1 class="cover-title">{{ slide.subtitle }}</h1>
      <p class="cover-desc">{{ slide.description }}</p>
    </div>
    <div
      class="cover-meta export-layer-fg"
      v-if="slide.meta"
      :style="metaGridStyle"
    >
      <div class="meta-item" v-for="item in slide.meta" :key="item.label">
        <span class="meta-label">{{ item.label }}</span>
        <span class="meta-value">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import AssetImage from '../AssetImage.vue'
import { imageUrl } from '../../data/slides'
import { projectConfig } from '../../config/project.js'

export default {
  name: 'CoverLayout',
  components: { AssetImage },
  props: {
    slide: { type: Object, required: true },
  },
  computed: {
    sectionBadge() {
      return projectConfig.sectionBadge || projectConfig.appSubtitle
    },
    metaGridStyle() {
      const count = this.slide.meta?.length || 0
      if (count <= 0) return {}
      return {
        gridTemplateColumns: `repeat(${count}, minmax(0, 1fr))`,
      }
    },
  },
  methods: { imageUrl },
}
</script>

<style scoped>
.cover-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2.5em 3.5em 6.25em;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.cover-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(6px);
  pointer-events: none;
}

.cover-glow--tr {
  width: 360px;
  height: 360px;
  right: -88px;
  top: -96px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.18), transparent 62%);
}

.cover-glow--bl {
  width: 420px;
  height: 420px;
  left: -150px;
  bottom: -180px;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.14), transparent 64%);
}

.cover-kicker {
  position: absolute;
  top: 2.125em;
  left: 2.75em;
  z-index: 2;
  color: var(--color-accent);
  font-size: 0.72em;
  font-weight: 700;
  letter-spacing: 0.26em;
}

.cover-partner {
  position: absolute;
  top: 1.75em;
  right: 2.75em;
  z-index: 2;
}

.cover-partner-logo {
  height: 3em;
  width: auto;
  object-fit: contain;
  filter: drop-shadow(0 8px 20px rgba(15, 23, 42, 0.12));
}

.cover-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25em;
  max-width: 52.5em;
  z-index: 2;
}

.cover-logo-wrap {
  width: min(82%, 42.5em);
  display: flex;
  justify-content: center;
  align-items: center;
}

.cover-logo {
  width: 100%;
  filter: drop-shadow(0 20px 48px rgba(37, 99, 235, 0.18));
}

.cover-title {
  font-size: 2em;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--color-primary);
  margin: 0;
  line-height: 1.15;
}

.cover-desc {
  max-width: 38.75em;
  font-size: 0.9em;
  color: var(--color-secondary);
  line-height: 1.5;
  margin: 0;
  white-space: pre-line;
}

.cover-meta {
  position: absolute;
  left: 2.5em;
  right: 2.5em;
  bottom: 1.875em;
  display: grid;
  gap: 0.625em;
  z-index: 2;
}

.meta-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.125em;
  padding: 0.625em 0.75em;
  text-align: left;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(37, 99, 235, 0.14);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
}

.meta-label {
  font-size: 0.58em;
  font-weight: 700;
  color: var(--color-muted-text);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.meta-value {
  font-size: 0.72em;
  font-weight: 600;
  color: var(--color-primary);
}
</style>
