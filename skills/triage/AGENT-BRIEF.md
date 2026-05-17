# 撰写智能体简报（Agent Brief）

智能体简报是工单迁至 `ready-for-agent` 时发布的结构化评论。它是 AFK 智能体将依之工作的权威规格；原工单正文与讨论是背景 —— **简报才是合约**。

## 原则

### 耐久重于精确

工单可能在 `ready-for-agent` 停留数日至数周，期间代码库会变。撰写的简报须在文件更名、迁移或重构后仍可读。

- **要做：** 描述接口、类型与行为契约
- **要做：** 点出智能体需查找或修改的具体类型名、函数签名、配置形状
- **不要做：** 引用文件路径 —— 会变旧
- **不要做：** 引用行号
- **不要做：** 假设当前实现结构会保持不变

### 描述行为而非步骤

说清楚系统 **应当如何表现**，不要说 **如何实现**。智能体会重新探索仓库并自定实现路径。

- **好：** 「`SkillConfig` 类型应接受可选字段 `schedule`，类型为 `CronExpression`」
- **差：** 「打开 src/types/skill.ts 在第 42 行加 schedule 字段」
- **好：** 「用户无参运行 **triage** 技能 时应看到需关注工单的摘要」
- **差：** 「在主处理函数里加 switch」

### 完整的验收标准

智能体须知道何时算完成。每份简报需有具体可测的验收项；每项应可独立核验。

- **好：** 「运行 `gh issue list --label needs-triage` 返回已通过初筛分类的工单」
- **差：** 「分拣应正常工作」

### 显式边界

声明不在范围内，避免智能体过度发挥或对相邻功能想当然。

## 模板

```markdown
## Agent Brief

**Category:** bug / enhancement
**Summary:** 一句话说明要完成什么

**Current behavior:**
描述现状。若是 bug，写坏掉的行为；若是 enhancement，写新特性所基于的现状。

**Desired behavior:**
描述智能体工作完成后应有的行为。
边界情况与错误路径要说清楚。

**Key interfaces:**
- `TypeName` —— 改动点与动机
- `functionName()` 返回类型 —— 现在返回什么 vs 期望返回什么
- 配置形状 —— 是否需要新选项

**Acceptance criteria:**
- [ ] 具体可测标准 1
- [ ] 具体可测标准 2
- [ ] 具体可测标准 3

**Out of scope:**
- 本工单不应触碰或解决的问题
- 看似相关但实际独立的相邻功能
```

## 示例

### 良好的智能体简报（bug）

```markdown
## Agent Brief

**Category:** bug
**Summary:** Skill 描述截断会在词中截断，导致破碎输出

**Current behavior:**
当 skill 描述超过 1024 字符，会在恰好 1024 处截断，无视词界。
生成的描述常以半个词收尾（例如 "Use when the user wants to confi"）。

**Desired behavior:**
应在 1024 前的最后一个词边界截断并追加 "..."。

**Key interfaces:**
- `SkillMetadata` 的 `description` —— 类型不必改，
  但写入描述的处理逻辑需遵循词边界
- 读取 SKILL.md frontmatter 并抽出 description 的函数

**Acceptance criteria:**
- [ ] 未满 1024 的描述保持不变
- [ ] 超限描述在 1024 前最后词边界截断
- [ ] 截断后以 "..." 结尾
- [ ] 包含 "..." 的总长不超过 1024

**Out of scope:**
- 修改 1024 上限本身
- 支持多行描述
```

### 良好的智能体简报（enhancement）

```markdown
## Agent Brief

**Category:** enhancement
**Summary:** 增加 `.out-of-scope/` 目录以跟踪被拒功能请求

**Current behavior:**
功能请求被拒时会打 `wontfix` 并评论结案；没有持久的决策记录。
下一次类似诉求时维护者得靠记忆或检索旧讨论。

**Desired behavior:**
被拒功能应记录在 `.out-of-scope/<concept>.md`，包含决策理由与所有相关请求的链接。
分拣新工单时应检索这些文件是否匹配。

**Key interfaces:**
- `.out-of-scope/` 下 Markdown：`# Concept Name`、`**Decision:**`、`**Reason:**`、`**Prior requests:**` 工单链接清单
- 分拣流程应尽早读完 `.out-of-scope/*.md`，按概念相似度匹配新工单

**Acceptance criteria:**
- [ ] 将以 wontfix 结案的功能写入/更新 `.out-of-scope/` 文件
- [ ] 文件包含决策、理由与指向结案工单的链接
- [ ] 若已有同名概念文件，新工单追加至「Prior requests」而非 duplicate
- [ ] 分拣时检索既有 `.out-of-scope/` ，匹配时在笔记中显式提出

**Out of scope:**
- 自动匹配（人工确认匹配）
- 重开曾经被拒功能
- bug 报告（仅 enhancement 被拒进入 `.out-of-scope/`）
```

### 糟糕的简报

```markdown
## Agent Brief

**Summary:** 修分拣 bug

**What to do:**
分拣坏了。去看主文件修一下，
大概 150 行附近的函数有问题。

**Files to change:**
- src/triage/handler.ts (line 150)
- src/types.ts (line 42)
```

糟糕原因：

- 无类目
- 描述含糊（「分拣坏了」）
- 指向会变旧的路径与行号
- 无验收标准
- 无范围边界
- 未交代当前 vs 期望行为
