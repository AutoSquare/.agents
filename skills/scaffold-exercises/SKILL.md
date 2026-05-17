---
name: scaffold-exercises
description: 生成通过 lint 的练习目录结构：含章节、题目、参考答案与讲解。用于搭建练习骨架、习题桩或新课程章节。
---

# Scaffold Exercises（练习脚手架）

创建能通过 `pnpm ai-hero-cli internal lint` 的练习目录结构，再以 `git commit` 提交。

## 命名

- **章节**：`exercises/` 下 `XX-section-name/`（例：`01-retrieval-skill-building`）
- **练习**：章节内 `XX.YY-exercise-name/`（例：`01.03-retrieval-with-bm25`）
- 章节号 = `XX`，练习号 = `XX.YY`
- 名称 dash-case（小写 + 连字符）

## 练习变体

每个练习至少需要下列子目录之一：

- `problem/` —— 学员工作区含 TODO
- `solution/` —— 参考答案实现
- `explainer/` —— 概念材料，无 TODO

打桩时除非计划另有指定，默认 `explainer/`。

## 必选文件

每个子目录（`problem/`、`solution/`、`explainer/`）须有 `readme.md`：

- **非空**（哪怕只是一行标题）
- 无死链

打桩时用最小 readme：标题 + 一句描述：

```md
# Exercise Title

Description here
```

若子目录含代码，还需 `main.ts`（多于一行）。纯 readme 桩可只有 readme。

## 工作流

1. **解析计划** —— 抽出章节名、练习名、变体类型
2. **创建目录** —— 对每个路径 `mkdir -p`
3. **写桩 readme** —— 每个变体目录一份带标题的 `readme.md`
4. **跑 lint** —— `pnpm ai-hero-cli internal lint`
5. **修到绿** —— 迭代直至通过

## Lint 概要

（`pnpm ai-hero-cli internal lint`）

- 每练习须有子目录（`problem/`、`solution/`、`explainer/`）
- `problem/`、`explainer/`、`explainer.1/` 至少其一存在
- 主子里 `readme.md` 存在且非空
- 无 `.gitkeep`
- 无 `speaker-notes.md`
- readme 无死链
- readme 无 `pnpm run exercise` 指令
- 除纯 readme-only 外每子目录要 `main.ts`

## 移动 / 重命名

重排练习时：

1. 用 `git mv`（不用裸 `mv`）—— 保留历史
2. 更新数字前缀维持顺序
3. 移动后重跑 lint

示例：

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## 示例：按计划打桩

计划如：

```
Section 05: Memory Skill Building
- 05.01 Introduction to Memory
- 05.02 Short-term Memory (explainer + problem + solution)
- 05.03 Long-term Memory
```

创建：

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

写 readme 桩：

```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# Introduction to Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# Long-term Memory"
```
