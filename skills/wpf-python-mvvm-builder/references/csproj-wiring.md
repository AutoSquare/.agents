# csproj 接线

## NuGet

```xml
<!-- dual-stack: packages -->
<ItemGroup>
  <PackageReference Include="CommunityToolkit.Mvvm" Version="8.4.0" />
  <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="9.0.0" />
</ItemGroup>
```

## CopyToOutputDirectory

`{Abbr}Env/` 是可移植 Python 环境，会复制到输出目录和安装包。它不能是 venv；目录内不得存在 `pyvenv.cfg`。

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

## XML 文档

GeoPile 启用 `GenerateDocumentationFile`；模板默认不强制，避免空项目 CS1591。用户要求时可 intake 开启。

## 增量原则

- 脚本只追加带锚点注释的 ItemGroup。
- 已存在锚点则跳过，保持幂等。
- `--dry-run` 只打印将写入的片段。
