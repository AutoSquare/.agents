<template>
  <div class="dual-case export-layer-fg" :style="gridStyle">
    <div
      v-for="(caseItem, index) in cases"
      :key="caseItem.name"
      class="dual-case__item"
      :class="{ 'dual-case__item--divider': index === 0 }"
    >
      <CaseCard
        :case-item="caseItem"
        :lazy-load="lazyLoad"
      />
    </div>
  </div>
</template>

<script>
import CaseCard from '../CaseCard.vue'

export default {
  name: 'DualCaseLayout',
  components: {
    CaseCard,
  },
  props: {
    slide: {
      type: Object,
      required: true,
    },
    lazyLoad: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    cases() {
      return this.slide.cases || []
    },
    layoutRatio() {
      return this.slide.layoutRatio || '50-50'
    },
    gridStyle() {
      if (this.layoutRatio === '60-40') {
        return { gridTemplateColumns: '60fr 40fr' }
      } else if (this.layoutRatio === '65-35') {
        return { gridTemplateColumns: '65fr 35fr' }
      }
      return { gridTemplateColumns: '1fr 1fr' }
    },
  },
}
</script>

<style scoped>
.dual-case {
  display: grid;
  flex: 1;
  min-height: 0;
  background: var(--color-background);
}

.dual-case__item {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 16px 20px 20px;
}

.dual-case__item--divider {
  border-right: 1px solid var(--color-border-light);
}

@media (max-width: 768px) {
  .dual-case {
    grid-template-columns: 1fr !important;
  }

  .dual-case__item--divider {
    border-right: none;
    border-bottom: 1px solid var(--color-border-light);
  }
}
</style>
