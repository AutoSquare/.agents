---
name: setup-pre-commit
description: 在当前仓库配置 Husky 预提交：lint-staged（Prettier）、类型检查与测试。用于添加 pre-commit、搭建 Husky、配置 lint-staged，或在提交时做格式化 / 类型检查 / 测试。
---

# Setup Pre-Commit Hooks（预提交钩子）

## 将安装什么

- **Husky** pre-commit 钩子
- **lint-staged** 对已暂存文件跑 Prettier
- **Prettier** 配置（若缺失）
- pre-commit 中串联 **typecheck** 与 **test** 脚本

## 步骤

### 1. 检测包管理器

查找 `package-lock.json`（npm）、`pnpm-lock.yaml`（pnpm）、`yarn.lock`（yarn）、`bun.lockb`（bun）。不明确时默认 npm。

### 2. 安装依赖

作为 devDependencies：

```
husky lint-staged prettier
```

### 3. 初始化 Husky

```bash
npx husky init
```

会创建 `.husky/` 并在 package.json 加 `prepare: "husky"`。

### 4. 编写 `.husky/pre-commit`

（Husky v9+ 可不要 shebang）

```
npx lint-staged
npm run typecheck
npm run test
```

**适配：** 把 `npm` 换成检测到的管理器。若 package.json 无 `typecheck` 或 `test` 脚本，删掉对应行并告知用户。

### 5. 创建 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. 如无则创建 `.prettierrc`

仅当尚无 Prettier 配置。默认：

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. 验证

- [ ] `.husky/pre-commit` 存在且可执行
- [ ] `.lintstagedrc` 存在
- [ ] package.json `prepare` 为 `"husky"`
- [ ] Prettier 配置存在
- [ ] 运行 `npx lint-staged` 自检

### 8. 提交

暂存所有变更并以 `Add pre-commit hooks (husky + lint-staged + prettier)` 提交。

首次提交会触发新钩子 —— 正好烟雾测试。

## 备注

- Husky v9+ 钩子文件可不需要 shebang
- `prettier --ignore-unknown` 会跳过无法解析的文件（图片等）
- pre-commit 先跑 lint-staged（快、只碰暂存），再全量 typecheck 与测试
