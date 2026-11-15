---
trigger: model_decision
description: 创建、修改或审查 Agent Skills（skills 目录、SKILL.md、技能文档）时读取。
---

## 8. Skills 自动生成规范

- Skills 目录必须包含全部可执行代码，不得依赖项目外部私有模块或宿主项目中的非标准库。Skills 必须具备可迁移性，即脱离当前项目后可直接复制至其他项目独立运行，不得包含硬编码的项目路径、环境变量或宿主项目专属依赖。
- Skills 必须附带完整文档，文档内容须涵盖：全部代码模块的职责说明、各函数的签名与调用方式、参数说明与返回值定义、Agent 调用本 Skills 的示例与操作说明。文档应使任何 Agent 无需阅读源码即可正确调用 Skills 的全部功能。
- Skills 的代码文件与目录组织必须遵循对应语言的主流工程规范（如 Python 采用 src/layout 或 flat layout、TypeScript 采用 src/ 分层结构等），禁止扁平堆砌或随意命名。目录层级、模块划分、命名风格均须符合该语言社区公认的最佳实践。
