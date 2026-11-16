# Skills 自动生成规范

## 触发条件

创建、修改、迁移或安装 Agent Skills 时读取。

## 可迁移性

- Skills 目录必须包含全部可执行代码，不得依赖项目外部私有模块或宿主项目中的非标准库。
- 脱离当前项目后应可直接复制至其他项目独立运行。
- 不得硬编码项目路径、环境变量或宿主项目专属依赖；技能内脚本与资源用相对技能目录的路径。

## 文档

- 必须附带完整文档：模块职责、函数签名与调用方式、参数与返回值、Agent 调用示例与操作说明。
- 任何 Agent 应能在不读源码的情况下正确调用全部功能。

## 工程结构

- 目录与模块划分遵循对应语言主流规范（如 Python `src/` layout、TypeScript 分层 `src/`）。
- 禁止扁平堆砌或随意命名。

## ZCode 发现与 frontmatter

ZCode 从文件系统按发现顺序扫描技能；frontmatter 是 `---` 包裹的扁平 `key: value` 块：

- `name` 与 `description` 必填；缺任一项（或 `description` 超过 1024 字符）技能会被丢弃。
- 触发语与能力说明应落在 `description` 前 250 字符内（模型目录只展示前 250 字符）；可选 `when_to_use` 说明触发时机。
- 目录结构为 `<skill>/SKILL.md`；以 `.` 开头的目录（除 `.system`）与 `node_modules` 会被跳过。
- `disable-model-invocation` 是 DSH 专属键，ZCode 不识别；ZCode 中带 description 的技能既可被模型按需调用，也可由用户 `/name` 显式调用。
- 发现顺序（前者优先、同名遮蔽后者）：显式配置根 → `~/.zcode/skills/` → `~/.agents/skills/` → 工作区 `.zcode/skills/` → 工作区 `.agents/skills/` → 插件。**用户级副本会遮蔽项目内 `.agents/skills/`**；更新技能源后需重跑 `setup-zcode-agents.ps1` 同步用户级副本。
- ZCode 用户级安装根为 `~/.zcode/skills/`（默认 `%USERPROFILE%\.zcode\skills\`）。
