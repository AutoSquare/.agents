<template>
  <div
    ref="storyboardRef"
    class="storyboard"
    role="region"
    aria-label="幻灯片预览列表"
  >
    <div
      v-for="slide in slides"
      :id="slideHash(slide.id)"
      :key="slide.id"
      :ref="(el) => setSlideRef(slide.id, el)"
      class="storyboard__item"
      :data-slide-id="slide.id"
    >
      <SlideFrame :slide="slide" :slide-total="slides.length" />
    </div>
  </div>
</template>

<script>
import SlideFrame from './SlideFrame.vue'
import { slideHash } from '../data/slides'

export default {
  name: 'SlideStoryboard',
  components: {
    SlideFrame,
  },
  props: {
    slides: {
      type: Array,
      required: true,
    },
  },
  emits: ['active-change'],
  data() {
    return {
      slideRefs: {},
      observer: null,
    }
  },
  mounted() {
    this.setupObserver()
    this.scrollToHash()
    window.addEventListener('hashchange', this.scrollToHash)
    window.addEventListener('keydown', this.onKeydown)
  },
  beforeUnmount() {
    if (this.observer) {
      this.observer.disconnect()
    }
    window.removeEventListener('hashchange', this.scrollToHash)
    window.removeEventListener('keydown', this.onKeydown)
  },
  methods: {
    slideHash,
    setSlideRef(id, el) {
      if (el) {
        this.slideRefs[id] = el
      }
    },
    setupObserver() {
      this.observer = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((e) => e.isIntersecting)
            .sort((a, b) => b.intersectionRatio - a.intersectionRatio)
          if (visible.length > 0) {
            const id = Number(visible[0].target.dataset.slideId)
            this.$emit('active-change', id)
            if (window.location.hash !== `#${slideHash(id)}`) {
              history.replaceState(null, '', `#${slideHash(id)}`)
            }
          }
        },
        { root: null, rootMargin: '-35% 0px -35% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] }
      )
      this.$nextTick(() => {
        Object.values(this.slideRefs).forEach((el) => {
          if (el) {
            this.observer.observe(el)
          }
        })
      })
    },
    scrollToId(id) {
      const el = this.slideRefs[id]
      if (!el) {
        return
      }
      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      el.scrollIntoView({ behavior: prefersReduced ? 'auto' : 'smooth', block: 'center' })
      history.replaceState(null, '', `#${slideHash(id)}`)
    },
    scrollToHash() {
      const hash = window.location.hash.replace('#', '')
      const match = hash.match(/^slide-(\d+)$/)
      if (match) {
        this.$nextTick(() => this.scrollToId(Number(match[1])))
      }
    },
    onKeydown(event) {
      const keys = ['ArrowDown', 'ArrowUp', 'j', 'k']
      if (!keys.includes(event.key)) {
        return
      }
      const current = this.slides.findIndex((s) => `#${slideHash(s.id)}` === window.location.hash)
      let next = current >= 0 ? current : 0
      if (event.key === 'ArrowDown' || event.key === 'j') {
        next = Math.min(next + 1, this.slides.length - 1)
      } else {
        next = Math.max(next - 1, 0)
      }
      event.preventDefault()
      this.scrollToId(this.slides[next].id)
    },
  },
}
</script>

<style scoped>
@import '../styles/storyboard-scroll.css';
</style>
