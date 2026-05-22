# PPT 制作套件 · 默认设计系统

> **用途**：16:9 双案例幻灯片预览与导出的通用视觉基准。  
> **素材**：由用户在 `public/assets/materials/` 自备，套件仅提供 `placeholder.png`。

## 色彩（与 design-tokens.css 对齐）

| 角色 | 说明 |
|------|------|
| 背景 | 暖白编辑纸感 `#FCFBF9` |
| 前景 | 深墨 `#0F1E24` |
| 强调 | 铜金 `#B89047` |

## 幻灯片结构

1. 页眉：分区标签、主标题、主题副题
2. 双案例区：左右分栏（50-50 / 60-40 / 65-35）
3. 页脚：项目配置中的 `footerText`

## 字体

- 标题与正文：系统无衬线 + 设计令牌 `--type-*`
- 导出离屏时按 `export-capture.css` 与 1024px 预览同比例缩放

## 项目示例

转轮地质案例见 [`examples/zhuanlun/design-system/MASTER.md`](../examples/zhuanlun/design-system/MASTER.md)。
