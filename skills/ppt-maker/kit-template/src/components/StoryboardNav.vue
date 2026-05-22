<template>
  <nav class="timeline-nav" aria-label="幻灯片侧边索引目录">
    <!-- Sliding golden timeline vertical track -->
    <div class="timeline-nav__track">
      <div class="timeline-nav__line"></div>
      <div class="timeline-nav__line-active" :style="activeProgressStyle"></div>
    </div>

    <ul class="timeline-nav__list">
      <li
        v-for="slide in slides"
        :key="slide.id"
        class="timeline-nav__item"
        :class="{ 'timeline-nav__item--active': activeId === slide.id }"
      >
        <button
          type="button"
          class="timeline-nav__btn"
          :aria-label="`跳转至：${slide.sectionLabel} ${slide.title}`"
          :aria-current="activeId === slide.id ? 'true' : undefined"
          @click="$emit('navigate', slide.id)"
        >
          <!-- Absolute dot aligning with the line -->
          <div class="timeline-nav__dot-wrap">
            <span class="timeline-nav__dot"></span>
          </div>

          <!-- Editorial text card extending to the right -->
          <div class="timeline-nav__card">
            <span class="timeline-nav__num">0{{ slide.id }}</span>
            <div class="timeline-nav__label-group">
              <span class="timeline-nav__badge">{{ slide.sectionLabel }}</span>
              <span class="timeline-nav__title">{{ slide.title.split(' · ')[0] }}</span>
            </div>
          </div>
        </button>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: 'StoryboardNav',
  props: {
    slides: {
      type: Array,
      required: true,
    },
    activeId: {
      type: Number,
      default: 1,
    },
  },
  emits: ['navigate'],
  computed: {
    activeProgressStyle() {
      // Calculate active progress height percentage
      const total = this.slides.length
      if (total <= 1) return { height: '0%' }
      const percent = ((this.activeId - 1) / (total - 1)) * 100
      return {
        height: `${percent}%`,
      }
    },
  },
}
</script>

<style scoped>
.timeline-nav {
  position: sticky;
  top: 140px;
  flex-shrink: 0;
  width: 220px;
  margin-left: 20px;
}

.timeline-nav__track {
  position: absolute;
  left: 16px;
  top: 16px;
  bottom: 16px;
  width: 2px;
  pointer-events: none;
}

.timeline-nav__line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: var(--color-border);
  opacity: 0.6;
}

.timeline-nav__line-active {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background-color: var(--color-accent);
  transition: height 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.timeline-nav__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.timeline-nav__item {
  position: relative;
}

.timeline-nav__btn {
  background: none;
  border: none;
  padding: 0;
  display: flex;
  align-items: center;
  text-align: left;
  cursor: pointer;
  width: 100%;
}

.timeline-nav__btn:focus-visible {
  outline: none;
}

.timeline-nav__btn:focus-visible .timeline-nav__card {
  box-shadow: var(--focus-ring);
}

/* Absolute dot positioning */
.timeline-nav__dot-wrap {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.timeline-nav__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-border);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.timeline-nav__btn:hover .timeline-nav__dot {
  background-color: var(--color-accent);
  transform: scale(1.2);
}

/* Active dot glow */
.timeline-nav__item--active .timeline-nav__dot {
  background-color: var(--color-accent);
  transform: scale(1.35);
  box-shadow: 0 0 0 4px var(--color-accent-light);
}

/* Horizontal card extension */
.timeline-nav__card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--card-radius);
  border: 1px solid transparent;
  transform: translateX(4px);
  opacity: 0.55;
  transition: all var(--transition-fast);
}

.timeline-nav__btn:hover .timeline-nav__card {
  opacity: 0.85;
  transform: translateX(8px);
}

.timeline-nav__item--active .timeline-nav__card {
  opacity: 1;
  background-color: var(--color-background);
  border-color: var(--color-border);
  box-shadow: 0 4px 16px rgba(27, 25, 24, 0.04), 0 0 0 1px rgba(27, 25, 24, 0.01);
  transform: translateX(10px);
}

/* Big serif number */
.timeline-nav__num {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-accent);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.timeline-nav__label-group {
  display: flex;
  flex-direction: column;
}

.timeline-nav__badge {
  font-size: 0.5625rem;
  font-weight: 700;
  color: var(--color-muted-text);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.timeline-nav__title {
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--color-foreground);
  line-height: 1.2;
  margin-top: 1px;
}

/* Responsive Nav Catalog */
@media (max-width: 768px) {
  .timeline-nav {
    position: static;
    width: 100%;
    margin-left: 0;
    margin-top: 24px;
    padding: 0 20px;
    box-sizing: border-box;
  }

  .timeline-nav__track {
    display: none; /* Hide vertical timeline line on mobile */
  }

  .timeline-nav__list {
    flex-direction: row;
    gap: 8px;
    justify-content: center;
    width: 100%;
  }

  .timeline-nav__item {
    flex: 1;
    max-width: 150px;
  }

  .timeline-nav__dot-wrap {
    display: none; /* Hide dot on mobile */
  }

  .timeline-nav__card {
    width: 100%;
    opacity: 0.75;
    transform: none !important;
    background-color: var(--color-background);
    border: 1px solid var(--color-border-light);
    justify-content: center;
    box-sizing: border-box;
  }

  .timeline-nav__btn:hover .timeline-nav__card {
    opacity: 0.9;
    transform: none;
    border-color: var(--color-border);
  }

  .timeline-nav__item--active .timeline-nav__card {
    opacity: 1;
    border-color: var(--color-accent);
    box-shadow: 0 2px 8px rgba(184, 144, 71, 0.06);
  }
}
</style>
