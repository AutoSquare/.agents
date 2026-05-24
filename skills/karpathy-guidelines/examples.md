# 示例

展示四原则的真实代码示例。每个示例说明 LLM 常见的错误做法及正确修复方式。

---

## 1. 编码前思考

### 示例 1：隐藏的假设

**用户请求：** "Add a feature to export user data"

**❌ LLM 常见错误（错误假设）**

```python
def export_users(format='json'):
    """Export all users to a file."""
    users = User.query.all()
    
    if format == 'json':
        with open('users.json', 'w') as f:
            json.dump([u.to_dict() for u in users], f)
    elif format == 'csv':
        with open('users.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'name'])
            writer.writeheader()
            writer.writerows([u.to_dict() for u in users])
    
    return f"Exported {len(users)} users"
```

**问题：**
- 假设应导出全部用户（分页呢？隐私呢？）
- 未询问就假设了文件位置
- 假设了要包含哪些字段
- 未检查实际数据结构就假设了 CSV 字段名

**✅ 正确做法（显式说明假设）**

```
在实现之前，我需要确认：

1. **范围**：导出全部用户还是过滤后的子集？（隐私影响）
2. **格式**：你提到「导出」，是指：
   - 浏览器下载文件？
   - 后台任务并邮件通知？
   - 返回数据的 API 端点？
3. **字段**：包含哪些用户字段？（部分可能敏感）
4. **数据量**：通常有多少用户？（影响实现方式）

最简方案：添加返回分页 JSON 的 API 端点。
基于文件的导出需要更多信息。

你更倾向哪种？
```

### 示例 2：多种解释

**用户请求：** "Make the search faster"

**❌ LLM 常见错误（默默选择）**

```python
# Adds caching, database indexes, and async processing
# without asking which "faster" matters
@lru_cache(maxsize=1000)
async def search(query: str) -> List[Result]:
    # ... 200 lines of optimization code
```

**✅ 正确做法**

```
「让搜索更快」可能指：

1. **更快的响应时间**（从 500ms 降到 100ms 以下）
   - 添加数据库索引
   - 缓存高频查询
   - 预估工作量：2 小时

2. **处理更多并发搜索**（吞吐量）
   - 添加 async/await
   - 连接池
   - 预估工作量：4 小时

3. **更快的感知速度**（用户体验）
   - 立即显示部分结果
   - 渐进式加载
   - 预估工作量：3 小时

当前典型查询约 500ms。
对你的场景来说，哪方面最重要？
```

---

## 2. 简洁优先

### 示例 1：过度抽象

**用户请求：** "Add a function to calculate discount"

**❌ LLM 常见错误（过度工程）**

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, Union
from dataclasses import dataclass

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage
    
    def calculate(self, amount: float) -> float:
        return amount * (self.percentage / 100)

class FixedDiscount(DiscountStrategy):
    def __init__(self, fixed_amount: float):
        self.fixed_amount = fixed_amount
    
    def calculate(self, amount: float) -> float:
        return min(self.fixed_amount, amount)

@dataclass
class DiscountConfig:
    strategy: DiscountStrategy
    min_purchase: float = 0.0
    max_discount: float = float('inf')

class DiscountCalculator:
    def __init__(self, config: DiscountConfig):
        self.config = config
    
    def apply_discount(self, amount: float) -> float:
        if amount < self.config.min_purchase:
            return 0
        discount = self.config.strategy.calculate(amount)
        return min(discount, self.config.max_discount)

# Usage requires 30+ lines of setup for a simple calculation
```

**✅ 正确做法（简洁）**

```python
def calculate_discount(amount: float, percent: float) -> float:
    """Calculate discount amount. percent should be 0-100."""
    return amount * (percent / 100)

# Usage
discount = calculate_discount(100.0, 10.0)  # $10 off
```

**何时增加复杂度：** 仅当确实需要多种折扣类型时。若该需求后来才出现，届时再重构。

### 示例 2：推测性功能

**用户请求：** "Save user preferences to database"

**❌ LLM 常见错误（多余功能）**

```python
class PreferenceManager:
    def __init__(self, db, cache=None, validator=None):
        self.db = db
        self.cache = cache or InMemoryCache()
        self.validator = validator or DefaultValidator()
    
    def save(self, user_id: int, prefs: dict, 
             merge: bool = True, 
             validate: bool = True,
             notify: bool = False) -> bool:
        """Save preferences with optional merging, validation, and notifications."""
        
        if validate:
            errors = self.validator.validate(prefs)
            if errors:
                raise ValidationError(errors)
        
        existing = self.get(user_id) if merge else {}
        
        if merge:
            existing.update(prefs)
            prefs = existing
        
        self.db.execute(
            "UPDATE users SET preferences = ? WHERE id = ?",
            (json.dumps(prefs), user_id)
        )
        
        if self.cache:
            self.cache.set(f"prefs:{user_id}", prefs)
        
        if notify:
            self.notify_preference_change(user_id, prefs)
        
        return True
    
    def notify_preference_change(self, user_id: int, prefs: dict):
        # Another 30 lines for a feature nobody asked for
        pass
```

**✅ 正确做法（只做被要求的事）**

```python
def save_preferences(db, user_id: int, preferences: dict):
    """Save user preferences to database."""
    db.execute(
        "UPDATE users SET preferences = ? WHERE id = ?",
        (json.dumps(preferences), user_id)
    )
```

**需要时再添加：** 缓存（性能成为问题时）、校验（出现脏数据时）、合并（需求明确时）。

---

## 3. 精准修改

### 示例 1：顺手重构

**用户请求：** "Fix the bug where empty emails crash the validator"

**❌ LLM 常见错误（改动过多）**

```diff
  def validate_user(user_data):
-     # Check email format
-     if not user_data.get('email'):
+     """Validate user data."""
+     email = user_data.get('email', '').strip()
+     
+     # Validate email
+     if not email:
          raise ValueError("Email required")
-     
-     # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email or '.' not in email.split('@')[1]:
          raise ValueError("Invalid email")
      
-     # Check username
-     if not user_data.get('username'):
+     # Validate username
+     username = user_data.get('username', '').strip()
+     if not username:
          raise ValueError("Username required")
+     if len(username) < 3:
+         raise ValueError("Username too short")
+     if not username.isalnum():
+         raise ValueError("Username must be alphanumeric")
      
      return True
```

**问题：**
- 「改进」了超出 bug 修复范围的邮箱校验
- 添加了未要求的用户名校验
- 修改了注释
- 添加了 docstring

**✅ 正确做法（精准修改）**

```diff
  def validate_user(user_data):
      # Check email format
-     if not user_data.get('email'):
+     email = user_data.get('email', '')
+     if not email or not email.strip():
          raise ValueError("Email required")
      
      # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email:
          raise ValueError("Invalid email")
      
      # Check username
      if not user_data.get('username'):
          raise ValueError("Username required")
      
      return True
```

**仅修改：** 修复空邮箱处理的具体行。

### 示例 2：风格漂移

**用户请求：** "Add logging to the upload function"

**❌ LLM 常见错误（重格式化一切）**

```diff
- def upload_file(file_path, destination):
+ def upload_file(file_path: str, destination: str) -> bool:
+     """Upload file to destination with logging."""
+     logger.info(f"Uploading {file_path} to {destination}")
+     
      try:
-         with open(file_path, 'rb') as f:
-             data = f.read()
-         
-         response = requests.post(destination, files={'file': data})
-         
-         if response.status_code == 200:
-             return True
-         else:
-             return False
+         with open(file_path, "rb") as f:
+             data = f.read()
+         response = requests.post(destination, files={"file": data})
+         success = response.status_code == 200
+         
+         if success:
+             logger.info(f"Upload successful: {file_path}")
+         else:
+             logger.error(f"Upload failed: {file_path}, status={response.status_code}")
+         
+         return success
      except Exception as e:
-         print(f"Error: {e}")
+         logger.exception(f"Upload error for {file_path}: {e}")
          return False
```

**问题：**
- 修改了引号风格（'' 改为 ""）
- 添加了未要求的类型注解
- 添加了 docstring
- 重新格式化了空白
- 修改了布尔返回逻辑

**✅ 正确做法（匹配现有风格）**

```diff
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
  def upload_file(file_path, destination):
+     logger.info(f'Starting upload: {file_path}')
      try:
          with open(file_path, 'rb') as f:
              data = f.read()
          
          response = requests.post(destination, files={'file': data})
          
          if response.status_code == 200:
+             logger.info(f'Upload successful: {file_path}')
              return True
          else:
+             logger.error(f'Upload failed: {file_path}, status={response.status_code}')
              return False
      except Exception as e:
-         print(f"Error: {e}")
+         logger.exception(f'Upload error: {file_path}')
          return False
```

**保持一致：** 单引号、无类型注解、原有布尔模式、间距风格。

---

## 4. 目标驱动执行

### 示例 1：模糊 vs 可验证

**用户请求：** "Fix the authentication system"

**❌ LLM 常见错误（模糊做法）**

```
我会通过以下步骤修复认证系统：
1. 审查代码
2. 识别问题
3. 做改进
4. 测试改动

[在没有明确成功标准的情况下继续修改]
```

**✅ 正确做法（可验证目标）**

```
要「修复认证」，需要先定义成功标准。
具体要解决什么问题？

若问题是「用户改密码后仍保持登录」：

计划：
1. 编写测试：改密码 → 验证旧 session 失效
   验证：测试失败（重现 bug）

2. 实现：改密码时使 session 失效
   验证：测试通过

3. 检查边界：多 session 并存、并发修改
   验证：额外测试通过

4. 确认无回归：现有认证测试仍通过
   验证：完整测试套件全绿

当前认证测试覆盖：[展示覆盖情况]
你遇到的具体认证问题是什么？
```

### 示例 2：多步骤与验证

**用户请求：** "Add rate limiting to the API"

**❌ LLM 常见错误（一次性全做）**

```python
# Implements full rate limiting with Redis, multiple strategies,
# configuration system, and monitoring in one 300-line commit
# No clear verification steps
```

**✅ 正确做法（分步增量并验证）**

```
限流实施计划：

1. 添加基础内存限流（单端点）
   验证：
   - 测试：100 次请求 → 前 10 次成功，其余返回 429
   - 手动：curl 端点 11 次，看到限流错误

2. 提取为中间件（应用到所有端点）
   验证：
   - 测试：/users 和 /posts 均有限流
   - 现有端点测试仍通过

3. 添加 Redis 后端（多服务器场景）
   验证：
   - 测试：限流在应用重启后仍有效
   - 测试：两个应用实例共享限流计数

4. 添加配置（各端点不同速率）
   验证：
   - 测试：/search 10/分钟，/users 100/分钟
   - 配置文件解析正确

每步可独立验证和部署。
从第 1 步开始？
```

### 示例 3：测试先行验证

**用户请求：** "The sorting breaks when there are duplicate scores"

**❌ LLM 常见错误（未重现就修复）**

```python
# Immediately changes sort logic without confirming the bug
def sort_scores(scores):
    return sorted(scores, key=lambda x: (-x['score'], x['name']))
```

**✅ 正确做法（先重现）**

```python
# 1. First, write a test that reproduces the issue
def test_sort_with_duplicate_scores():
    """Test sorting when multiple items have same score."""
    scores = [
        {'name': 'Alice', 'score': 100},
        {'name': 'Bob', 'score': 100},
        {'name': 'Charlie', 'score': 90},
    ]
    
    result = sort_scores(scores)
    
    # The bug: order is non-deterministic for duplicates
    # Run this test multiple times, it should be consistent
    assert result[0]['score'] == 100
    assert result[1]['score'] == 100
    assert result[2]['score'] == 90

# Verify: Run test 10 times → fails with inconsistent ordering

# 2. Now fix with stable sort
def sort_scores(scores):
    """Sort by score descending, then name ascending for ties."""
    return sorted(scores, key=lambda x: (-x['score'], x['name']))

# Verify: Test passes consistently
```

---

## 反模式汇总

| 原则 | 反模式 | 修正 |
|-----------|-------------|-----|
| 编码前思考 | 默默假设文件格式、字段、范围 | 显式列出假设，请求澄清 |
| 简洁优先 | 单次折扣计算使用策略模式 | 实际需要复杂度之前用一个函数 |
| 精准修改 | 修 bug 时重格式化引号、加类型注解 | 只改修复所报告问题的行 |
| 目标驱动 | 「我会审查并改进代码」 | 「为 bug X 写测试 → 让它通过 → 验证无回归」 |

## 核心洞察

「过度复杂」的示例并非明显错误——它们遵循设计模式和最佳实践。问题在于**时机**：在需要之前就增加了复杂度，导致：

- 代码更难理解
- 引入更多 bug
- 实现耗时更长
- 更难测试

「简洁」版本则：
- 更易理解
- 实现更快
- 更易测试
- 实际需要时再做重构

**好代码是简洁解决今天的问题，而不是过早解决明天的问题。**
