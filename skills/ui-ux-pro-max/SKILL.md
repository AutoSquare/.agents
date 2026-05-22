---
name: ui-ux-pro-max
description: Web 与移动端 UI/UX 设计智能：67 种风格、161 套配色、57 组字体配对、99 条 UX 指南；本项目以 React Native 为主。用于设计/审查/改进界面、landing page、dashboard、表单、图表、配色排版、无障碍与 React Native UI 实现。
---
# UI/UX Pro Max - 设计智能指南

面向 Web 与移动应用的综合性设计指南，含 67 种风格、161 套配色、57 组字体配对、99 条 UX 指南、25 种图表类型；本项目以 React Native 栈指南为主，配合 CSV 检索与设计系统生成，按优先级给出推荐。

## 何时使用

当任务涉及 **UI 结构、视觉设计决策、交互模式或用户体验质量控制** 时，应使用此 Skill。

### 必须使用

在以下情况必须调用此 Skill：

- 设计新的页面（Landing Page、Dashboard、Admin、SaaS、Mobile App）
- 创建或重构 UI 组件（按钮、弹窗、表单、表格、图表等）
- 选择配色方案、字体系统、间距规范或布局体系
- 审查 UI 代码的用户体验、可访问性或视觉一致性
- 实现导航结构、动效或响应式行为
- 做产品层级的设计决策（风格、信息层级、品牌表达）
- 提升界面的感知质量、清晰度或可用性
- **`ppt-maker` 幻灯片风格定制**：在 `ppt-projects/{slug}/` 下运行 `search.py --design-system --persist`，将结果映射到 `src/styles/design-tokens.css`

### 建议使用

在以下情况建议使用此 Skill：

- UI 看起来"不够专业"，但原因不明确
- 收到可用性或体验方面的反馈
- 准备上线前的 UI 质量优化
- 需要对齐跨平台设计（Web / iOS / Android）
- 构建设计系统或可复用组件库

### 无需使用

在以下情况无需使用此 Skill：

- 纯后端逻辑开发
- 仅涉及 API 或数据库设计
- 与界面无关的性能优化
- 基础设施或 DevOps 工作
- 非视觉类脚本或自动化任务

**判断准则**：如果任务会改变某个功能 **看起来如何、使用起来如何、如何运动或如何被交互**，就应该使用此 Skill。

## 按优先级的规则类别

*供人工/AI 查阅：按 1→10 决定先关注哪类规则；需要细则时用 `--domain <Domain>` 查询。脚本不读取本表。*

| 优先级 | 类别 | 影响 | 域 | 关键检查（必备） | 反模式（避免） |
|----------|----------|--------|--------|------------------------|------------------------|
| 1 | 无障碍 | 严重 | `ux` | 对比度 4.5:1、替代文本、键盘导航、aria-label | 移除焦点环、无标签的纯图标按钮 |
| 2 | 触控与交互 | 严重 | `ux` | 最小尺寸 44×44px、间距 ≥8px、加载反馈 | 仅依赖悬停、瞬时状态变化（0ms） |
| 3 | 性能 | 高 | `ux` | WebP/AVIF、懒加载、预留空间（CLS &lt; 0.1） | 布局抖动、累积布局偏移 |
| 4 | 风格选择 | 高 | `style`, `product` | 匹配产品类型、一致性、SVG 图标（不用 emoji） | 随意混用扁平与拟物、用 emoji 充当图标 |
| 5 | 布局与响应式 | 高 | `ux` | 移动优先断点、viewport meta、禁止横向滚动 | 横向滚动、固定 px 容器宽度、禁用缩放 |
| 6 | 排版与色彩 | 中 | `typography`, `color` | 基准 16px、行高 1.5、语义化色彩 token | 正文 &lt; 12px、灰底灰字、组件中直接使用 hex |
| 7 | 动效 | 中 | `ux` | 时长 150–300ms、动效传达含义、空间连续性 | 纯装饰动效、动画 width/height、未适配 reduced-motion |
| 8 | 表单与反馈 | 中 | `ux` | 可见标签、错误贴近字段、辅助说明、渐进披露 | 仅用 placeholder 作标签、错误仅显示在顶部、一次性信息过载 |
| 9 | 导航模式 | 高 | `ux` | 可预测的返回、底部导航 ≤5 项、深层链接 | 导航过载、返回行为异常、无深层链接 |
| 10 | 图表与数据 | 低 | `chart` | 图例、工具提示、可访问色彩 | 仅靠颜色传达含义 |

## 快速参考

### 1. 无障碍（严重）

- `color-contrast` - 普通文本最低对比度 4.5:1（大文本 3:1）；Material Design
- `focus-states` - 交互元素须显示可见焦点环（2–4px；Apple HIG、MD）
- `alt-text` - 有意义的图片须提供描述性替代文本
- `aria-labels` - 纯图标按钮须设置 aria-label；原生端使用 accessibilityLabel（Apple HIG）
- `keyboard-nav` - Tab 顺序与视觉顺序一致；提供完整键盘支持（Apple HIG）
- `form-labels` - 使用带 for 属性的 label
- `skip-links` - 为键盘用户提供跳至主内容的链接
- `heading-hierarchy` - 标题层级按 h1→h6 顺序递增，不可跳级
- `color-not-only` - 不可仅靠颜色传达信息（须配合图标或文字）
- `dynamic-type` - 支持系统文字缩放；文字增大时避免截断（Apple Dynamic Type、MD）
- `reduced-motion` - 遵循 prefers-reduced-motion；用户请求时减少或禁用动画（Apple Reduced Motion API、MD）
- `voiceover-sr` - 提供有意义的 accessibilityLabel/accessibilityHint；VoiceOver/屏幕阅读器阅读顺序合理（Apple HIG、MD）
- `escape-routes` - 模态框与多步流程须提供取消/返回路径（Apple HIG）
- `keyboard-shortcuts` - 保留系统与无障碍快捷键；拖拽操作须提供键盘替代方案（Apple HIG）

### 2. 触控与交互（严重）

- `touch-target-size` - 最小触控目标 44×44pt（Apple）/ 48×48dp（Material）；必要时扩展可点击区域超出视觉边界
- `touch-spacing` - 触控目标之间最小间距 8px/8dp（Apple HIG、MD）
- `hover-vs-tap` - 主要交互使用点击/轻触；不可仅依赖悬停
- `loading-buttons` - 异步操作期间禁用按钮；显示加载指示或进度
- `error-feedback` - 在问题附近显示清晰的错误信息
- `cursor-pointer` - 可点击元素添加 cursor-pointer（Web）
- `gesture-conflicts` - 避免主内容区横向滑动；优先纵向滚动
- `tap-delay` - 使用 touch-action: manipulation 减少 300ms 延迟（Web）
- `standard-gestures` - 一致使用平台标准手势；勿重新定义（如右滑返回、双指缩放）（Apple HIG）
- `system-gestures` - 勿拦截系统手势（控制中心、返回滑动等）（Apple HIG）
- `press-feedback` - 按下时提供视觉反馈（ripple/高亮；MD state layers）
- `haptic-feedback` - 确认与重要操作使用触觉反馈；避免过度使用（Apple HIG）
- `gesture-alternative` - 不可仅依赖手势交互；关键操作须始终提供可见控件
- `safe-area-awareness` - 主要触控目标远离刘海、Dynamic Island、手势条与屏幕边缘
- `no-precision-required` - 避免要求用户精确点击小图标或细窄边缘
- `swipe-clarity` - 滑动操作须显示清晰可发现性提示（chevron、标签、引导）
- `drag-threshold` - 开始拖拽前设置移动阈值，避免误触拖拽

### 3. 性能（高）

- `image-optimization` - 使用 WebP/AVIF、响应式图片（srcset/sizes）、非关键资源懒加载
- `image-dimension` - 声明 width/height 或使用 aspect-ratio 防止布局偏移（Core Web Vitals: CLS）
- `font-loading` - 使用 font-display: swap/optional 避免不可见文字（FOIT）；预留空间减少布局偏移（MD）
- `font-preload` - 仅预加载关键字体；避免对每个变体滥用 preload
- `critical-css` - 优先加载首屏 CSS（内联关键 CSS 或尽早加载样式表）
- `lazy-loading` - 通过动态 import / 路由级拆分懒加载非首屏组件
- `bundle-splitting` - 按路由/功能拆分代码（React Suspense / Next.js dynamic）降低首屏负载与 TTI
- `third-party-scripts` - 第三方脚本 async/defer 加载；审计并移除不必要的脚本（MD）
- `reduce-reflows` - 避免频繁读写布局；批量读取 DOM 后再写入
- `content-jumping` - 为异步内容预留空间，避免布局跳动（Core Web Vitals: CLS）
- `lazy-load-below-fold` - 首屏以下图片与重型媒体使用 loading="lazy"
- `virtualize-lists` - 50+ 条目的列表虚拟化，提升内存效率与滚动性能
- `main-thread-budget` - 60fps 下每帧工作控制在 ~16ms 以内；重型任务移出主线程（HIG、MD）
- `progressive-loading` - 耗时 >1s 的操作使用骨架屏/shimmer，而非长时间阻塞式 spinner（Apple HIG）
- `input-latency` - 点击/滚动输入延迟控制在 ~100ms 以内（Material 响应性标准）
- `tap-feedback-speed` - 轻触后 100ms 内提供视觉反馈（Apple HIG）
- `debounce-throttle` - 高频事件（scroll、resize、input）使用 debounce/throttle
- `offline-support` - 提供离线状态提示与基本降级方案（PWA / 移动端）
- `network-fallback` - 慢网络提供降级模式（低分辨率图片、减少动效）

### 4. 风格选择（高）

- `style-match` - 风格须匹配产品类型（使用 `--design-system` 获取推荐）
- `consistency` - 全站保持同一风格
- `no-emoji-icons` - 使用 SVG 图标（Phosphor、Heroicons），勿用 emoji
- `color-palette-from-product` - 根据产品/行业选择配色（检索 `--domain color`）
- `effects-match-style` - 阴影、模糊、圆角与所选风格一致（glass / flat / clay 等）
- `platform-adaptive` - 遵循平台惯用法（iOS HIG vs Material）：导航、控件、排版、动效
- `state-clarity` - hover/pressed/disabled 状态视觉区分明确，且符合整体风格（Material state layers）
- `elevation-consistent` - 卡片、面板、模态框使用一致的 elevation/阴影层级；避免随意阴影值
- `dark-mode-pairing` - 明暗模式同步设计，保持品牌、对比度与风格一致
- `icon-style-consistent` - 全产品统一图标集/视觉语言（描边宽度、圆角）
- `system-controls` - 优先使用原生/系统控件；仅在品牌需要时自定义（Apple HIG）
- `blur-purpose` - 模糊用于表示背景可关闭（模态框、面板），不作装饰（Apple HIG）
- `primary-action` - 每屏仅一个主要 CTA；次要操作视觉从属（Apple HIG）

### 5. 布局与响应式（高）

- `viewport-meta` - width=device-width initial-scale=1（禁止禁用缩放）
- `mobile-first` - 移动优先设计，再扩展至平板与桌面
- `breakpoint-consistency` - 使用系统化断点（如 375 / 768 / 1024 / 1440）
- `readable-font-size` - 移动端正文最小 16px（避免 iOS 自动缩放）
- `line-length-control` - 移动端每行 35–60 字符；桌面端 60–75 字符
- `horizontal-scroll` - 移动端禁止横向滚动；内容须适配视口宽度
- `spacing-scale` - 使用 4pt/8dp 递增间距体系（Material Design）
- `touch-density` - 组件间距适合触控：不过密、避免误触
- `container-width` - 桌面端统一最大宽度（max-w-6xl / 7xl）
- `z-index-management` - 定义分层 z-index 刻度（如 0 / 10 / 20 / 40 / 100 / 1000）
- `fixed-element-offset` - 固定导航栏/底栏须为下层内容预留安全内边距
- `scroll-behavior` - 避免嵌套滚动区域干扰主滚动体验
- `viewport-units` - 移动端优先 min-h-dvh 而非 100vh
- `orientation-support` - 横屏模式下布局仍可读、可操作
- `content-priority` - 移动端优先展示核心内容；折叠或隐藏次要内容
- `visual-hierarchy` - 通过尺寸、间距、对比度建立层级——不可仅靠颜色

### 6. 排版与色彩（中）

- `line-height` - 正文行高 1.5–1.75
- `line-length` - 每行限制 65–75 字符
- `font-pairing` - 标题与正文字体气质匹配
- `font-scale` - 统一字号阶梯（如 12 14 16 18 24 32）
- `contrast-readability` - 浅色背景使用较深文字（如 slate-900 on white）
- `text-styles-system` - 使用平台字体体系：iOS 11 Dynamic Type 样式 / Material 5 字体角色（display、headline、title、body、label）（HIG、MD）
- `weight-hierarchy` - 用 font-weight 强化层级：标题 Bold（600–700）、正文 Regular（400）、标签 Medium（500）（MD）
- `color-semantic` - 定义语义化色彩 token（primary、secondary、error、surface、on-surface），组件中勿直接使用 hex（Material color system）
- `color-dark-mode` - 暗色模式使用去饱和/较浅色调变体，非简单反色；单独验证对比度（HIG、MD）
- `color-accessible-pairs` - 前景/背景对比度须达 4.5:1（AA）或 7:1（AAA）；使用工具验证（WCAG、MD）
- `color-not-decorative-only` - 功能性颜色（错误红、成功绿）须配合图标/文字；避免仅靠颜色表达（HIG、MD）
- `truncation-strategy` - 优先换行而非截断；截断时使用省略号，并通过 tooltip/展开提供完整文本（Apple HIG）
- `letter-spacing` - 遵循平台默认字距；正文避免过紧 tracking（HIG、MD）
- `number-tabular` - 数据列、价格、计时器使用 tabular/等宽数字，防止布局偏移
- `whitespace-balance` - 有意使用留白分组相关内容、分隔区块；避免视觉杂乱（Apple HIG）

### 7. 动效（中）

- `duration-timing` - 微交互 150–300ms；复杂过渡 ≤400ms；避免 >500ms（MD）
- `transform-performance` - 仅动画 transform/opacity；避免动画 width/height/top/left
- `loading-states` - 加载超过 300ms 时显示骨架屏或进度指示
- `excessive-motion` - 每视图最多动画 1–2 个关键元素
- `easing` - 进入用 ease-out、退出用 ease-in；UI 过渡避免 linear
- `motion-meaning` - 每个动画须表达因果关系，而非纯装饰（Apple HIG）
- `state-transition` - 状态变化（hover / active / expanded / collapsed / modal）应平滑过渡，不可瞬间切换
- `continuity` - 页面/屏幕过渡保持空间连续性（共享元素、方向性滑动）（Apple HIG）
- `parallax-subtle` - 视差效果应谨慎使用；须遵循 reduced-motion 且不造成迷失感（Apple HIG）
- `spring-physics` - 优先 spring/物理曲线，而非 linear 或 cubic-bezier，以获得自然手感（Apple HIG fluid animations）
- `exit-faster-than-enter` - 退出动画短于进入（约为进入时长的 60–70%），提升响应感（MD motion）
- `stagger-sequence` - 列表/网格项入场依次延迟 30–50ms；避免同时出现或过慢依次展示（MD）
- `shared-element-transition` - 屏幕间使用共享元素/hero 过渡保持视觉连续（MD、HIG）
- `interruptible` - 动画须可中断；用户点击/手势可立即取消进行中的动画（Apple HIG）
- `no-blocking-animation` - 动画期间不可阻塞用户输入；UI 须保持可交互（Apple HIG）
- `fade-crossfade` - 同一容器内内容替换使用 crossfade（MD）
- `scale-feedback` - 可点击卡片/按钮按下时 subtle scale（0.95–1.05）；释放后恢复（HIG、MD）
- `gesture-feedback` - 拖拽、滑动、捏合须实时跟踪手指的视觉反馈（MD Motion）
- `hierarchy-motion` - 用 translate/scale 方向表达层级：从下方进入 = 更深、向上退出 = 返回（MD）
- `motion-consistency` - 全局统一 duration/easing token；所有动画共享同一节奏与手感
- `opacity-threshold` - 淡出元素不应长期停留在 opacity 0.2 以下；要么完全淡出，要么保持可见
- `modal-motion` - 模态框/面板从触发源动画进入（scale+fade 或 slide-in），提供空间上下文（HIG、MD）
- `navigation-direction` - 前进导航向左/向上；后退向右/向下——方向逻辑一致（HIG）
- `layout-shift-avoid` - 动画不得引发布局重排或 CLS；位置变化使用 transform

### 8. 表单与反馈（中）

- `input-labels` - 每个输入框须有可见标签（不可仅用 placeholder）
- `error-placement` - 错误显示在对应字段下方
- `submit-feedback` - 提交时显示加载，随后成功/失败状态
- `required-indicators` - 标记必填字段（如星号）
- `empty-states` - 无内容时提供有用提示与操作
- `toast-dismiss` - Toast 3–5 秒后自动消失
- `confirmation-dialogs` - 破坏性操作前须确认
- `input-helper-text` - 复杂输入下方提供持久辅助说明，而非仅 placeholder（Material Design）
- `disabled-states` - 禁用元素降低 opacity（0.38–0.5）+ 光标变化 + 语义属性（MD）
- `progressive-disclosure` - 渐进展示复杂选项；避免一次性信息过载（Apple HIG）
- `inline-validation` - blur 时验证（非逐键）；用户完成输入后再显示错误（MD）
- `input-type-keyboard` - 使用语义化 input type（email、tel、number）触发正确的移动端键盘（HIG、MD）
- `password-toggle` - 密码字段提供显示/隐藏切换（MD）
- `autofill-support` - 使用 autocomplete / textContentType 属性以支持系统自动填充（HIG、MD）
- `undo-support` - 破坏性或批量操作支持撤销（如「撤销删除」toast）（Apple HIG）
- `success-feedback` - 完成操作后提供简短视觉确认（对勾、toast、颜色闪烁）（MD）
- `error-recovery` - 错误信息须包含明确恢复路径（重试、编辑、帮助链接）（HIG、MD）
- `multi-step-progress` - 多步流程显示步骤指示或进度条；允许返回（MD）
- `form-autosave` - 长表单自动保存草稿，防止误关闭丢失数据（Apple HIG）
- `sheet-dismiss-confirm` - 关闭含未保存更改的面板/模态框前须确认（Apple HIG）
- `error-clarity` - 错误信息须说明原因与修复方法（不可仅写「Invalid input」）（HIG、MD）
- `field-grouping` - 相关字段逻辑分组（fieldset/legend 或视觉分组）（MD）
- `read-only-distinction` - 只读状态在视觉与语义上须与禁用区分（MD）
- `focus-management` - 提交错误后自动聚焦首个无效字段（WCAG、MD）
- `error-summary` - 多个错误时在顶部显示摘要，并锚定至各字段（WCAG）
- `touch-friendly-input` - 移动端输入框高度 ≥44px，满足触控目标要求（Apple HIG）
- `destructive-emphasis` - 破坏性操作使用语义危险色（红），并与主要操作视觉分离（HIG、MD）
- `toast-accessibility` - Toast 不可抢夺焦点；使用 aria-live="polite" 供屏幕阅读器播报（WCAG）
- `aria-live-errors` - 表单错误使用 aria-live 区域或 role="alert" 通知屏幕阅读器（WCAG）
- `contrast-feedback` - 错误与成功状态颜色须满足 4.5:1 对比度（WCAG、MD）
- `timeout-feedback` - 请求超时须显示清晰反馈并提供重试选项（MD）

### 9. 导航模式（高）

- `bottom-nav-limit` - 底部导航最多 5 项；图标须配文字标签（Material Design）
- `drawer-usage` - 抽屉/侧边栏用于次级导航，非主要操作（Material Design）
- `back-behavior` - 返回导航须可预测且一致；保留滚动/状态（Apple HIG、MD）
- `deep-linking` - 所有关键屏幕须可通过深层链接/URL 访问，便于分享与通知（Apple HIG、MD）
- `tab-bar-ios` - iOS：顶级导航使用底部 Tab Bar（Apple HIG）
- `top-app-bar-android` - Android：主要结构使用 Top App Bar 与导航图标（Material Design）
- `nav-label-icon` - 导航项须同时有图标与文字标签；纯图标导航损害可发现性（MD）
- `nav-state-active` - 当前位置在导航中须视觉高亮（颜色、字重、指示器）（HIG、MD）
- `nav-hierarchy` - 主导航（tabs/底栏）与次级导航（drawer/设置）须清晰分离（MD）
- `modal-escape` - 模态框与面板须提供明确的关闭入口；移动端支持下滑关闭（Apple HIG）
- `search-accessible` - 搜索须易于触达（顶栏或 tab）；提供最近/建议查询（MD）
- `breadcrumb-web` - Web：3 层以上深层级使用面包屑辅助定位（MD）
- `state-preservation` - 返回时须恢复先前滚动位置、筛选状态与输入（HIG、MD）
- `gesture-nav-support` - 支持系统手势导航（iOS 右滑返回、Android 预测性返回）且无冲突（HIG、MD）
- `tab-badge` - 导航项 badge 应谨慎使用，表示未读/待处理；用户访问后清除（HIG、MD）
- `overflow-menu` - 操作超出可用空间时使用 overflow/更多菜单，而非强行堆叠（MD）
- `bottom-nav-top-level` - 底部导航仅用于顶级屏幕；不可在其内嵌套子导航（MD）
- `adaptive-navigation` - 大屏（≥1024px）优先侧边栏；小屏使用底部/顶部导航（Material Adaptive）
- `back-stack-integrity` - 不可静默重置导航栈或意外跳回首页（HIG、MD）
- `navigation-consistency` - 导航位置全站一致；不可因页面类型而改变
- `avoid-mixed-patterns` - 同一层级不可混用 Tab + Sidebar + Bottom Nav
- `modal-vs-navigation` - 模态框不可用于主导航流程；会破坏用户路径（HIG）
- `focus-on-route-change` - 页面切换后将焦点移至主内容区，服务屏幕阅读器用户（WCAG）
- `persistent-nav` - 深层页面仍须能触达核心导航；子流程中不可完全隐藏（HIG、MD）
- `destructive-nav-separation` - 危险操作（删除账户、登出）须与普通导航项在视觉与空间上分离（HIG、MD）
- `empty-nav-state` - 导航目标不可用时须说明原因，不可静默隐藏（MD）

### 10. 图表与数据（低）

- `chart-type` - 图表类型匹配数据类型（趋势 → 折线、对比 → 柱状、占比 → 饼/环）
- `color-guidance` - 使用可访问配色；避免仅用红/绿组合（色觉障碍用户）（WCAG、MD）
- `data-table` - 提供表格替代方案以支持无障碍；仅图表对屏幕阅读器不友好（WCAG）
- `pattern-texture` - 以图案、纹理或形状补充颜色，使数据在无颜色时仍可区分（WCAG、MD）
- `legend-visible` - 始终显示图例；靠近图表放置，不可脱离至滚动折叠下方（MD）
- `tooltip-on-interact` - 悬停（Web）或轻触（移动端）显示精确数值的工具提示/数据标签（HIG、MD）
- `axis-labels` - 坐标轴标注单位与可读刻度；移动端避免截断或旋转标签
- `responsive-chart` - 小屏图表须重排或简化（如横向柱图替代纵向、减少刻度）
- `empty-data-state` - 无数据时显示有意义空状态（「暂无数据」+ 引导），而非空白图表（MD）
- `loading-chart` - 图表数据加载时使用骨架屏或 shimmer 占位；勿显示空坐标轴框架
- `animation-optional` - 图表入场动画须遵循 prefers-reduced-motion；数据应立即可读（HIG）
- `large-dataset` - 1000+ 数据点须聚合或采样；提供下钻查看详情，而非全部渲染（MD）
- `number-formatting` - 坐标轴与标签使用符合 locale 的数字、日期、货币格式（HIG、MD）
- `touch-target-chart` - 可交互图表元素（点、扇区）须 ≥44pt 点击区域或触摸时扩展（Apple HIG）
- `no-pie-overuse` - 避免饼/环图展示 >5 类；改用柱状图更清晰
- `contrast-data` - 数据线/柱与背景对比度 ≥3:1；数据文字标签 ≥4.5:1（WCAG）
- `legend-interactive` - 图例应可点击切换系列可见性（MD）
- `direct-labeling` - 小数据集直接在图表上标注数值，减少视线移动
- `tooltip-keyboard` - 工具提示内容须可通过键盘访问，不可仅依赖悬停（WCAG）
- `sortable-table` - 数据表格须支持排序，aria-sort 指示当前排序状态（WCAG）
- `axis-readability` - 坐标轴刻度不可过密；保持可读间距，小屏自动跳过
- `data-density` - 限制单图信息密度，避免认知过载；必要时拆分为多图
- `trend-emphasis` - 强调数据趋势而非装饰；避免厚重渐变/阴影遮挡数据
- `gridline-subtle` - 网格线低对比度（如 gray-200），不与数据争抢视觉
- `focusable-elements` - 可交互图表元素（点、柱、扇区）须支持键盘导航（WCAG）
- `screen-reader-summary` - 提供文本摘要或 aria-label 描述图表核心洞察，供屏幕阅读器使用（WCAG）
- `error-state-chart` - 数据加载失败须显示错误信息与重试操作，而非损坏/空白图表
- `export-option` - 数据密集型产品提供 CSV/图片导出
- `drill-down-consistency` - 下钻交互须保持清晰返回路径与层级面包屑
- `time-scale-clarity` - 时间序列图表须清晰标注时间粒度（日/周/月）并支持切换

## 如何使用

使用下方 CLI 工具检索特定域。

---

# 前置条件

检查是否已安装 Python：

```bash
python --version || python --version
```

若未安装 Python，请根据用户操作系统安装：

**macOS：**
```bash
brew install python3
```

**Ubuntu/Debian：**
```bash
sudo apt update && sudo apt install python3
```

**Windows：**
```powershell
winget install Python.Python.3.12
```

---

## 如何使用本技能

当用户提出以下任一需求时使用本技能：

| 场景 | 触发示例 | 从何处开始 |
|----------|-----------------|------------|
| **新项目 / 页面** | "做一个 landing page"、"搭建一个 dashboard" | 步骤 1 → 步骤 2（设计系统） |
| **新组件** | "做一个定价卡片"、"加一个弹窗" | 步骤 3（领域检索：style、ux） |
| **选择风格 / 配色 / 字体** | "金融科技应用适合什么风格？"、"推荐配色" | 步骤 2（设计系统） |
| **审查现有 UI** | "审查这页的 UX 问题"、"检查无障碍" | 上文快速参考检查清单 |
| **修复 UI 缺陷** | "按钮 hover 坏了"、"加载时布局跳动" | 快速参考 → 对应章节 |
| **改进 / 优化** | "让页面更快"、"改善移动端体验" | 步骤 3（领域检索：ux、react） |
| **实现深色模式** | "添加深色模式支持" | 步骤 3（领域：style "dark mode"） |
| **添加图表 / 数据可视化** | "加一个分析 dashboard 图表" | 步骤 3（领域：chart） |
| **技术栈最佳实践** | "React 性能技巧"、"SwiftUI 导航" | 步骤 4（技术栈检索） |

按以下工作流执行：

### 步骤 1：分析用户需求

从用户请求中提取关键信息：
- **产品类型**：娱乐（社交、视频、音乐、游戏）、工具（扫描、编辑、转换）、效率（任务管理、笔记、日历），或混合型
- **目标受众**：C 端消费者；考虑年龄段、使用场景（通勤、休闲、工作）
- **风格关键词**：活泼、鲜明、极简、深色模式、内容优先、沉浸式等
- **技术栈**：React Native（本项目唯一技术栈）

### 步骤 2：生成设计系统（必需）

**始终从 `--design-system` 开始**，以获取带推理依据的完整推荐：

```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

该命令将：
1. 并行检索多个领域（product、style、color、landing、typography）
2. 应用 `ui-reasoning.csv` 中的推理规则以选择最佳匹配
3. 返回完整设计系统：pattern、style、colors、typography、effects
4. 包含应避免的反模式

**示例：**
```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### 步骤 2b：持久化设计系统（主文件 + 覆盖模式）

若需**跨会话分层检索**设计系统，添加 `--persist`：

```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<query>" --design-system --persist -p "Project Name"
```

将创建：
- `design-system/MASTER.md` — 全局唯一事实来源，包含全部设计规则
- `design-system/pages/` — 页面级覆盖规则目录

**带页面级覆盖：**
```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

还将创建：
- `design-system/pages/dashboard.md` — 相对主文件的页面级差异规则

**分层检索如何工作：**
1. 构建特定页面（如「结账」）时，先查看 `design-system/pages/checkout.md`
2. 若页面文件存在，其规则**覆盖**主文件
3. 若不存在，则仅使用 `design-system/MASTER.md`

**上下文感知检索提示：**
```
我正在构建 [页面名称] 页面。请阅读 design-system/MASTER.md。
同时检查 design-system/pages/[page-name].md 是否存在。
若页面文件存在，优先采用其规则。
若不存在，则仅使用主文件规则。
现在，请生成代码……
```

### 步骤 3：按需补充详细检索（按需）

获得设计系统后，使用领域检索获取补充细节：

```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<keyword>" --domain <domain> [-n <max_results>]
```

**何时使用详细检索：**

| 需求 | Domain | 示例 |
|------|--------|---------|
| 产品类型模式 | `product` | `--domain product "entertainment social"` |
| 更多风格选项 | `style` | `--domain style "glassmorphism dark"` |
| 配色方案 | `color` | `--domain color "entertainment vibrant"` |
| 字体搭配 | `typography` | `--domain typography "playful modern"` |
| 图表推荐 | `chart` | `--domain chart "real-time dashboard"` |
| UX 最佳实践 | `ux` | `--domain ux "animation accessibility"` |
| 落地页结构 | `landing` | `--domain landing "hero social-proof"` |
| React Native 性能 | `react` | `--domain react "rerender memo list"` |
| 应用界面无障碍 | `web` | `--domain web "accessibilityLabel touch safe-areas"` |
| AI 提示词 / CSS 关键词 | `prompt` | `--domain prompt "minimalism"` |

### 步骤 4：技术栈指南（React Native）

获取 React Native 实现层面的最佳实践：

```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<keyword>" --stack react-native
```

---

## 检索参考

### 可用领域

| Domain | 用途 | 示例关键词 |
|--------|---------|------------------|
| `product` | 产品类型推荐 | SaaS、e-commerce、portfolio、healthcare、beauty、service |
| `style` | UI 风格、配色、效果 | glassmorphism、minimalism、dark mode、brutalism |
| `typography` | 字体搭配、Google Fonts | elegant、playful、professional、modern |
| `color` | 按产品类型的配色 | saas、ecommerce、healthcare、beauty、fintech、service |
| `landing` | 页面结构、CTA 策略 | hero、hero-centric、testimonial、pricing、social-proof |
| `chart` | 图表类型、库推荐 | trend、comparison、timeline、funnel、pie |
| `ux` | 最佳实践、反模式 | animation、accessibility、z-index、loading |
| `react` | React/Next.js 性能 | waterfall、bundle、suspense、memo、rerender、cache |
| `web` | 应用界面指南（iOS/Android/React Native） | accessibilityLabel、touch targets、safe areas、Dynamic Type |
| `prompt` | AI 提示词、CSS 关键词 | （风格名称） |

### 可用技术栈

| Stack | 关注点 |
|-------|-------|
| `react-native` | Components、Navigation、Lists |

---

## 示例工作流

**用户请求：**「做一个 AI 搜索首页。」

### 步骤 1：分析需求
- 产品类型：工具（AI 搜索引擎）
- 目标受众：追求快速、智能搜索的 C 端用户
- 风格关键词：现代、极简、内容优先、深色模式
- 技术栈：React Native（本项目唯一技术栈）

### 步骤 2：生成设计系统（必需）

```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "AI search tool modern minimal" --design-system -p "AI Search"
```

**输出：** 含 pattern、style、colors、typography、effects 及反模式的完整设计系统。

### 步骤 3：按需补充详细检索

```bash
# 获取现代工具类产品的风格选项
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "minimalism dark mode" --domain style

# 获取搜索交互与加载的 UX 最佳实践
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "search loading animation" --domain ux
```

### 步骤 4：技术栈指南

```bash
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "list performance navigation" --stack react-native
```

**随后：** 综合设计系统与详细检索结果并实现设计。

---

## 输出格式

`--design-system` 标志支持两种输出格式：

```bash
# ASCII 框（默认）— 适合终端显示
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "fintech crypto" --design-system

# Markdown — 适合文档
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "fintech crypto" --design-system -f markdown
```

---

## 获得更好结果的技巧

### 查询策略

- 使用**多维关键词** — 组合产品 + 行业 + 调性 + 密度：如 `"entertainment social vibrant content-dense"`，而非仅 `"app"`
- 同一需求尝试不同关键词：`"playful neon"` → `"vibrant dark"` → `"content-first minimal"`
- 先使用 `--design-system` 获取完整推荐，再对不确定的维度用 `--domain` 深入检索
- 实现层面指导务必加上 `--stack react-native`

### 常见卡点

| 问题 | 处理方式 |
|---------|------------|
| 无法确定风格/配色 | 换关键词重新运行 `--design-system` |
| 深色模式对比度问题 | 快速参考 §6：`color-dark-mode` + `color-accessible-pairs` |
| 动画不自然 | 快速参考 §7：`spring-physics` + `easing` + `exit-faster-than-enter` |
| 表单 UX 差 | 快速参考 §8：`inline-validation` + `error-clarity` + `focus-management` |
| 导航令人困惑 | 快速参考 §9：`nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| 小屏布局错乱 | 快速参考 §5：`mobile-first` + `breakpoint-consistency` |
| 性能卡顿 | 快速参考 §3：`virtualize-lists` + `main-thread-budget` + `debounce-throttle` |

### 交付前检查清单

- 实现前运行 `--domain ux "animation accessibility z-index loading"` 作为 UX 校验
- 最终审查时对照快速参考 **§1–§3**（严重 + 高）
- 在 375px（小屏手机）及横屏方向下测试
- 在开启 **reduced-motion** 且 **Dynamic Type** 为最大字号时验证行为
- 单独检查深色模式对比度（勿假设浅色模式数值可直接沿用）
- 确认所有触控目标 ≥44pt，且无内容被安全区域遮挡

---

## 专业 UI 通用规则

以下为常被忽视、导致 UI 显得不专业的要点：
适用范围说明：以下规则面向应用 UI（iOS/Android/React Native/Flutter），而非桌面 Web 交互模式。

### 图标与视觉元素

- 默认图标库使用 **Phosphor (`@phosphor-icons/react`)**。`src/ui-ux-pro-max/data/icons.csv` 中列出的只是常用推荐图标，不是完整集合。
- 当推荐表中找不到合适的图标时：
  - **优先继续从 Phosphor 的完整图标集中选择任何语义更贴切的图标**；
  - 如果 Phosphor 也没有理想选项，可以使用 **Heroicons (`@heroicons/react`)** 作为备选，注意保持风格一致（线性/填充、笔画粗细、圆角风格）。

| 规则 | 标准 | 避免 | 重要性 |
|------|----------|--------|----------------|
| **不用 Emoji 作结构图标** | 使用矢量图标（如 Phosphor `@phosphor-icons/react`、Heroicons `@heroicons/react`、react-native-vector-icons、`@expo/vector-icons`）。 | 在导航、设置或系统控件中使用 Emoji（🎨 🚀 ⚙️）。 | Emoji 依赖字体、跨平台不一致，且无法通过设计令牌控制。 |
| **仅使用矢量资源** | 使用 SVG 或平台矢量图标，清晰缩放并支持主题。 | 会模糊或像素化的栅格 PNG 图标。 | 保证可缩放、清晰渲染及明暗主题适配。 |
| **稳定的交互状态** | 按压状态用颜色、透明度或 elevation 过渡，不改变布局边界。 | 导致周围内容位移或视觉抖动的布局变换。 | 避免不稳定交互，在移动端保持流畅动效与感知品质。 |
| **正确使用品牌 Logo** | 使用官方品牌资源并遵循使用规范（间距、颜色、留白）。 | 猜测路径、擅自改色或修改比例。 | 避免品牌误用，符合法律与平台要求。 |
| **图标尺寸一致** | 将图标尺寸定义为设计令牌（如 icon-sm、icon-md = 24pt、icon-lg）。 | 随意混用 20pt / 24pt / 28pt 等任意值。 | 保持界面节奏与视觉层级。 |
| **描边一致** | 同一视觉层使用一致描边宽度（如 1.5px 或 2px）。 | 随意混用粗细描边。 | 描边不一致会降低精致感与统一性。 |
| **填充与线框规范** | 同一层级仅用一种图标风格。 | 在同一层级混用填充与线框图标。 | 保持语义清晰与风格连贯。 |
| **最小触控目标** | 交互区域至少 44×44pt（图标较小时用 hitSlop 扩展）。 | 小图标无扩展点击区域。 | 满足无障碍与平台可用性标准。 |
| **图标对齐** | 与文字基线对齐并保持一致内边距。 | 图标错位或周围间距不一致。 | 避免细微失衡降低感知品质。 |
| **图标对比度** | 遵循 WCAG：小元素 4.5:1，较大 UI 字形至少 3:1。 | 与背景对比度过低的图标。 | 确保明暗模式下均可访问。 |


### 交互（应用）

| 规则 | 应当 | 避免 |
|------|----|----- |
| **点击反馈** | 80–150ms 内提供清晰的按压反馈（ripple/opacity/elevation） | 点击无视觉响应 |
| **动画时长** | 微交互约 150–300ms，使用平台原生 easing | 瞬时过渡或过慢动画（>500ms） |
| **无障碍焦点** | 读屏焦点顺序与视觉顺序一致，标签描述清晰 | 无标签控件或混乱的焦点遍历 |
| **禁用状态清晰** | 使用禁用语义（`disabled`/原生 disabled 属性）、降低强调、不可点击 | 看似可点却无响应的控件 |
| **最小触控目标** | 点击区域 ≥44×44pt（iOS）或 ≥48×48dp（Android），图标较小时扩展热区 | 过小点击区或无内边距的纯图标热区 |
| **手势冲突预防** | 每区域一种主手势，避免嵌套点击/拖拽冲突 | 重叠手势导致误操作 |
| **语义化原生控件** | 优先使用原生交互基元（`Button`、`Pressable` 及平台等价物）并设置正确无障碍角色 | 无语义的通用容器作主控件 |

### 明暗模式对比度

| 规则 | 应当 | 避免 |
|------|----|----- |
| **浅色表面可读性** | 卡片/表面与背景有足够不透明度/elevation 以区分层级 | 过度透明导致层级模糊 |
| **浅色文字对比度** | 正文在浅色表面上对比度 ≥4.5:1 | 低对比度灰色正文 |
| **深色文字对比度** | 主文字 ≥4.5:1，次要文字在深色表面上 ≥3:1 | 深色模式下文字融入背景 |
| **边框与分隔线可见性** | 两种主题下分隔线均可见（不仅浅色模式） | 某主题下边框消失 |
| **状态对比度一致** | 按压/聚焦/禁用状态在明暗主题下同样可辨 | 仅为一类主题定义交互状态 |
| **令牌驱动主题** | 使用映射到各主题的语义色令牌（表面/文字/图标） | 每屏硬编码十六进制色值 |
| **遮罩与弹层可读性** | 使用足够强的模态遮罩隔离前景（通常 40–60% 黑） | 遮罩过弱导致背景与前景竞争 |

### 布局与间距

| 规则 | 应当 | 避免 |
|------|----|----- |
| **安全区域合规** | 固定顶栏、标签栏、底部 CTA 栏均尊重上下安全区 | 固定 UI 置于刘海、状态栏或手势区下 |
| **系统栏留白** | 为状态/导航栏及手势 Home 指示条留出间距 | 可点击内容与系统 UI 重叠 |
| **内容宽度一致** | 按设备类型（手机/平板）保持可预测的内容宽度 | 各屏随意混用宽度 |
| **8dp 间距节奏** | 内边距/间隙/区块间距使用一致的 4/8dp 体系 | 无节奏的随意间距增量 |
| **可读行宽** | 大屏长文保持可读（平板避免段落贴边） | 全宽长文损害可读性 |
| **区块间距层级** | 按层级定义垂直节奏（如 16/24/32/48） | 同级 UI 间距不一致 |
| **断点自适应边距** | 更宽屏与横屏增加水平内边距 | 所有尺寸/方向使用相同窄边距 |
| **滚动与固定元素共存** | 列表上下留出 inset，避免被固定栏遮挡 | 滚动内容被粘性顶/底栏遮住 |

---

## 交付前检查清单

交付 UI 代码前，请核对以下项：
适用范围说明：本清单面向应用 UI（iOS/Android/React Native/Flutter）。

### 视觉质量
- [ ] 未用 Emoji 作图标（应使用 SVG）
- [ ] 所有图标来自同一图标族且风格一致
- [ ] 使用官方品牌资源，比例与留白正确
- [ ] 按压态视觉不改变布局边界、不引起抖动
- [ ] 一致使用语义主题令牌（无每屏随意硬编码颜色）

### 交互
- [ ] 所有可点击元素有清晰按压反馈（ripple/opacity/elevation）
- [ ] 触控目标满足最小尺寸（iOS ≥44×44pt，Android ≥48×48dp）
- [ ] 微交互时长在 150–300ms，easing 符合原生手感
- [ ] 禁用状态视觉清晰且不可交互
- [ ] 读屏焦点顺序与视觉顺序一致，交互标签描述清晰
- [ ] 手势区域避免嵌套/冲突（点击/拖拽/返回滑动冲突）

### 明暗模式
- [ ] 明暗模式下主文字对比度均 ≥4.5:1
- [ ] 明暗模式下次要文字对比度均 ≥3:1
- [ ] 分隔线/边框及交互状态在两种模式下均可区分
- [ ] 模态/抽屉遮罩不透明度足以保证前景可读（通常 40–60% 黑）
- [ ] 交付前两种主题均已测试（非仅由单一主题推断）

### 布局
- [ ] 顶栏、标签栏、底部 CTA 栏均尊重安全区域
- [ ] 滚动内容未被固定/粘性栏遮挡
- [ ] 已在小屏手机、大屏手机、平板（竖屏 + 横屏）上验证
- [ ] 水平内边距/边距随设备尺寸与方向正确适配
- [ ] 组件、区块、页面层级均保持 4/8dp 间距节奏
- [ ] 大屏长文行宽仍可读（无贴边全宽段落）

### 无障碍
- [ ] 有意义的图片/图标均有 accessibility 标签
- [ ] 表单字段有标签、提示与清晰错误信息
- [ ] 颜色不是唯一指示手段
- [ ] 支持 reduced motion 与动态字号且布局不崩坏
- [ ] 无障碍 trait/role/state（选中、禁用、展开）播报正确
