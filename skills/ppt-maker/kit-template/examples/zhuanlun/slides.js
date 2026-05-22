import { projectConfig } from '../../src/config/project.js'

export const ASSET_BASE = projectConfig.content.assetBase

export const slides = [
  {
    id: 1,
    sectionLabel: '代表应用 一',
    sectionIndex: '01',
    title: 'CZ铁路 · 成昆铁路',
    theme: '岩体内部三维结构发育规律',
    layoutRatio: '50-50', // Symmetric layout for the first slide
    cases: [
      {
        index: 'A',
        name: 'CZ铁路',
        subtitle: '隧道口 · 高陡斜坡',
        description: '应用毫米级高精度 LiDAR 三维激光扫描技术，针对多个高陡斜坡进行非接触式数字化岩体结构面解译与产状发育分析。',
        images: ['cz-tunnel-3d.png', 'cz-slope-segment.png'],
        imageFit: 'contain',
        imageFrameType: 'hud', // HUD style (black digital terminal theme) for point clouds/3D data
        tags: ['隧道口', '岩体结构', '三维激光扫描'],
        metadata: [
          { label: '地质强度指标 (GSI)', value: '65 - 75' },
          { label: '扫描精度等级', value: '毫米级 LiDAR' },
          { label: '解译结构面数', value: '45,210 个' }
        ]
      },
      {
        index: 'B',
        name: '成昆铁路',
        subtitle: '依卜特克斜坡',
        description: '基于依卜特克斜坡现场航拍影像，提取岩体裂隙几何参数并识别断层错动面，完成斜坡整体多场应力及滑动稳定性量化评估。',
        images: ['km-slope-aerial.png', 'km-rock-mass.png'],
        imageFit: 'contain',
        imageFrameType: 'paper', // Paper/photo style with copper crop marks for actual site photographs
        tags: ['稳定性量化', '结构面识别', '斜坡评估'],
        metadata: [
          { label: '抗剪强度参数', value: 'c=120kPa, φ=32°' },
          { label: '斜坡安全系数 (Fs)', value: '1.15 (欠稳定)' },
          { label: '主控结构面', value: '两组剪切共轭裂隙' }
        ]
      },
    ],
  },
  {
    id: 2,
    sectionLabel: '代表应用 二',
    sectionIndex: '02',
    title: '抚松县抚生村滑坡 · 大藤峡水电站',
    theme: '岩体结构对斜坡灾变演化的控制',
    layoutRatio: '60-40', // Asymmetric layout: 60% Left, 40% Right
    cases: [
      {
        index: 'A',
        name: '抚生村 7.29 滑坡',
        subtitle: '多种仪器联合监测',
        description: '针对吉林省抚松县抚生村滑坡灾害，建立“GNSS位移+气象降雨+钻孔倾角”多源联合应急监测体系，指导滑坡高风险区划分。',
        images: ['fusheng-aerial-map.png'],
        imageFit: 'cover',
        imageFrameType: 'paper',
        tags: ['GNSS位移', '气象监测', '应急预警'],
        metadata: [
          { label: '滑坡总体积', value: '约 120 万 m³' },
          { label: '监测站数量', value: '15 套 GNSS / 3 组雨量计' },
          { label: '突变预警阈值', value: '15 mm/d 变形速率' }
        ]
      },
      {
        index: 'B',
        name: '大藤峡水电站',
        subtitle: '岩体结构评价',
        description: '在广西大藤峡水电站枢纽闸基段，通过一比一百大型地质力学模型物理试验，揭示岩体顺层滑移破裂及坝基应力分布形态。',
        images: ['datengxia-dam.png', 'datengxia-model.jpg'],
        imageFit: 'cover',
        imageFrameType: 'hud',
        tags: ['顺层滑移', '三维力学模型', '抗滑稳定'],
        metadata: [
          { label: '坝基岩体极限承载力', value: '3.5 MPa' },
          { label: '物理模型相似比', value: '1:100 室内模型' },
          { label: '岩性地层特征', value: '泥质粉砂岩/泥页岩互层' }
        ]
      },
    ],
  },
  {
    id: 3,
    sectionLabel: '代表应用 三',
    sectionIndex: '03',
    title: '簇头沟泥石流 · 金沙江流域变形体',
    theme: '堆积体灾变演化理论',
    layoutRatio: '65-35', // Asymmetric layout: 65% Left, 35% Right
    cases: [
      {
        index: 'A',
        name: '簇头沟泥石流',
        subtitle: '碎屑流物源演化',
        description: '通过泥石流拦挡坝上下游高程及物源方量变动多期遥感解译对比，对多级拦挡阶梯工程阻滑、降能和控灾效应进行定量化剖析。',
        images: ['cutougou-flow-a.png', 'cutougou-flow-b.png'],
        imageFit: 'contain',
        imageFrameType: 'hud',
        tags: ['1#拦挡坝', '2#拦挡坝', '高程差异解译'],
        metadata: [
          { label: '泥石流最大流量', value: '450 m³/s' },
          { label: '防冲控制构筑物', value: '双级台阶阶梯阻滑拦挡坝' },
          { label: '堆积体变动幅度', value: '最大高程变动达 +4.5m' }
        ]
      },
      {
        index: 'B',
        name: '金沙江变形体',
        subtitle: '长期监测系统',
        description: '在金沙江上游白格滑坡及堆积体区域，基于多期孔隙水压及GNSS位移长期自动监测，建立堆积体渐进式滑动复活演化理论。',
        images: ['jinsha-landslide.png'],
        imageFit: 'contain',
        imageFrameType: 'paper',
        tags: ['白格滑坡', '堆积体复活', '长期监测'],
        metadata: [
          { label: '变形体区域面积', value: '约 2.4 km²' },
          { label: 'GNSS 位移累积', value: '水平 4.2m / 垂直 1.8m' },
          { label: '地下孔隙监测', value: '24 组多深度振弦式传感器' }
        ]
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
