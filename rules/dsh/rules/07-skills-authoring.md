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

## DSH 发现与 frontmatter

DeepSeek Harness 从文件系统按目录一层发现技能；不满足下列条件会被**静默丢弃**（只写日志）：

- `name` 必填且匹配 `^[a-z0-9]+(?:-[a-z0-9]+)*$`，建议与技能目录同名。
- `description` 必填；DSH 目录只展示规范化后的前 500 字符，触发语与能力说明应落在前 500 字符内。
- 可选 `disable-model-invocation: true` 与 `user-invocable: false`；不要使用 `disableModelInvocation` 等旧键。
- 目录结构为 `<skill>/SKILL.md`；不识别嵌套技能树与扁平 `<name>.md` 之外的其它布局。
- DSH 安装根为 `$DSH_HOME/skills/`（默认 `~/.dsh/skills/`）；项目内 `.agents/skills/` 与 `.dsh/skills/` 优先于用户级。