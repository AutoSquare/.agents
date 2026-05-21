# Logo 使用规范

各营销物料中 Logo 正确落地的指南。

## Logo 变体

### 主变体
| 变体 | 文件名 | 使用场景 |
|------|--------|----------|
| Full Horizontal | logo-full-horizontal.{ext} | 网站页眉、文档 |
| Stacked | logo-stacked.{ext} | 方形区域、社交头像 |
| Icon Only | logo-icon.{ext} | Favicon、应用图标、小尺寸 |
| Wordmark Only | logo-wordmark.{ext} | 图标已单独出现时 |

### 配色变体
| 变体 | 使用场景 |
|------|----------|
| Full Color | 白底 / 浅底默认 |
| Reversed | 深色背景 |
| Monochrome Dark | 浅色背景且无法使用彩色时 |
| Monochrome Light | 深色背景且无法使用彩色时 |

## 安全区

### 最小安全区

Logo 周围留白应等于标识（图标部分）的高度。

```
    ┌─────────────────────────────┐
    │           [x]               │
    │   ┌───────────────────┐     │
    │   │                   │     │
[x] │   │    [LOGO]         │ [x] │
    │   │                   │     │
    │   └───────────────────┘     │
    │           [x]               │
    └─────────────────────────────┘
```

其中 [x] = 标识高度

## 最小尺寸

### 数字媒体
| 格式 | 最小宽度 | 说明 |
|------|----------|------|
| Full Logo | 120px | 各元素清晰可读 |
| Icon Only | 24px | Favicon / 小图标 |
| Icon Only | 32px | UI 元素 |

### 印刷
| 格式 | 最小宽度 | 说明 |
|------|----------|------|
| Full Logo | 35mm | 名片、信纸 |
| Icon Only | 10mm | 小型印刷品 |

## 配色使用

### 批准背景
| 背景 | Logo 版本 |
|------|-----------|
| White | Full color or dark mono |
| Light gray (#F5F5F5+) | Full color or dark mono |
| Brand primary | Reversed (white) |
| Dark (#333 or darker) | Reversed (white) |
| Photography | Ensure sufficient contrast |

### 配色规则
1. 禁止在批准色板外更改 Logo 颜色
2. 禁止对 Logo 使用渐变
3. 禁止对 Logo 元素设置透明度
4. 禁止添加阴影或特效

## 错误用法

### 绝对禁止
- ❌ 拉伸或压缩 Logo
- ❌ 倾斜旋转
- ❌ 添加投影
- ❌ 使用渐变填充
- ❌ 使用未批准颜色
- ❌ 添加描边或轮廓
- ❌ 置于杂乱背景
- ❌ 裁剪任意部分
- ❌ 重排元素
- ❌ 附加额外元素

### 示意对比
```
WRONG: Stretched      WRONG: Rotated       WRONG: Wrong color
┌──────────────┐      ┌────────┐          ┌────────┐
│   L O G O    │      │  /    │          │ LOGO   │ <- wrong color
└──────────────┘      │ /LOGO │          └────────┘
                      └───────/
```

## 联合品牌

### 合作方 Logo 规范
1. 视觉权重对等（同高）
2. 两 Logo 之间留足间距
3. 必要时使用分隔线
4. 均使用各自批准配色
5. 安全区规则同时适用

### 布局选项
```
Option A: Side by side with divider
[OUR LOGO] | [PARTNER LOGO]

Option B: Stacked
    [OUR LOGO]
        +
  [PARTNER LOGO]
```

## 文件格式

### 推荐格式
| 用途 | 格式 | 说明 |
|------|------|------|
| Web | SVG | 首选，可缩放 |
| Web fallback | PNG | 带透明通道 |
| Print | PDF | 矢量，高质量 |
| Print alt | EPS | 旧系统兼容 |
| Documents | PNG | 高分辨率（300dpi） |

### 文件组织
```
assets/logos/
├── full-horizontal/
│   ├── logo-full-color.svg
│   ├── logo-full-color.png
│   ├── logo-reversed.svg
│   ├── logo-mono-dark.svg
│   └── logo-mono-light.svg
├── icon-only/
│   ├── icon-full-color.svg
│   ├── icon-reversed.svg
│   └── favicon.ico
└── monochrome/
    ├── logo-black.svg
    └── logo-white.svg
```

## 平台规范

### 社交媒体
| 平台 | 格式 | 尺寸 | 说明 |
|------|------|------|------|
| LinkedIn | PNG | 300x300px | Icon only |
| Twitter/X | PNG | 400x400px | Icon only |
| Facebook | PNG | 180x180px | Icon only |
| Instagram | PNG | 320x320px | Icon only |

### 网站
| 位置 | 变体 | 尺寸 |
|------|------|------|
| Header | Full horizontal | 120-200px width |
| Footer | Full horizontal | 100-150px width |
| Favicon | Icon only | 32x32px |
| Apple Touch | Icon only | 180x180px |

### 文档
| 文档 | 变体 | 位置 |
|------|------|------|
| Letterhead | Full horizontal | Top left |
| Presentation | Icon + wordmark | Title slide |
| Report | Full horizontal | Cover + footer |

## Logo 审批流程

### 使用前确认
1. 确认版本正确
2. 检查背景兼容性
3. 满足最小尺寸
4. 分配足够安全区
5. 对照本规范复核

### 申请特批

非标准用法须：
1. 提交含拟用方式的 mockup
2. 说明媒介与受众
3. 等待品牌团队批准
4. 记录已批准的例外
