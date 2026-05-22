<template>
  <div
    class="asset-image"
    :class="{
      'asset-image--multi': images.length > 1,
      'asset-image--contain': fit === 'contain',
    }"
  >
    <div
      v-for="(src, i) in images"
      :key="src"
      class="asset-image__frame"
      :class="[
        `asset-image__frame--${frameType}`,
        { 'asset-image__frame--clickable': openLightbox }
      ]"
      @click="handleImageClick(src)"
    >
      <img
        :src="src"
        :alt="`${altBase}${images.length > 1 ? ` 图${i + 1}` : ''}`"
        class="asset-image__img"
        :loading="lazy ? 'lazy' : 'eager'"
        @error="$emit('error')"
      />

      <!-- Hover interactive glass overlay -->
      <div v-if="openLightbox" class="asset-image__overlay">
        <span class="overlay-text">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="overlay-icon">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="11" y1="8" x2="11" y2="14"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
          点击查阅细节解译
        </span>
      </div>

      <!-- Heterogeneous HUD Corner indicators -->
      <template v-if="frameType === 'hud'">
        <div class="hud-corner hud-corner--tl"></div>
        <div class="hud-corner hud-corner--tr"></div>
        <div class="hud-corner hud-corner--bl"></div>
        <div class="hud-corner hud-corner--br"></div>
        <div class="hud-crosshair"></div>
      </template>

      <!-- Heterogeneous Paper Gold Crop corner marks -->
      <template v-else-if="frameType === 'paper'">
        <div class="crop-mark crop-mark--tl"></div>
        <div class="crop-mark crop-mark--tr"></div>
        <div class="crop-mark crop-mark--bl"></div>
        <div class="crop-mark crop-mark--br"></div>
      </template>
    </div>

    <!-- Loading failure fallback -->
    <div v-if="failed" class="asset-image__fallback">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="fallback-icon">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <circle cx="8.5" cy="8.5" r="1.5"></circle>
        <polyline points="21 15 16 10 5 21"></polyline>
      </svg>
      <span>参考素材暂未就绪 / 勘测底图占位</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetImage',
  props: {
    images: {
      type: Array,
      required: true,
    },
    altBase: {
      type: String,
      default: '',
    },
    lazy: {
      type: Boolean,
      default: false,
    },
    failed: {
      type: Boolean,
      default: false,
    },
    fit: {
      type: String,
      default: 'contain',
    },
    frameType: {
      type: String,
      default: 'paper',
      validator: (v) => ['paper', 'hud'].includes(v),
    },
  },
  emits: ['error'],
  inject: {
    openLightbox: {
      from: 'openLightbox',
      default: null,
    },
  },
  methods: {
    handleImageClick(src) {
      if (this.openLightbox) {
        this.openLightbox(src, this.altBase)
      }
    },
  },
}
</script>

<style scoped>
.asset-image {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 8px;
  width: 100%;
}

.asset-image--multi {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.asset-image__frame {
  position: relative; /* Anchor for corners and overlays */
  margin: 0;
  flex: 1;
  min-height: 0;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: var(--card-radius);
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

/* IMAGE FRAME STYLE 1: HUD Sci-Tech Dark Terminal */
.asset-image__frame--hud {
  background: #090D16;
  border: 1px solid rgba(14, 116, 144, 0.25);
  box-shadow: inset 0 0 16px rgba(14, 116, 144, 0.08);
}

.asset-image__frame--hud .asset-image__img {
  filter: saturate(1.1) contrast(1.02);
  padding: 2px;
}

/* IMAGE FRAME STYLE 2: Premium Editorial Paper with Copper Brackets */
.asset-image__frame--paper {
  background: #FDFDFB;
  border: 1px solid var(--color-border);
  box-shadow: 0 4px 16px rgba(27, 25, 24, 0.03);
}

.asset-image__frame--paper .asset-image__img {
  padding: 4px;
}

/* Clickable hover states */
.asset-image__frame--clickable {
  cursor: pointer;
}

.asset-image__frame--clickable:hover {
  transform: scale(1.015);
}

.asset-image__frame--hud.asset-image__frame--clickable:hover {
  border-color: rgba(14, 116, 144, 0.65);
  box-shadow: 0 8px 24px rgba(14, 116, 144, 0.12), inset 0 0 20px rgba(14, 116, 144, 0.15);
}

.asset-image__frame--paper.asset-image__frame--clickable:hover {
  border-color: var(--color-accent);
  box-shadow: 0 12px 28px -4px rgba(184, 144, 71, 0.08), 0 0 0 1px rgba(184, 144, 71, 0.1);
}

/* Crop marks for Paper Frame */
.crop-mark {
  position: absolute;
  width: 6px;
  height: 6px;
  border: 1px solid var(--color-accent);
  pointer-events: none;
  opacity: 0.85;
}

.crop-mark--tl { top: 4px; left: 4px; border-right: none; border-bottom: none; }
.crop-mark--tr { top: 4px; right: 4px; border-left: none; border-bottom: none; }
.crop-mark--bl { bottom: 4px; left: 4px; border-right: none; border-top: none; }
.crop-mark--br { bottom: 4px; right: 4px; border-left: none; border-top: none; }

/* HUD Corner markers for HUD Frame */
.hud-corner {
  position: absolute;
  width: 5px;
  height: 5px;
  border: 1.5px solid #06B6D4; /* Bright cyan */
  pointer-events: none;
  opacity: 0.9;
}

.hud-corner--tl { top: 3px; left: 3px; border-right: none; border-bottom: none; }
.hud-corner--tr { top: 3px; right: 3px; border-left: none; border-bottom: none; }
.hud-corner--bl { bottom: 3px; left: 3px; border-right: none; border-top: none; }
.hud-corner--br { bottom: 3px; right: 3px; border-left: none; border-top: none; }

.hud-crosshair {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  pointer-events: none;
  opacity: 0.15;
}
.hud-crosshair::before, .hud-crosshair::after {
  content: '';
  position: absolute;
  background-color: #06B6D4;
}
.hud-crosshair::before { top: 4px; left: 0; width: 10px; height: 2px; }
.hud-crosshair::after { top: 0; left: 4px; width: 2px; height: 10px; }

/* Image positioning styles */
.asset-image__img {
  width: 100%;
  height: 100%;
  min-height: 120px;
  object-fit: cover;
  display: block;
  transition: transform var(--transition-fast);
}

.asset-image--contain .asset-image__img {
  object-fit: contain;
}

/* Elegant glassmorphism hover overlay */
.asset-image__overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 30, 36, 0.4);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-fast);
  pointer-events: none; /* Let click pass through to the frame */
}

.asset-image__frame:hover .asset-image__overlay {
  opacity: 1;
}

.overlay-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-body);
  font-size: 0.6875rem;
  font-weight: 700;
  color: #FCFBF9;
  letter-spacing: 0.08em;
  background: rgba(184, 144, 71, 0.85); /* Accent gold banner */
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(15, 30, 36, 0.15);
}

.overlay-icon {
  stroke-width: 3px;
}

/* Loading error fallback styling */
.asset-image__fallback {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 140px;
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--color-muted-text);
  background: var(--color-surface);
  border: 1px dashed var(--color-border);
  border-radius: var(--card-radius);
  padding: 12px;
  text-align: center;
}

.fallback-icon {
  opacity: 0.6;
  color: var(--color-accent);
}

@media (max-width: 640px) {
  .asset-image--multi {
    grid-template-columns: 1fr;
  }
}
</style>
