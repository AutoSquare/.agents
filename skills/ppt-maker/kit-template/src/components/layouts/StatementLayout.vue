<template>
  <div
    class="statement-layout"
    :class="{
      'statement-layout--agent': isAgentLayout,
      'statement-layout--brand': hasBrandLogos,
    }"
  >
    <div class="statement-content export-layer-fg">
      <h2 class="statement-title text-gradient">{{ slide.title }}</h2>
      <p class="statement-desc">{{ slide.description }}</p>
      <div class="statement-tags" v-if="slide.tags && slide.tags.length">
        <span class="pill-badge" v-for="tag in slide.tags" :key="tag">{{ tag }}</span>
      </div>
    </div>

    <div class="agent-orbit glass-card export-layer-fg" v-if="isAgentLayout">
      <div class="agent-core">
        <span class="agent-core__eyebrow">Agent</span>
        <strong>统一调度中枢</strong>
        <small>自然语言入口</small>
      </div>
      <div class="agent-node" v-for="(node, idx) in slide.agentFlow" :key="node.title" :class="`agent-node--${idx + 1}`">
        <span>{{ node.title }}</span>
        <small>{{ node.desc }}</small>
      </div>
    </div>

    <div class="statement-brand-panel export-layer-fg" v-if="hasBrandLogos && slide.features && slide.features.length">
      <div class="brand-collab glass-card">
        <template v-for="(logo, idx) in slide.brandLogos" :key="logo.image">
          <div class="brand-collab__logo">
            <img :src="imageUrl(logo.image)" :alt="logo.alt" />
          </div>
          <div class="brand-collab__divider" v-if="idx < slide.brandLogos.length - 1">
            <span>联合支持</span>
          </div>
        </template>
      </div>
      <div class="statement-features statement-features--brand">
        <div class="feature-item glass-card" v-for="(feat, idx) in slide.features" :key="idx">
          <h3 class="feature-title">{{ feat.title }}</h3>
          <p class="feature-desc">{{ feat.description }}</p>
        </div>
      </div>
    </div>

    <div class="statement-features export-layer-fg" v-else-if="slide.features && slide.features.length">
      <div class="feature-item glass-card" v-for="(feat, idx) in slide.features" :key="idx">
        <h3 class="feature-title">{{ feat.title }}</h3>
        <p class="feature-desc">{{ feat.description }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { imageUrl } from '../../data/slides'

export default {
  name: 'StatementLayout',
  props: {
    slide: { type: Object, required: true }
  },
  computed: {
    isAgentLayout() {
      return Array.isArray(this.slide.agentFlow) && this.slide.agentFlow.length > 0
    },
    hasBrandLogos() {
      return Array.isArray(this.slide.brandLogos) && this.slide.brandLogos.length > 0
    }
  },
  methods: {
    imageUrl(filename) {
      return imageUrl(filename)
    }
  }
}
</script>

<style scoped>
.statement-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 28px;
  padding: 44px 56px;
  align-items: center;
  position: relative;
  z-index: 1;
  min-height: 0;
}

.statement-content {
  text-align: left;
}

.statement-title {
  font-size: 2.6rem;
  font-weight: 800;
  letter-spacing: -0.055em;
  margin: 0 0 16px 0;
  line-height: 1.05;
}

.statement-desc {
  font-size: 1.1rem;
  color: var(--color-secondary);
  font-weight: 600;
  line-height: 1.55;
  margin: 0;
  max-width: 520px;
}

.statement-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.statement-layout--agent {
  grid-template-columns: 0.82fr 1.18fr;
  gap: 30px;
  padding: 34px 56px;
}

.statement-layout--agent .statement-title {
  font-size: 2.16rem;
  letter-spacing: -0.025em;
  line-height: 1.12;
  padding: 0 4px;
  margin-left: -4px;
}

.statement-layout--agent .statement-desc {
  font-size: 0.92rem;
  max-width: 390px;
}

.statement-layout--brand {
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr;
  gap: 26px;
  padding: 52px 64px 48px;
}

.statement-layout--brand .statement-content {
  text-align: center;
  align-self: end;
}

.statement-layout--brand .statement-title {
  font-size: 2.75rem;
}

.statement-layout--brand .statement-desc {
  max-width: none;
}

.brand-collab {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr auto 1fr;
  align-items: center;
  justify-items: center;
  gap: 12px;
  height: 100%;
  min-height: 276px;
  padding: 24px 32px;
  background:
    radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.12), transparent 38%),
    rgba(255, 255, 255, 0.86);
}

.brand-collab__divider {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  color: var(--color-accent);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.18em;
}

.brand-collab__divider::before,
.brand-collab__divider::after {
  content: '';
  height: 1px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.36));
}

.brand-collab__divider::after {
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.36), transparent);
}

.brand-collab__logo {
  width: 100%;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-collab__logo img {
  width: 100%;
  height: 82px;
  object-fit: contain;
  display: block;
}

.brand-collab__logo:first-of-type img {
  height: 88px;
}

.brand-collab__logo:last-child img {
  height: 74px;
}

.statement-brand-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 42px;
  align-self: start;
}

.statement-features--brand {
  align-self: stretch;
  gap: 16px;
  margin-top: 0;
}

.statement-features--brand .feature-item {
  flex: 1;
  padding: 18px 22px;
}

.statement-features--brand .feature-title {
  font-size: 1.05rem;
  margin-bottom: 8px;
}

.statement-features--brand .feature-desc {
  font-size: 0.8rem;
  line-height: 1.5;
}

.agent-orbit {
  position: relative;
  min-height: 340px;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 48%, rgba(37, 99, 235, 0.14), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.9));
}

.agent-orbit::before,
.agent-orbit::after {
  content: '';
  position: absolute;
  inset: 48px 70px;
  border: 1px dashed rgba(37, 99, 235, 0.24);
  border-radius: 999px;
}

.agent-orbit::after {
  inset: 92px 128px;
  border-style: solid;
  opacity: 0.55;
}

.agent-core {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 154px;
  height: 112px;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-strong));
  color: #ffffff;
  box-shadow: 0 26px 58px rgba(37, 99, 235, 0.28);
  z-index: 2;
}

.agent-core__eyebrow,
.agent-core small {
  font-size: 0.66rem;
  font-weight: 700;
  opacity: 0.86;
}

.agent-core strong {
  font-size: 0.92rem;
  font-weight: 800;
}

.agent-node {
  position: absolute;
  width: 136px;
  height: 74px;
  padding: 12px 13px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(37, 99, 235, 0.16);
  box-shadow: var(--card-shadow);
  z-index: 3;
}

.agent-node span {
  display: block;
  margin-bottom: 4px;
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 800;
}

.agent-node small {
  display: block;
  color: var(--color-secondary);
  font-size: 0.6rem;
  line-height: 1.35;
}

.agent-node--1 {
  left: 58px;
  top: 52px;
}

.agent-node--2 {
  right: 58px;
  top: 52px;
}

.agent-node--3 {
  left: 58px;
  bottom: 52px;
}

.agent-node--4 {
  right: 58px;
  bottom: 52px;
}

.statement-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  padding: 18px 22px;
  text-align: left;
  position: relative;
  overflow: hidden;
}

.feature-item::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, var(--color-accent), var(--color-accent-warm));
}

.feature-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--color-primary);
  margin: 0 0 8px 0;
}

.feature-desc {
  font-size: 0.8rem;
  color: var(--color-secondary);
  line-height: 1.5;
  margin: 0;
}
</style>
