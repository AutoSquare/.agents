# csproj 接线

## NuGet（脚手架追加）

```xml
<!-- dual-stack: packages -->
<ItemGroup>
  <PackageReference Include="CommunityToolkit.Mvvm" Version="8.4.0" />
  <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="9.0.0" />
</ItemGroup>
```

版本可在 Skill 迭代时 bump；须与 TargetFramework 兼容。

## CopyToOutputDirectory

```xml
<!-- dual-stack: {Abbr}Py -->
<ItemGroup>
  <None Update="{Abbr}Py/**/*.py">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </None>
</ItemGroup>
<!-- dual-stack: {Abbr}Env -->
<ItemGroup>
  <Content Include="{Abbr}Env/**/*" Condition="Exists('{Abbr}Env')">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </Content>
</ItemGroup>
<!-- dual-stack: baseline -->
<ItemGroup>
  <Content Include="Assets/Baseline/**/*.json">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </Content>
</ItemGroup>
```

## XML 文档（可选）

GeoPile 启用 `GenerateDocumentationFile`；母版默认**不强制**，避免空项目 CS1591。用户要求时可 intake 开启。

## 增量原则

- 脚本只 **追加** 带锚点注释的 ItemGroup
- 已存在锚点则跳过（幂等）
- `--dry-run` 只打印将写入的片段
