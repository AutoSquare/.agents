---
trigger: glob
glob:
  - "**/*.cs"
  - "**/*.csproj"
  - "**/*.xaml"
---

## 9. C# 系列（含 WPF、WinUI3 等）开发规范

1. 所有开发中编写的 `public` 类、接口、结构体、枚举以及 `public` 方法、属性、事件必须添加完整的 XML 文档注释，以避免编译时产生 XML 注释警告（CS1591）。注释内容应遵循以下规范：
   - 使用标准的 XML 文档注释格式，以 `///` 开头
   - 必须包含 `<summary>` 标签，详细描述成员的功能、用途和工作原理
   - 对于方法，应根据需要添加 `<param>`、`<returns>`、`<exception>` 等标签
   - 注释语言应使用简洁准确的中文，避免模糊或冗余描述

   示例：

   ```csharp
   /// <summary>
   /// 用户认证服务，负责处理用户登录、注销和权限验证功能。
   /// 适用于需要用户身份验证的场景，通过调用后端 API 验证用户凭据并维护会话状态。
   /// </summary>
   public class AuthenticationService
   {
       /// <summary>
       /// 用户登录方法
       /// </summary>
       /// <param name="username">用户名</param>
       /// <param name="password">密码</param>
       /// <returns>登录成功返回 true，否则返回 false</returns>
       /// <exception cref="ArgumentNullException">当 username 或 password 为 null 时抛出</exception>
       public bool Login(string username, string password)
       {
           // 实现代码
       }
   }
   ```

2. 代码格式应保持整洁，移除所有不必要的空行。具体规范包括：
   - 类、方法、属性等成员之间只保留一个空行
   - 代码块内部逻辑分组之间可保留一个空行
   - 避免连续多个空行
   - 避免行首、行尾的空白字符
   - 保持一致的缩进风格
