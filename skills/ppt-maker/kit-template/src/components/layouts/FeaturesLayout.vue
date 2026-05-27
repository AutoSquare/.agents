<template>
  <div
    class="features-layout"
    :class="{
      'features-layout--duo': isDuo,
      'features-layout--flow': isFlowStyle,
    }"
  >
    <div class="features-header export-layer-fg">
      <h2 class="features-title">{{ slide.title }}</h2>
      <p class="features-subtitle text-gradient" v-if="slide.subtitle">{{ slide.subtitle }}</p>
    </div>

    <div class="duo-flow" v-if="isDuo">
      <article class="duo-flow-card glass-card export-layer-fg" v-if="slide.features[0]">
        <div class="duo-flow-icon" v-html="iconSvg(slide.features[0].icon)"></div>
        <span class="duo-flow-kicker">{{ slide.features[0].kicker || 'PC 端' }}</span>
        <h3>{{ normalizeDuoTitle(slide.features[0].title) }}</h3>
        <p>{{ slide.features[0].description }}</p>
        <div class="feature-tags" v-if="slide.features[0].tags && slide.features[0].tags.length">
          <span class="stat-chip" v-for="tag in slide.features[0].tags" :key="tag">{{ tag }}</span>
        </div>
      </article>

      <aside class="duo-flow-hub glass-card export-layer-fg" v-if="slide.duoPanel">
        <div class="duo-flow-hub__icons">
          <div class="duo-icon-wrap" v-html="duoPanelIcon(0)"></div>
          <span class="duo-flow-arrow">↔</span>
          <div class="duo-icon-wrap" v-html="duoPanelIcon(1)"></div>
        </div>
        <h3>{{ slide.duoPanel.title }}</h3>
        <ul>
          <li v-for="(bullet, i) in slide.duoPanel.bullets" :key="i">{{ bullet }}</li>
        </ul>
      </aside>

      <article class="duo-flow-card glass-card export-layer-fg" v-if="slide.features[1]">
        <div class="duo-flow-icon" v-html="iconSvg(slide.features[1].icon)"></div>
        <span class="duo-flow-kicker">{{ slide.features[1].kicker || '移动端' }}</span>
        <h3>{{ normalizeDuoTitle(slide.features[1].title) }}</h3>
        <p>{{ slide.features[1].description }}</p>
        <div class="feature-tags" v-if="slide.features[1].tags && slide.features[1].tags.length">
          <span class="stat-chip" v-for="tag in slide.features[1].tags" :key="tag">{{ tag }}</span>
        </div>
      </article>
    </div>

    <div
      class="duo-flow duo-flow--feature"
      :class="`duo-flow--count-${featureCount}`"
      v-else-if="isFlowStyle"
    >
      <article class="duo-flow-card glass-card export-layer-fg" v-for="(feat, idx) in slide.features" :key="idx">
        <div class="flow-card-head">
          <div class="duo-flow-icon" v-html="iconSvg(feat.icon)"></div>
          <span class="duo-flow-kicker">{{ formatIndex(idx) }}</span>
        </div>
        <h3>{{ feat.title }}</h3>
        <p>{{ feat.description }}</p>
        <div class="feature-tags" v-if="feat.tags && feat.tags.length">
          <span class="stat-chip" v-for="tag in feat.tags" :key="tag">{{ tag }}</span>
        </div>
      </article>
    </div>

    <div class="features-body" v-else>
      <div
        class="features-grid"
        :class="{
          'features-grid--quad': featureCount === 4,
        }"
        :style="gridStyle"
      >
        <div
          class="feature-card glass-card export-layer-fg"
          :class="{ 'feature-card--compact': featureCount === 4 }"
          v-for="(feat, idx) in slide.features"
          :key="idx"
        >
          <div class="feature-index pill-badge">{{ formatIndex(idx) }}</div>
          <div class="feature-icon" v-if="feat.icon">
            <div class="icon-circle" v-html="iconSvg(feat.icon)"></div>
          </div>
          <h3 class="feature-title">{{ feat.title }}</h3>
          <p class="feature-desc">{{ feat.description }}</p>
          <div class="feature-tags" v-if="feat.tags && feat.tags.length">
            <span class="stat-chip" v-for="tag in feat.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </div>

    </div>

    <div class="flow-bar export-layer-fg" v-if="slide.flowBar && slide.flowBar.length">
      <template v-for="(step, i) in slide.flowBar" :key="step">
        <span class="flow-bar__step">{{ step }}</span>
        <span class="flow-bar__arrow" v-if="i < slide.flowBar.length - 1" aria-hidden="true">→</span>
      </template>
    </div>

    <div class="features-callout glass-card export-layer-fg" v-if="slide.callout">
      <p>{{ slide.callout }}</p>
    </div>
  </div>
</template>

<script>
const ICONS = {
  AlertTriangle: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
  Layers: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 12 12 17 22 12"></polyline><polyline points="2 17 12 22 22 17"></polyline></svg>',
  Users: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
  Box: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>',
  Activity: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
  Shield: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
  Radio: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="2"></circle><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"></path></svg>',
  Monitor: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
  Smartphone: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>',
  Cpu: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>',
  Database: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
  Share2: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>',
  Briefcase: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>',
  BookOpen: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>',
}

export default {
  name: 'FeaturesLayout',
  props: {
    slide: { type: Object, required: true }
  },
  computed: {
    featureCount() {
      return this.slide.features ? this.slide.features.length : 0
    },
    isDuo() {
      return this.featureCount === 2 && !!this.slide.duoPanel
    },
    isFlowStyle() {
      return this.slide.featureStyle === 'flow' && !this.isDuo
    },
    columns() {
      if (this.isDuo) return 1
      if (this.featureCount === 4) return 2
      if (this.featureCount === 3) return 3
      return 2
    },
    gridStyle() {
      if (this.isDuo) return {}
      return { gridTemplateColumns: `repeat(${this.columns}, 1fr)` }
    }
  },
  methods: {
    formatIndex(idx) {
      return String(idx + 1).padStart(2, '0')
    },
    iconSvg(name) {
      const svg = ICONS[name]
      if (!svg) return ''
      return svg.replace('stroke="currentColor"', 'stroke="var(--color-accent)"')
    },
    normalizeDuoTitle(title) {
      return title.replace('PC 端：', '').replace('移动端：', '')
    },
    duoPanelIcon(index) {
      const fallback = index === 0 ? 'Monitor' : 'Smartphone'
      const name = this.slide.duoPanel?.icons?.[index] || fallback
      return this.iconSvg(name)
    }
  }
}
</script>

<style scoped>
.features-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px 38px 22px;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.features-layout--duo {
  justify-content: flex-start;
  padding-bottom: 58px;
}

.features-layout--flow {
  justify-content: flex-start;
  padding-bottom: 72px;
}

.features-layout--duo .features-body {
  flex: 0 1 auto;
  min-height: auto;
}

.features-layout--duo .features-header {
  margin-bottom: 10px;
}

.features-layout--flow .features-header {
  margin-bottom: 10px;
}

.features-header {
  margin-bottom: 14px;
}

.features-title {
  font-size: 1.96rem;
  font-weight: 800;
  color: var(--color-primary);
  margin: 0 0 6px 0;
  letter-spacing: -0.045em;
  line-height: 1;
}

.features-subtitle {
  font-size: 0.96rem;
  font-weight: 700;
  margin: 0;
}

.features-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.features-body--duo {
  display: grid;
  grid-template-columns: 58% 42%;
  gap: 16px;
  align-items: start;
  flex: 0 1 auto;
  min-height: auto;
}

.duo-flow {
  display: grid;
  grid-template-columns: 1fr 0.92fr 1fr;
  gap: 18px;
  align-items: stretch;
  min-height: 0;
}

.duo-flow--feature {
  grid-template-columns: repeat(3, 1fr);
  flex: 1;
  align-items: start;
}

.duo-flow--count-4 {
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.duo-flow--feature .duo-flow-card {
  display: flex;
  flex-direction: column;
  min-height: 236px;
  padding: 18px 18px 16px;
  background:
    radial-gradient(circle at 18% 12%, rgba(37, 99, 235, 0.09), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.92));
}

.flow-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.duo-flow--feature .duo-flow-icon {
  margin-bottom: 0;
}

.duo-flow--feature .duo-flow-kicker {
  min-width: 34px;
  height: 26px;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.18);
}

.duo-flow--feature .duo-flow-card h3 {
  margin-bottom: 12px;
}

.duo-flow--feature .feature-tags {
  margin-top: auto;
  padding-top: 16px;
}

.duo-flow-card,
.duo-flow-hub {
  position: relative;
  min-height: 220px;
  padding: 18px 18px 16px;
  overflow: hidden;
}

.duo-flow-card::before,
.duo-flow-hub::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, var(--color-accent), var(--color-accent-warm));
}

.duo-flow-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.11), rgba(124, 58, 237, 0.1));
  border: 1px solid rgba(37, 99, 235, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.duo-flow-kicker {
  display: inline-flex;
  margin-bottom: 6px;
  color: var(--color-accent);
  font-size: 0.68rem;
  font-weight: 800;
}

.duo-flow-card h3,
.duo-flow-hub h3 {
  margin: 0 0 10px;
  color: var(--color-primary);
  font-size: 1.02rem;
  font-weight: 800;
}

.duo-flow-card p {
  margin: 0;
  color: var(--color-secondary);
  font-size: 0.72rem;
  line-height: 1.48;
}

.duo-flow--count-4 .duo-flow-card {
  min-height: 224px;
  padding: 16px 16px 14px;
}

.duo-flow--count-4 .duo-flow-card h3 {
  font-size: 0.9rem;
}

.duo-flow--count-4 .duo-flow-card p {
  font-size: 0.66rem;
  line-height: 1.42;
}

.duo-flow-hub {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background:
    radial-gradient(circle at 50% 18%, rgba(37, 99, 235, 0.13), transparent 36%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.9));
}

.duo-flow-hub__icons {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.duo-flow-arrow {
  color: var(--color-accent);
  font-size: 1.2rem;
  font-weight: 800;
}

.duo-flow-hub ul {
  margin: 0;
  padding-left: 16px;
  color: var(--color-secondary);
  font-size: 0.7rem;
  line-height: 1.55;
}

.duo-flow-hub li {
  margin-bottom: 6px;
}

.features-grid {
  display: grid;
  gap: 14px;
  flex: 1;
  min-height: 0;
  align-items: stretch;
}

.features-grid--quad {
  grid-auto-rows: minmax(0, 1fr);
}

.features-grid--duo {
  grid-template-columns: 1fr;
  grid-auto-rows: auto;
  align-content: start;
  flex: 0 1 auto;
  min-height: auto;
}

.features-grid--duo .feature-card {
  min-height: unset;
  flex-shrink: 0;
}

.features-grid--duo .feature-desc {
  margin-bottom: 0;
}

.feature-card {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  min-height: 0;
  position: relative;
  overflow: visible;
}

.feature-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, var(--color-accent), var(--color-accent-warm));
}

.feature-index {
  position: absolute;
  top: 12px;
  right: 14px;
  font-size: 0.62rem;
  padding: 3px 8px;
}

.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--card-shadow-hover);
}

.icon-circle {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.11) 0%, rgba(124, 58, 237, 0.1) 100%);
  border: 1px solid rgba(37, 99, 235, 0.2);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-title {
  font-size: 0.96rem;
  font-weight: 800;
  color: var(--color-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.015em;
}

.feature-desc {
  font-size: 0.72rem;
  color: var(--color-secondary);
  line-height: 1.45;
  margin: 0 0 auto 0;
  overflow: visible;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.feature-card--compact {
  padding: 14px 16px;
}

.feature-card--compact .icon-circle {
  width: 32px;
  height: 32px;
  margin-bottom: 8px;
}

.feature-card--compact .feature-title {
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.feature-card--compact .feature-desc {
  font-size: 0.68rem;
  line-height: 1.38;
}

.duo-panel {
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.duo-panel-icons {
  display: flex;
  gap: 12px;
}

.duo-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(124, 58, 237, 0.1));
  border: 1px solid rgba(37, 99, 235, 0.18);
  color: var(--color-accent);
}

.duo-panel-title {
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-primary);
  margin: 0;
}

.duo-panel-list {
  margin: 0;
  padding-left: 18px;
  font-size: 0.74rem;
  color: var(--color-secondary);
  line-height: 1.55;
}

.duo-panel-list li {
  margin-bottom: 8px;
}

.flow-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 14px;
  background: var(--pill-bg);
  border: 1px solid var(--pill-border);
  border-radius: 12px;
}

.flow-bar__step {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--color-primary);
}

.flow-bar__arrow {
  font-size: 0.75rem;
  color: var(--color-accent);
  opacity: 0.7;
}

.features-layout--duo .features-callout {
  position: absolute;
  left: 38px;
  right: 38px;
  bottom: 18px;
  margin-top: 0;
  padding: 10px 16px;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.08), rgba(124, 58, 237, 0.05));
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-left: 3px solid var(--color-accent);
  border-radius: 14px;
  box-shadow: none;
}

.features-layout--flow .features-callout {
  position: absolute;
  left: 38px;
  right: 38px;
  bottom: 20px;
  margin-top: 0;
  padding: 10px 16px;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.08), rgba(124, 58, 237, 0.05));
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-left: 3px solid var(--color-accent);
  border-radius: 14px;
  box-shadow: none;
}

.features-layout--flow .flow-bar {
  margin-top: 12px;
  margin-bottom: 12px;
}

.features-callout {
  margin-top: 10px;
  padding: 10px 16px;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.1), rgba(124, 58, 237, 0.06));
  border-left: 3px solid var(--color-accent);
  border-radius: 12px;
}

.features-callout p {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-primary);
}
</style>
