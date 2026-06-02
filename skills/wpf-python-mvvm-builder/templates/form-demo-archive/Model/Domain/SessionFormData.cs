using System.Text.Json;
using System.Text.Json.Serialization;

namespace {{RootNamespace}}.Model.Domain;

/// <summary>
/// 测试表单字段，序列化至 dataTables「测试表单」以验证 archive 工程包 round-trip。
/// </summary>
public sealed class SessionFormData
{
    /// <summary>数据表名。</summary>
    public const string TableName = "测试表单";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.Never,
    };

    /// <summary>项目名称。</summary>
    public string ProjectName { get; set; } = string.Empty;

    /// <summary>负责人。</summary>
    public string OwnerName { get; set; } = string.Empty;

    /// <summary>备注。</summary>
    public string Memo { get; set; } = string.Empty;

    /// <summary>联系电话。</summary>
    public string ContactPhone { get; set; } = string.Empty;

    /// <summary>所属部门。</summary>
    public string Department { get; set; } = string.Empty;

    /// <summary>工程地点。</summary>
    public string SiteAddress { get; set; } = string.Empty;

    /// <summary>
    /// 从工程文档读取测试表单；缺失或解析失败时返回空表单。
    /// </summary>
    /// <param name="document">工程文档。</param>
    /// <returns>表单数据。</returns>
    public static SessionFormData FromDocument(ProjectDocument document)
    {
        if (!document.DataTables.TryGetValue(TableName, out var json) || string.IsNullOrWhiteSpace(json))
            return new SessionFormData();
        try
        {
            return JsonSerializer.Deserialize<SessionFormData>(json, JsonOptions) ?? new SessionFormData();
        }
        catch (JsonException)
        {
            return new SessionFormData();
        }
    }

    /// <summary>
    /// 将当前表单写入工程文档 dataTables。
    /// </summary>
    /// <param name="document">工程文档。</param>
    public void ApplyToDocument(ProjectDocument document)
    {
        document.DataTables[TableName] = JsonSerializer.Serialize(this, JsonOptions);
    }

    /// <summary>
    /// 创建默认空表单 JSON，供新工程种子使用。
    /// </summary>
    /// <returns>JSON 文本。</returns>
    public static string CreateDefaultJson() =>
        JsonSerializer.Serialize(new SessionFormData(), JsonOptions);
}
