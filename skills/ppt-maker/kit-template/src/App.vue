<template>
  <div class="app">
    <!-- Skip Navigation Link -->
    <a href="#storyboard-start" class="skip-link">跳至幻灯片内容</a>

    <!-- Top Premium Editorial Header -->
    <header class="app-header">
      <div class="app-header__brand">
        <span class="app-header__subtitle">{{ projectConfig.appSubtitle }}</span>
        <h1 class="app-header__title">{{ projectConfig.appTitle }}</h1>
      </div>
      <div class="app-header__divider"></div>
      <div class="app-header__controls">
        <p class="app-header__desc">
          {{ projectConfig.appDesc }}
        </p>

        <div class="app-header__export-group">
          <label class="export-resolution">
            <span class="export-resolution__label">导出分辨率</span>
            <select
              v-model="exportCapturePreset"
              class="export-resolution__select"
              :disabled="isExportBusy"
              aria-label="选择离屏渲染导出分辨率"
            >
              <option
                v-for="preset in capturePresetOptions"
                :key="preset.id"
                :value="preset.id"
              >
                {{ preset.label }}
              </option>
            </select>
          </label>

          <div class="app-header__export-buttons">
        <button
          class="ctrl-btn ctrl-btn--export"
          :disabled="isExportBusy"
          aria-label="导出可编辑 PowerPoint 文件"
          @click="exportPptx"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ctrl-btn__icon">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <line x1="9" y1="15" x2="15" y2="15"></line>
          </svg>
          {{ exportPptxLabel }}
        </button>

        <button
          class="ctrl-btn ctrl-btn--export-raster"
          :disabled="isExportBusy"
          aria-label="导出像素级 PowerPoint，按所选分辨率离屏高清渲染"
          title="按所选分辨率离屏渲染后写入 PPT（非屏幕截图）"
          @click="exportPptxRaster"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ctrl-btn__icon">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
          {{ exportRasterLabel }}
        </button>

        <button
          class="ctrl-btn ctrl-btn--export-images"
          :disabled="isExportBusy"
          aria-label="导出幻灯片 PNG 压缩包，按所选分辨率离屏渲染"
          :title="`离屏渲染 ${slides.length} 张 PNG 并打包为 ZIP，可在 PPT 中插入图片铺满幻灯片`"
          @click="exportSlideImagesZip"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ctrl-btn__icon">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          {{ exportImagesLabel }}
        </button>
          </div>
        </div>

        <!-- Toggle Drafting Grid Switch -->
        <button
          class="ctrl-btn"
          :class="{ 'ctrl-btn--active': gridState.active }"
          @click="toggleGrid"
          aria-label="切换对齐辅助网格"
          :aria-pressed="gridState.active ? 'true' : 'false'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ctrl-btn__icon">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="9" y1="3" x2="9" y2="21"></line>
            <line x1="15" y1="3" x2="15" y2="21"></line>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="3" y1="15" x2="21" y2="15"></line>
          </svg>
          对齐辅助网格 (Draft Grid)
          <span class="ctrl-btn__status">{{ gridState.active ? 'ON' : 'OFF' }}</span>
        </button>
      </div>
    </header>

    <!-- Main Content Layout -->
    <div id="storyboard-start" class="storyboard-layout">
      <main class="storyboard-main">
        <SlideStoryboard
          :slides="slides"
          @active-change="activeId = $event"
        />
      </main>
      
      <!-- Timeline Navigation Catalog -->
      <StoryboardNav
        :slides="slides"
        :active-id="activeId"
        @navigate="onNavigate"
      />
    </div>

    <!-- Full-Screen Interactive Lightbox Modal -->
    <transition name="lightbox-fade">
      <div
        v-if="lightbox.isOpen"
        class="lightbox-modal"
        @click.self="closeLightbox"
        role="dialog"
        aria-modal="true"
        aria-label="高清素材细节查阅模态框"
      >
        <!-- Top Toolbar inside Modal -->
        <div class="lightbox-modal__topbar">
          <div class="lightbox-modal__title-group">
            <span class="lightbox-modal__sub">MATERIAL LOOKUP // 细节解译</span>
            <h3 class="lightbox-modal__title">{{ lightbox.alt }}</h3>
          </div>
          <button class="lightbox-modal__close-btn" @click="closeLightbox" aria-label="关闭详情窗口">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Zoom Floating indicator bubble -->
        <div class="lightbox-modal__zoom-indicator">
          <span>倍率: {{ Math.round(lightbox.zoom * 100) }}%</span>
        </div>

        <!-- Canvas and Zoomable Image -->
        <div
          class="lightbox-modal__canvas"
          @wheel.prevent="handleWheel"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="endDrag"
          @mouseleave="endDrag"
          :class="{ 'lightbox-modal__canvas--zoom-active': lightbox.zoom > 1.0, 'lightbox-modal__canvas--dragging': lightbox.isDragging }"
        >
          <img
            :src="lightbox.src"
            :alt="lightbox.alt"
            class="lightbox-modal__img"
            :style="imageTransformStyle"
            draggable="false"
          />
        </div>

        <!-- Bottom Status spec bar with Copy Path Tool -->
        <div class="lightbox-modal__bottombar">
          <div class="lightbox-modal__path-copy">
            <span class="path-label">素材绝对路径:</span>
            <code class="path-value">{{ lightbox.src }}</code>
            <button class="path-copy-btn" @click="copyPath" aria-label="复制路径到剪贴板">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="btn-icon">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              一键复制路径 (复刻PPT插入使用)
            </button>
          </div>
          <div class="lightbox-modal__tips">
            <span class="tips-item">🔍 鼠标滚轮/无极缩放 (0.5x - 5.0x)</span>
            <span class="tips-item">🖐️ 拖拽平移画面 (放大后)</span>
            <span class="tips-item">⌨️ 按 ESC 退出</span>
          </div>
        </div>
      </div>
    </transition>

    <!-- Global Toast notification -->
    <transition name="toast-slide">
      <div v-if="showToast" class="global-toast" role="status" aria-live="polite">
        <div class="global-toast__content">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="toast-icon">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span class="toast-text">{{ toastMessage }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { reactive } from 'vue'
import SlideStoryboard from './components/SlideStoryboard.vue'
import StoryboardNav from './components/StoryboardNav.vue'
import { projectConfig } from './config/project.js'
import { slides } from './data/slides'
import {
  CAPTURE_PRESETS,
  DEFAULT_CAPTURE_PRESET,
  getCapturePreset,
} from './utils/capturePresets'

export default {
  name: 'App',
  components: {
    SlideStoryboard,
    StoryboardNav,
  },
  data() {
    return {
      projectConfig,
      slides,
      activeId: 1,
      gridState: reactive({ active: false }), // Reactive alignment grid state
      lightbox: {
        isOpen: false,
        src: '',
        alt: '',
        zoom: 1.0,
        x: 0,
        y: 0,
        isDragging: false,
        startX: 0,
        startY: 0,
      },
      showToast: false,
      toastMessage: '',
      exportingPptx: false,
      exportingRaster: false,
      rasterProgress: '',
      exportingImages: false,
      imageProgress: '',
      exportCapturePreset: DEFAULT_CAPTURE_PRESET,
    }
  },
  provide() {
    return {
      gridState: this.gridState,
      openLightbox: this.openLightbox,
    }
  },
  computed: {
    imageTransformStyle() {
      return {
        transform: `translate(${this.lightbox.x}px, ${this.lightbox.y}px) scale(${this.lightbox.zoom})`,
        transition: this.lightbox.isDragging ? 'none' : 'transform 0.15s ease-out',
      }
    },
    isExportBusy() {
      return this.exportingPptx || this.exportingRaster || this.exportingImages
    },
    exportPptxLabel() {
      if (this.exportingPptx) return '正在生成可编辑 PPT…'
      return '导出 PowerPoint（可编辑）'
    },
    exportRasterLabel() {
      if (this.exportingRaster) {
        return this.rasterProgress || '正在生成像素级 PPT…'
      }
      return '导出像素级 PPT'
    },
    exportImagesLabel() {
      if (this.exportingImages) {
        return this.imageProgress || '正在打包图片…'
      }
      return '导出幻灯片图片 (ZIP)'
    },
    capturePresetOptions() {
      return Object.values(CAPTURE_PRESETS)
    },
    activeCapturePreset() {
      return getCapturePreset(this.exportCapturePreset)
    },
  },
  mounted() {
    window.addEventListener('keydown', this.handleGlobalKey)
  },
  unmounted() {
    window.removeEventListener('keydown', this.handleGlobalKey)
  },
  methods: {
    onNavigate(id) {
      const el = document.getElementById(`slide-${id}`)
      if (el) {
        const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
        el.scrollIntoView({ behavior: prefersReduced ? 'auto' : 'smooth', block: 'center' })
        history.replaceState(null, '', `#slide-${id}`)
        this.activeId = id
      }
    },
    toggleGrid() {
      this.gridState.active = !this.gridState.active
      this.triggerToast(`辅助对齐网格已${this.gridState.active ? '开启' : '关闭'}`)
    },
    openLightbox(src, alt) {
      this.lightbox.src = src
      this.lightbox.alt = alt || '解译素材图'
      this.lightbox.zoom = 1.0
      this.lightbox.x = 0
      this.lightbox.y = 0
      this.lightbox.isOpen = true
      document.body.style.overflow = 'hidden' // Lock background scrolling
    },
    closeLightbox() {
      this.lightbox.isOpen = false
      document.body.style.overflow = '' // Unlock background scrolling
    },
    handleGlobalKey(e) {
      if (e.key === 'Escape' && this.lightbox.isOpen) {
        this.closeLightbox()
      }
    },
    handleWheel(e) {
      const delta = e.deltaY > 0 ? -0.15 : 0.15
      this.lightbox.zoom = Math.min(Math.max(this.lightbox.zoom + delta, 0.5), 5.0)
    },
    startDrag(e) {
      if (this.lightbox.zoom <= 1.0) return
      this.lightbox.isDragging = true
      this.lightbox.startX = e.clientX - this.lightbox.x
      this.lightbox.startY = e.clientY - this.lightbox.y
    },
    onDrag(e) {
      if (!this.lightbox.isDragging) return
      this.lightbox.x = e.clientX - this.lightbox.startX
      this.lightbox.y = e.clientY - this.lightbox.startY
    },
    endDrag() {
      this.lightbox.isDragging = false
    },
    copyPath() {
      // Write absolute server-relative path for convenience
      const relativePath = this.lightbox.src
      navigator.clipboard.writeText(relativePath).then(() => {
        this.triggerToast(`已成功复制素材路径：${relativePath}`)
      }).catch(() => {
        // Fallback for security errors
        const tempInput = document.createElement('input')
        tempInput.value = relativePath
        document.body.appendChild(tempInput)
        tempInput.select()
        document.execCommand('copy')
        document.body.removeChild(tempInput)
        this.triggerToast(`已复制路径：${relativePath}`)
      })
    },
    triggerToast(message) {
      this.toastMessage = message
      this.showToast = true
      // Auto dismiss after 2.5 seconds
      if (this.toastTimeout) clearTimeout(this.toastTimeout)
      this.toastTimeout = setTimeout(() => {
        this.showToast = false
      }, 2500)
    },
    async exportPptx() {
      if (this.isExportBusy) return
      this.exportingPptx = true
      try {
        const { exportStoryboardToPptx } = await import('./utils/exportPptx')
        const { missingImages } = await exportStoryboardToPptx(this.slides)
        if (missingImages.length > 0) {
          this.triggerToast(
            `PPT 已下载；${missingImages.length} 个素材缺失：${missingImages.slice(0, 2).join('、')}${missingImages.length > 2 ? '…' : ''}`,
          )
        } else {
          this.triggerToast(
            `可编辑 PPT 已生成并下载（${this.projectConfig.exports.editableFileName}）`,
          )
        }
      } catch (err) {
        console.error(err)
        this.triggerToast(`导出失败：${err.message || '请确认开发服务器已启动且素材可访问'}`)
      } finally {
        this.exportingPptx = false
      }
    },
    async exportPptxRaster() {
      if (this.isExportBusy) return
      if (this.lightbox.isOpen) {
        this.closeLightbox()
      }
      this.exportingRaster = true
      this.rasterProgress = '正在准备…'
      document.body.classList.add('export-raster-active')
      try {
        const { exportStoryboardToRasterPptx } = await import(
          /* webpackChunkName: "pptx-raster-export" */
          './utils/exportPptxRaster'
        )
        await exportStoryboardToRasterPptx(
          this.slides,
          { gridState: this.gridState },
          {
            capturePreset: this.exportCapturePreset,
            onProgress: (current, total, phase) => {
              if (phase === 'write') {
                this.rasterProgress = '正在写入 PPT…'
              } else {
                this.rasterProgress = `正在渲染 ${current}/${total} 页…`
              }
            },
          },
        )
        const preset = this.activeCapturePreset
        this.triggerToast(
          `像素级 PPT 已下载（${this.projectConfig.exports.rasterFileName}）。${preset.shortLabel} ${preset.width}×${preset.height} 离屏渲染整页图，与预览一致，PowerPoint 中不可编辑文字。`,
        )
      } catch (err) {
        console.error(err)
        this.triggerToast(
          `像素级导出失败：${err.message || '请确认素材已加载完成，刷新页面后重试'}`,
        )
      } finally {
        document.body.classList.remove('export-raster-active')
        this.exportingRaster = false
        this.rasterProgress = ''
      }
    },
    async exportSlideImagesZip() {
      if (this.isExportBusy) return
      if (this.lightbox.isOpen) {
        this.closeLightbox()
      }
      this.exportingImages = true
      this.imageProgress = '正在准备…'
      document.body.classList.add('export-raster-active')
      try {
        const { exportStoryboardToImageZip } = await import(
          /* webpackChunkName: "slide-images-export" */
          './utils/exportSlideImages'
        )
        await exportStoryboardToImageZip(
          this.slides,
          { gridState: this.gridState },
          {
            capturePreset: this.exportCapturePreset,
            onProgress: (current, total, phase) => {
              if (phase === 'zip') {
                this.imageProgress = '正在打包 ZIP…'
              } else {
                this.imageProgress = `正在渲染 ${current}/${total} 页…`
              }
            },
          },
        )
        const preset = this.activeCapturePreset
        this.triggerToast(
          `幻灯片图片已下载（${this.projectConfig.exports.zipFileName}）。内含 ${this.slides.length} 张 ${preset.width}×${preset.height} PNG（${preset.shortLabel}），可在 PowerPoint 中使用「插入 → 图片」铺满幻灯片。`,
        )
      } catch (err) {
        console.error(err)
        this.triggerToast(
          `图片导出失败：${err.message || '请确认素材已加载完成，刷新页面后重试'}`,
        )
      } finally {
        document.body.classList.remove('export-raster-active')
        this.exportingImages = false
        this.imageProgress = ''
      }
    },
  },
}
</script>

<style>
@import './styles/design-tokens.css';
@import './styles/storyboard.css';
@import './styles/nav.css';
@import './styles/print.css';
@import './styles/export-capture.css';

/* Reset and basic body overrides */
body {
  margin: 0;
  padding: 0;
  font-family: var(--font-body);
  background-color: var(--color-canvas);
  color: var(--color-foreground);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Accessibility skip-link */
.skip-link {
  position: absolute;
  top: -100px;
  left: 16px;
  background-color: var(--color-accent);
  color: var(--color-on-primary);
  padding: 8px 16px;
  border-radius: var(--card-radius);
  z-index: var(--z-skip);
  font-weight: 700;
  transition: top var(--transition-fast);
  box-shadow: 0 4px 12px rgba(184, 144, 71, 0.2);
}

.skip-link:focus-visible {
  top: 16px;
  outline: none;
}

/* Premium Editorial App Header */
.app-header {
  flex-shrink: 0;
  padding: 20px 40px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.app-header__brand {
  display: flex;
  flex-direction: column;
}

.app-header__subtitle {
  font-size: 0.625rem;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: 0.18em;
  font-family: var(--font-body);
}

.app-header__title {
  margin: 2px 0 0;
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-foreground);
  letter-spacing: -0.01em;
}

.app-header__divider {
  width: 1px;
  height: 32px;
  background-color: var(--color-border);
}

.app-header__controls {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.app-header__desc {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-secondary);
  font-weight: 500;
}

.app-header__export-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.app-header__export-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.export-resolution {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.export-resolution__label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-secondary);
  white-space: nowrap;
}

.export-resolution__select {
  min-height: 44px;
  padding: 8px 12px;
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-foreground);
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--card-radius);
  cursor: pointer;
}

.export-resolution__select:disabled {
  opacity: 0.65;
  cursor: wait;
}

.export-resolution__select:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
  border-color: var(--color-accent);
}

/* Drafting Grid Control Button */
.ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-secondary);
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--card-radius);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.ctrl-btn:hover {
  color: var(--color-foreground);
  border-color: var(--color-accent);
  background-color: var(--color-accent-light);
}

.ctrl-btn:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

.ctrl-btn--active {
  color: var(--color-accent-warm);
  background-color: #FDF2E9; /* Warm orange light background */
  border-color: var(--color-accent-warm);
}

.ctrl-btn--active:hover {
  background-color: #FBE5D6;
  border-color: var(--color-accent-warm);
  color: var(--color-accent-warm);
}

.ctrl-btn__icon {
  flex-shrink: 0;
  opacity: 0.85;
}

.ctrl-btn__status {
  font-size: 0.625rem;
  padding: 1px 4px;
  border-radius: 2px;
  background: rgba(0,0,0,0.05);
  margin-left: 4px;
  font-weight: 800;
}

.ctrl-btn--active .ctrl-btn__status {
  background: rgba(194, 65, 12, 0.1);
}

.ctrl-btn--export {
  color: var(--color-foreground);
  border-color: var(--color-accent);
  background: var(--color-accent-light);
}

.ctrl-btn--export:hover:not(:disabled) {
  background: #F0E8D8;
  border-color: var(--color-accent);
  color: var(--color-foreground);
}

.ctrl-btn--export:disabled,
.ctrl-btn--export-raster:disabled,
.ctrl-btn--export-images:disabled {
  opacity: 0.65;
  cursor: wait;
}

.ctrl-btn--export-raster {
  color: var(--color-secondary);
  border-color: var(--color-border);
  background: var(--color-surface);
}

.ctrl-btn--export-raster:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-foreground);
  background: var(--color-accent-light);
}

.ctrl-btn--export-images {
  color: var(--color-secondary);
  border-color: var(--color-border);
  background: var(--color-background);
}

.ctrl-btn--export-images:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-foreground);
  background: var(--color-accent-light);
}

body.export-raster-active .asset-image__overlay {
  opacity: 0 !important;
  pointer-events: none !important;
}

body.export-raster-active .slide-frame__canvas:hover {
  box-shadow: var(--slide-shadow);
}

/* Global Lightbox Modal Styles */
.lightbox-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 30, 36, 0.96); /* Elegant deep coal backdrop */
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  color: #FCFBF9;
}

.lightbox-modal__topbar {
  flex-shrink: 0;
  padding: 16px 24px;
  background: rgba(15, 30, 36, 0.8);
  border-bottom: 1px solid rgba(225, 221, 212, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.lightbox-modal__title-group {
  display: flex;
  flex-direction: column;
}

.lightbox-modal__sub {
  font-size: 0.625rem;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: 0.15em;
}

.lightbox-modal__title {
  margin: 2px 0 0;
  font-family: var(--font-heading);
  font-size: 1.125rem;
  font-weight: 700;
}

.lightbox-modal__close-btn {
  background: none;
  border: none;
  color: rgba(252, 251, 249, 0.7);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.lightbox-modal__close-btn:hover {
  background: rgba(252, 251, 249, 0.1);
  color: #FCFBF9;
}

.lightbox-modal__close-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--color-accent);
}

/* Floating Zoom bubble indicator */
.lightbox-modal__zoom-indicator {
  position: absolute;
  top: 90px;
  left: 24px;
  background: rgba(184, 144, 71, 0.9);
  color: #FCFBF9;
  padding: 4px 10px;
  font-size: 0.6875rem;
  font-weight: 700;
  border-radius: 4px;
  z-index: 1010;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  pointer-events: none;
}

/* Modal Canvas for Panning and Zooming */
.lightbox-modal__canvas {
  flex: 1;
  min-height: 0;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-in;
}

.lightbox-modal__canvas--zoom-active {
  cursor: grab;
}

.lightbox-modal__canvas--dragging {
  cursor: grabbing;
}

.lightbox-modal__img {
  max-width: 85vw;
  max-height: 70vh;
  object-fit: contain;
  box-shadow: 0 24px 48px rgba(0,0,0,0.4);
  border-radius: 2px;
  user-select: none;
}

/* Lightbox Modal Bottom Bar with Copy Path Tool */
.lightbox-modal__bottombar {
  flex-shrink: 0;
  padding: 16px 24px;
  background: rgba(15, 30, 36, 0.9);
  border-top: 1px solid rgba(225, 221, 212, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.lightbox-modal__path-copy {
  display: flex;
  align-items: center;
  gap: 10px;
}

.path-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: rgba(252, 251, 249, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.path-value {
  font-family: Consolas, Monaco, monospace;
  font-size: 0.75rem;
  background: rgba(0,0,0,0.3);
  padding: 4px 8px;
  border-radius: 2px;
  color: var(--color-accent);
  border: 1px solid rgba(184, 144, 71, 0.2);
}

.path-copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  font-family: var(--font-body);
  font-size: 0.6875rem;
  font-weight: 700;
  color: #FCFBF9;
  background: var(--color-accent);
  border: none;
  border-radius: var(--card-radius);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.path-copy-btn:hover {
  background: #C29F55; /* Lighter copper */
}

.btn-icon {
  opacity: 0.9;
}

.lightbox-modal__tips {
  display: flex;
  gap: 16px;
}

.tips-item {
  font-size: 0.6875rem;
  color: rgba(252, 251, 249, 0.5);
  font-weight: 600;
}

/* Global Toast Notification styles */
.global-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
}

.global-toast__content {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--color-primary);
  border: 1px solid var(--color-accent);
  color: var(--color-on-primary);
  padding: 10px 20px;
  border-radius: 30px;
  box-shadow: 0 16px 32px rgba(15, 30, 36, 0.25);
}

.toast-icon {
  color: var(--color-accent);
}

.toast-text {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

/* Lightbox Animation Transitions */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.25s ease;
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}

/* Toast Animation Transitions */
.toast-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-slide-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-slide-enter-from {
  opacity: 0;
  transform: translate(-50%, 12px);
}
.toast-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, 12px);
}

/* Responsive Header */
@media (max-width: 850px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 16px 20px;
  }
  .app-header__divider {
    display: none;
  }
  .app-header__controls {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
