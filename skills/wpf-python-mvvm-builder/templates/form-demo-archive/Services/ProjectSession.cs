using System.IO;
using System.Text;
using {{RootNamespace}}.Model.Domain;

namespace {{RootNamespace}}.Services;

/// <summary>
/// 当前工程会话（archive + form-demo）：基线含测试表单表。
/// </summary>
public sealed class ProjectSession
{
    private string? _workspaceDirectory;
    private static bool _initialized;

    /// <summary>当前活动会话单例。</summary>
    public static ProjectSession Live { get; } = new();

    /// <summary>内存中的工程文档。</summary>
    public ProjectDocument Document { get; private set; } = new();

    /// <summary>是否已修改。</summary>
    public bool IsDirty { get; private set; }

    /// <summary>
    /// 确保会话已从基线或最近工程初始化。
    /// </summary>
    public void EnsureInitialized()
    {
        if (_initialized)
            return;
        _initialized = true;
        Document = CreateFromBaseline();
    }

    /// <summary>从基线 JSON 创建新文档。</summary>
    /// <returns>含种子表与测试表单的文档。</returns>
    public static ProjectDocument CreateFromBaseline()
    {
        var doc = new ProjectDocument();
        var root = AppPaths.Root;
        CopyBaselineTable(doc, root, ProjectFileFormat.DataFolder, "项目基本信息", isMaterial: false);
        CopyBaselineTable(doc, root, ProjectFileFormat.MaterialFolder, "示例材料", isMaterial: true);
        doc.DataTables[SessionFormData.TableName] = SessionFormData.CreateDefaultJson();
        return doc;
    }

    /// <summary>标记文档已修改。</summary>
    public void MarkDirty() => IsDirty = true;

    /// <summary>清除脏标记。</summary>
    public void ClearDirty() => IsDirty = false;

    /// <summary>构建 UI 状态（archive 模式不使用，供 MainWindow 统一调用）。</summary>
    /// <param name="statusText">状态栏文本。</param>
    /// <returns>空字典。</returns>
    public static IReadOnlyDictionary<string, object?> BuildUiState(string statusText) =>
        new Dictionary<string, object?>();

    /// <summary>
    /// 退出时若已脏且已有路径则自动保存。
    /// </summary>
    /// <param name="uiState">忽略；memory 模式专用。</param>
    public async Task PersistOnExitAsync(IReadOnlyDictionary<string, object?>? uiState = null)
    {
        EnsureInitialized();
        if (!IsDirty)
            return;
        var fileService = CompositionRoot.ProjectFileService;
        if (string.IsNullOrWhiteSpace(fileService.CurrentPath))
            return;
        await fileService.SaveAsync().ConfigureAwait(false);
    }

    /// <summary>同步包装：退出时脏保存。</summary>
    /// <param name="uiState">忽略；memory 模式专用。</param>
    public void PersistOnExit(IReadOnlyDictionary<string, object?>? uiState = null)
    {
        PersistOnExitAsync(uiState).GetAwaiter().GetResult();
    }

    /// <summary>导出 Python 工作区目录。</summary>
    /// <returns>工作区根目录绝对路径。</returns>
    public string ExportWorkspaceForPython()
    {
        EnsureInitialized();
        if (string.IsNullOrEmpty(_workspaceDirectory))
        {
            _workspaceDirectory = Path.Combine(
                Path.GetTempPath(),
                AppPaths.WorkspacePrefix + Guid.NewGuid().ToString("N"));
        }
        WriteTablesToWorkspace(_workspaceDirectory);
        return _workspaceDirectory;
    }

    /// <summary>从 Python 工作区合并表回内存文档。</summary>
    /// <param name="workspaceRoot">工作区根目录。</param>
    public void MergeTablesFromWorkspaceDirectory(string workspaceRoot)
    {
        EnsureInitialized();
        MergeFolder(workspaceRoot, ProjectFileFormat.DataFolder, Document.DataTables);
        MergeFolder(workspaceRoot, ProjectFileFormat.MaterialFolder, Document.MaterialTables);
        IsDirty = true;
    }

    /// <summary>用已加载文档替换当前会话。</summary>
    /// <param name="document">工程文档。</param>
    public void ReplaceDocument(ProjectDocument document)
    {
        Document = document;
        _initialized = true;
        IsDirty = false;
    }

    /// <summary>清理当前 Python 工作区目录。</summary>
    public void CleanupPythonWorkspaceDirectory()
    {
        if (string.IsNullOrEmpty(_workspaceDirectory))
            return;
        try
        {
            if (Directory.Exists(_workspaceDirectory))
                Directory.Delete(_workspaceDirectory, recursive: true);
        }
        catch (IOException)
        {
        }
        catch (UnauthorizedAccessException)
        {
        }
        _workspaceDirectory = null;
    }

    private static void CopyBaselineTable(ProjectDocument doc, string appRoot, string folder, string tableName, bool isMaterial)
    {
        var path = Path.Combine(appRoot, "Assets", "Baseline", folder, tableName + ".json");
        if (!File.Exists(path))
            return;
        var text = File.ReadAllText(path, Encoding.UTF8);
        if (isMaterial)
            doc.MaterialTables[tableName] = text;
        else
            doc.DataTables[tableName] = text;
    }

    private void WriteTablesToWorkspace(string workspaceRoot)
    {
        WriteFolder(workspaceRoot, ProjectFileFormat.DataFolder, Document.DataTables);
        WriteFolder(workspaceRoot, ProjectFileFormat.MaterialFolder, Document.MaterialTables);
    }

    private static void WriteFolder(string workspaceRoot, string folderName, Dictionary<string, string> tables)
    {
        var dir = Path.Combine(workspaceRoot, folderName);
        Directory.CreateDirectory(dir);
        foreach (var pair in tables)
        {
            var path = Path.Combine(dir, pair.Key + ".json");
            File.WriteAllText(path, pair.Value, new UTF8Encoding(false));
        }
    }

    private static void MergeFolder(string workspaceRoot, string folderName, Dictionary<string, string> target)
    {
        var dir = Path.Combine(workspaceRoot, folderName);
        if (!Directory.Exists(dir))
            return;
        foreach (var file in Directory.GetFiles(dir, "*.json"))
        {
            var tableName = Path.GetFileNameWithoutExtension(file);
            target[tableName] = File.ReadAllText(file, Encoding.UTF8);
        }
    }
}
