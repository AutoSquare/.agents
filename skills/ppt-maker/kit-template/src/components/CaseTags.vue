<template>
  <div v-if="tags.length" class="case-tags">
    <span v-for="tag in tags" :key="tag" class="case-tags__item">{{ tag }}</span>
  </div>
</template>

<script>
export default {
  name: 'CaseTags',
  props: {
    tags: {
      type: Array,
      default: () => [],
    },
  },
}
</script>

<style scoped>
.case-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.case-tags__item {
  padding: 2px 6px;
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--color-secondary);
  background: var(--color-accent-light);
  border: 1px solid rgba(184, 144, 71, 0.15);
  border-radius: 2px;
  line-height: 1.3;
}
</style>
