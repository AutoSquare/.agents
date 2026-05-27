<template>
  <div
    class="split-layout"
    :class="{
      'split-layout--browser': slide.imageFrame === 'browser',
      'split-layout--wide-callout': slide.calloutFullWidth,
      [`split-layout--${slide.variant}`]: slide.variant,
    }"
  >
    <div class="split-text export-layer-fg">
      <h2 class="split-title">{{ slide.title }}</h2>
      <p class="split-subtitle text-gradient" v-if="slide.subtitle">{{ slide.subtitle }}</p>

      <div class="split-content" v-html="renderedContent"></div>

      <div class="split-badges" v-if="slide.badges && slide.badges.length">
        <span class="pill-badge" v-for="badge in slide.badges" :key="badge">{{ badge }}</span>
      </div>

      <div class="split-callout glass-card" v-if="slide.callout">
        <p v-if="!calloutUrl">{{ slide.callout }}</p>
        <p v-else class="split-callout-row">
          <span>{{ calloutPrefix }}</span>
          <span class="url-pill">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="2" y1="12" x2="22" y2="12"></line>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
            </svg>
            {{ calloutUrl }}
          </span>
        </p>
      </div>
    </div>

    <div class="split-media">
      <div
        v-if="hasMedia"
        class="media-container export-layer-fg"
        :class="{
          'media-container--browser': slide.imageFrame === 'browser',
          'media-container--fixed-aspect': slide.imageAspect,
          [`media-container--${slide.variant}`]: slide.variant,
          'glass-card': slide.imageFrame !== 'browser',
        }"
        :style="mediaStyle"
      >
        <AssetImage
          :images="resolvedImages"
          :alt-base="slide.imageAlt"
          :fit="slide.imageFit || 'contain'"
          :frame-type="resolvedFrameType"
          :object-position="slide.imagePosition || 'center'"
          class="split-image"
        />
      </div>
    </div>
  </div>
</template>

<script>
import AssetImage from '../AssetImage.vue'
import { imageUrl } from '../../data/slides'

export default {
  name: 'SplitLayout',
  components: { AssetImage },
  props: {
    slide: { type: Object, required: true }
  },
  computed: {
    hasMedia() {
      return this.resolvedImages.length > 0
    },
    resolvedImages() {
      if (Array.isArray(this.slide.images) && this.slide.images.length) {
        return this.slide.images.map((f) => imageUrl(f))
      }
      if (this.slide.image) {
        return [imageUrl(this.slide.image)]
      }
      return []
    },
    resolvedFrameType() {
      if (this.slide.imageFrame === 'browser') return 'none'
      return this.slide.imageFrameType || 'paper'
    },
    mediaStyle() {
      if (!this.slide.imageAspect) return {}
      return { aspectRatio: this.slide.imageAspect }
    },
    calloutUrl() {
      if (!this.slide.callout) return ''
      const match = this.slide.callout.match(/https?:\/\/[^\s]+/)
      return match ? match[0] : ''
    },
    calloutPrefix() {
      if (!this.calloutUrl) return this.slide.callout
      return this.slide.callout.replace(this.calloutUrl, '').trim()
    },
    renderedContent() {
      if (!this.slide.content) return ''
      let html = this.slide.content
      html = html.replace(/### (.*)/g, '<h3>$1</h3>')
      html = html.replace(/- \*\*(.*?)\*\*：(.*)/g, '<li><strong>$1</strong>：$2</li>')
      html = html.replace(/- (.*)/g, '<li>$1</li>')
      html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
      return html
    }
  }
}
</script>

<style scoped>
.split-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 0.88fr 1.12fr;
  gap: 28px;
  padding: 24px 40px;
  min-height: 0;
  align-items: stretch;
  position: relative;
  z-index: 1;
}

.split-layout--browser {
  grid-template-columns: 0.68fr 1.32fr;
  gap: 20px;
  padding: 18px 32px 58px;
}

.split-layout--wide-callout {
  grid-template-columns: 0.72fr 1.28fr;
  gap: 22px;
  padding-bottom: 58px;
}

.split-layout--policy {
  grid-template-columns: 0.78fr 1.22fr;
  gap: 18px;
  padding: 18px 36px 68px;
}

.split-text {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-height: 0;
}

.split-title {
  font-size: 2.05rem;
  font-weight: 800;
  color: var(--color-primary);
  margin: 0 0 6px 0;
  letter-spacing: -0.045em;
  line-height: 1.05;
}

.split-subtitle {
  font-size: 1.02rem;
  font-weight: 700;
  margin: 0 0 18px 0;
}

.split-layout--browser .split-title {
  font-size: 1.78rem;
}

.split-layout--browser .split-subtitle {
  font-size: 0.9rem;
  margin-bottom: 12px;
}

.split-layout--policy .split-title {
  font-size: 1.92rem;
}

.split-layout--policy .split-subtitle {
  margin-bottom: 12px;
}

.split-content {
  font-size: 0.78rem;
  color: var(--color-secondary);
  line-height: 1.55;
  overflow: hidden;
}

.split-content :deep(h3) {
  font-size: 0.92rem;
  font-weight: 800;
  color: var(--color-primary);
  margin: 12px 0 6px 0;
}

.split-layout--browser .split-content {
  font-size: 0.7rem;
  line-height: 1.45;
}

.split-layout--browser .split-content :deep(h3) {
  font-size: 0.82rem;
  margin: 8px 0 4px 0;
}

.split-layout--browser .split-content :deep(ul) {
  margin-bottom: 8px;
}

.split-layout--browser .split-content :deep(li) {
  margin-bottom: 3px;
}

.split-layout--policy .split-content {
  font-size: 0.73rem;
  line-height: 1.42;
}

.split-layout--policy .split-content :deep(h3) {
  font-size: 0.86rem;
  margin: 10px 0 4px;
}

.split-content :deep(h3:first-child) {
  margin-top: 0;
}

.split-content :deep(ul) {
  padding-left: 16px;
  margin: 0 0 12px 0;
}

.split-content :deep(li) {
  margin-bottom: 4px;
  padding-left: 2px;
}

.split-content :deep(strong) {
  color: var(--color-accent);
}

.split-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.split-layout--browser .split-badges {
  gap: 6px;
  margin-top: 8px;
}

.split-callout {
  margin-top: auto;
  padding: 12px 16px;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.1), rgba(124, 58, 237, 0.06));
  border-left: 3px solid var(--color-accent);
  border-radius: 12px;
}

.split-layout--browser .split-callout {
  position: absolute;
  left: 32px;
  right: 32px;
  bottom: 18px;
  margin-top: 0;
  padding: 10px 16px;
  border-radius: 14px;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.08), rgba(124, 58, 237, 0.05));
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-left: 3px solid var(--color-accent);
  box-shadow: none;
  z-index: 2;
}

.split-layout--wide-callout .split-callout {
  position: absolute;
  left: 40px;
  right: 40px;
  bottom: 18px;
  margin-top: 0;
  padding: 10px 16px;
  border-radius: 14px;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.08), rgba(124, 58, 237, 0.05));
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-left: 3px solid var(--color-accent);
  box-shadow: none;
  z-index: 2;
}

.split-layout--wide-callout .split-callout p {
  font-size: 0.72rem;
  font-weight: 800;
}

.split-layout--policy .split-callout {
  left: 36px;
  right: 36px;
  bottom: 16px;
}

.split-layout--policy .split-callout p {
  font-size: 0.68rem;
}

.split-layout--browser .split-callout-row {
  justify-content: flex-start;
  flex-wrap: nowrap;
  gap: 12px;
}

.split-layout--browser .split-callout p {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--color-primary);
}

.split-layout--browser .split-callout-row > span:first-child {
  flex: 0 0 auto;
  padding: 0;
  border-radius: 0;
  background: transparent;
  color: var(--color-primary);
  font-weight: 800;
  letter-spacing: 0;
}

.split-layout--browser .url-pill {
  flex: 0 1 auto;
  justify-content: flex-start;
  max-width: none;
  padding: 0;
  background: transparent;
  border: 0;
  border-radius: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-accent);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.split-callout p {
  margin: 0;
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--color-primary);
}

.split-callout-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.split-media {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
}

.media-container {
  width: 100%;
  height: 100%;
  min-height: 0;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.86)),
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.12), transparent 42%);
  border-color: rgba(37, 99, 235, 0.18);
  position: relative;
  overflow: hidden;
}

.media-container--browser {
  width: min(100%, 590px);
  height: auto;
  max-height: 100%;
  aspect-ratio: 16 / 9;
  align-self: center;
  flex-shrink: 0;
  padding: 5px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  border: 1px solid rgba(148, 163, 184, 0.28);
  box-shadow: 0 32px 80px rgba(15, 23, 42, 0.28);
  border-radius: 16px;
  box-sizing: border-box;
}

.media-container--fixed-aspect {
  height: auto;
  max-height: 100%;
  align-self: center;
  flex-shrink: 0;
}

.media-container--policy {
  width: auto;
  height: min(100%, 360px);
  max-width: 100%;
  padding: 8px;
}

.media-container--policy :deep(.asset-image__frame) {
  background: #ffffff;
}

.media-container--policy :deep(.asset-image__img) {
  padding: 2px;
}

.media-container--fixed-aspect :deep(.asset-image),
.media-container--fixed-aspect :deep(.asset-image__frame) {
  height: 100%;
}

.media-container--browser::before {
  display: none;
}

.media-container--browser::after {
  display: none;
}

.media-container--browser :deep(.asset-image) {
  flex: 1;
  min-height: 0;
  height: 100%;
}

.media-container--browser :deep(.asset-image__frame) {
  flex: 1;
  height: 100%;
  background: #ffffff;
  border-radius: 11px;
  border: 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

.media-container--browser :deep(.asset-image__img) {
  min-height: 0;
  object-fit: contain;
  object-position: center center;
}

.split-image {
  width: 100%;
  height: 100%;
}
</style>
