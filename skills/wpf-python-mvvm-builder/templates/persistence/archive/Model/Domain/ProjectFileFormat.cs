namespace {{RootNamespace}}.Model.Domain;

/// <summary>
/// 工程包逻辑表名与归档扩展名常量（archive 模式）。
/// </summary>
public static class ProjectFileFormat
{
    /// <summary>持久化路线标识。</summary>
    public const string PersistenceMode = "archive";

    /// <summary>工程文件扩展名（含点）。</summary>
    public const string Extension = "{{Ext}}";

    /// <summary>数据表目录名。</summary>
    public const string DataFolder = "数据表";

    /// <summary>材料库目录名。</summary>
    public const string MaterialFolder = "材料库";

    /// <summary>manifest 文件名。</summary>
    public const string ManifestFileName = "manifest.json";

    /// <summary>样本结果表名。</summary>
    public const string SampleResultTable = "样本计算结果";
}
