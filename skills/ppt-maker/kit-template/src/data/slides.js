import { projectConfig } from '../config/project.js'

export const ASSET_BASE = projectConfig.content.assetBase

const PLACEHOLDER = 'placeholder.png'

export const slides = [
  {
    id: 1,
    layout: 'dual',
    sectionLabel: '幻灯片 一',
    sectionIndex: '01',
    title: '案例主题 A · 案例主题 B',
    theme: '副标题或研究主题说明',
    layoutRatio: '50-50',
    cases: [
      {
        index: 'A',
        name: '案例 A',
        subtitle: '子标题',
        description: '在此填写案例 A 的说明文字。将配图放入 public/assets/materials/ 并在 images 中填写文件名。',
        images: [PLACEHOLDER, PLACEHOLDER],
        imageFit: 'contain',
        imageFrameType: 'hud',
        tags: ['标签一', '标签二'],
        metadata: [
          { label: '指标一', value: '数值' },
          { label: '指标二', value: '数值' },
        ],
      },
      {
        index: 'B',
        name: '案例 B',
        subtitle: '子标题',
        description: '在此填写案例 B 的说明文字。',
        images: [PLACEHOLDER, PLACEHOLDER],
        imageFit: 'contain',
        imageFrameType: 'paper',
        tags: ['标签一', '标签二'],
        metadata: [
          { label: '指标一', value: '数值' },
          { label: '指标二', value: '数值' },
        ],
      },
    ],
  },
  {
    id: 2,
    layout: 'dual',
    sectionLabel: '幻灯片 二',
    sectionIndex: '02',
    title: '案例主题 C · 案例主题 D',
    theme: '副标题或研究主题说明',
    layoutRatio: '60-40',
    cases: [
      {
        index: 'A',
        name: '案例 C',
        subtitle: '子标题',
        description: '60-40 分栏布局示例页。',
        images: [PLACEHOLDER],
        imageFit: 'cover',
        imageFrameType: 'paper',
        tags: ['标签'],
        metadata: [{ label: '指标', value: '数值' }],
      },
      {
        index: 'B',
        name: '案例 D',
        subtitle: '子标题',
        description: '右侧窄栏案例。',
        images: [PLACEHOLDER],
        imageFit: 'cover',
        imageFrameType: 'hud',
        tags: ['标签'],
        metadata: [{ label: '指标', value: '数值' }],
      },
    ],
  },
  {
    id: 3,
    layout: 'dual',
    sectionLabel: '幻灯片 三',
    sectionIndex: '03',
    title: '案例主题 E · 案例主题 F',
    theme: '副标题或研究主题说明',
    layoutRatio: '65-35',
    cases: [
      {
        index: 'A',
        name: '案例 E',
        subtitle: '子标题',
        description: '65-35 分栏布局示例页。',
        images: [PLACEHOLDER, PLACEHOLDER],
        imageFit: 'contain',
        imageFrameType: 'hud',
        tags: ['标签'],
        metadata: [{ label: '指标', value: '数值' }],
      },
      {
        index: 'B',
        name: '案例 F',
        subtitle: '子标题',
        description: '右侧窄栏案例。',
        images: [PLACEHOLDER],
        imageFit: 'contain',
        imageFrameType: 'paper',
        tags: ['标签'],
        metadata: [{ label: '指标', value: '数值' }],
      },
    ],
  },
]

export function imageUrl(filename) {
  return `${ASSET_BASE}${filename}`
}

export function slideHash(id) {
  return `slide-${id}`
}
