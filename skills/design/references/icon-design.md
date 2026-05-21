# 图标设计参考

使用 Gemini 3.1 Pro Preview 的 AI 驱动 SVG 图标生成。15 种风格、12 个类别、多尺寸导出。

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/icon/generate.py` | 用 Gemini 3.1 Pro Preview 生成 SVG 图标 |

## 命令

### 生成单个图标

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "settings gear" --style outlined
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "shopping cart" --style filled --color "#6366F1"
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --name "dashboard" --category navigation --style duotone
```

### 批量生成变体

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "cloud upload" --batch 4 --output-dir ./icons
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "notification bell" --batch 6 --style outlined --output-dir ./icons
```

### 生成多尺寸

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "user profile" --sizes "16,24,32,48" --output-dir ./icons
```

### 列出风格/类别

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --list-styles
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --list-categories
```

## CLI 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `--prompt, -p` | 图标描述 | 必填 |
| `--name, -n` | 图标名称（用于文件名） | - |
| `--style, -s` | 图标风格（15 种） | - |
| `--category, -c` | 图标类别（上下文） | - |
| `--color` | 主色十六进制 | currentColor |
| `--size` | 显示尺寸（px） | 24 |
| `--viewbox` | SVG viewBox 尺寸 | 24 |
| `--output, -o` | 输出文件路径 | 自动 |
| `--output-dir` | 输出目录（批量） | ./icons |
| `--batch` | 变体数量 | - |
| `--sizes` | 逗号分隔尺寸 | - |

## 可用风格

| 风格 | 描边 | 填充 | 最适合 |
|------|------|------|--------|
| outlined | 2px | none | UI 界面、Web 应用 |
| filled | 0 | solid | 移动应用、导航栏 |
| duotone | 0 | dual | 营销、落地页 |
| thin | 1-1.5px | none | 奢侈品牌、编辑类 |
| bold | 3px | none | 页眉、Hero 区 |
| rounded | 2px | none | 友好型应用、健康 |
| sharp | 2px | none | 科技、金融科技、企业 |
| flat | 0 | solid | Material Design、Google 风格 |
| gradient | 0 | gradient | 现代品牌、SaaS |
| glassmorphism | 1px | semi | 现代 UI、叠加层 |
| pixel | 0 | solid | 游戏、复古 |
| hand-drawn | varies | none | 手工艺、创意 |
| isometric | 1-2px | partial | 技术文档、信息图 |
| glyph | 0 | solid | 系统 UI、紧凑布局 |
| animated-ready | 2px | varies | 交互 UI、引导流程 |

## 图标类别

| 类别 | 图标 |
|------|------|
| navigation | 箭头、菜单、首页、chevron |
| action | 编辑、删除、保存、下载、上传 |
| communication | 邮件、聊天、电话、通知 |
| media | 播放、暂停、音量、相机 |
| file | 文档、文件夹、压缩包、云 |
| user | 用户、群组、资料、设置 |
| commerce | 购物车、包、钱包、信用卡 |
| data | 图表、曲线、分析、仪表盘 |
| development | 代码、终端、缺陷、git、API |
| social | 心、星、书签、奖杯 |
| weather | 太阳、月亮、云、雨 |
| map | 图钉、位置、指南针、地球 |

## SVG 最佳实践

- **ViewBox**：使用 `0 0 24 24`（标准）或 `0 0 16 16`（紧凑）
- **颜色**：使用 `currentColor` 以便 CSS 继承，避免硬编码颜色
- **可访问性**：始终包含 `<title>` 元素
- **优化**：路径节点最少，不嵌入字体或位图
- **尺寸**：按 24px 设计，在 16px 与 48px 下测试清晰度
- **描边**：outlined 风格使用 `stroke-linecap="round"` 与 `stroke-linejoin="round"`

## 模型

- **gemini-3.1-pro-preview**：推理能力强、令牌效率高、事实一致性好
- 纯文本输出（SVG 为 XML 文本）— 无需图像生成 API
- 支持结构化输出以保持 SVG 格式一致

## 工作流

1. 描述图标 → `--prompt "settings gear"`
2. 选择风格 → `--style outlined`
3. 生成 → 脚本输出 .svg 文件
4. 可选批量 → `--batch 4` 生成变体
5. 多尺寸导出 → `--sizes "16,24,32,48"`

## 环境配置

```bash
export GEMINI_API_KEY="your-key"
pip install google-genai
```
