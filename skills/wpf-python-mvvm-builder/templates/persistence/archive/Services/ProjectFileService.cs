using System.IO;
using {{RootNamespace}}.Model.Domain;
using {{RootNamespace}}.Model.Persistence;

namespace {{RootNamespace}}.Services;

/// <summary>
/// archive 模式工程文件打开、保存与最近路径记忆。
/// </summary>
public sealed class ProjectFileService
{
    /// <summary>当前工程文件路径；未保存过则为 null。</summary>
    public string? CurrentPath { get; private set; }

    /// <summary>
    /// 从磁盘打开工程包。
    /// </summary>
    /// <param name="filePath">工程文件路径。</param>
    /// <returns>加载后的文档。</returns>
    public async Task<ProjectDocument> OpenAsync(string filePath)
    {
        var doc = await ProjectVault.LoadAsync(filePath).ConfigureAwait(false);
        CurrentPath = filePath;
        ProjectSession.Live.ReplaceDocument(doc);
        UserSettingsStore.SaveLastProjectPath(filePath);
        return doc;
    }

    /// <summary>
    /// 保存到当前路径；若无路径则返回 false。
    /// </summary>
    /// <returns>成功返回 true。</returns>
    public async Task<bool> SaveAsync()
    {
        if (string.IsNullOrWhiteSpace(CurrentPath))
            return false;
        await ProjectVault.SaveAsync(ProjectSession.Live.Document, CurrentPath).ConfigureAwait(false);
        ProjectSession.Live.ClearDirty();
        UserSettingsStore.SaveLastProjectPath(CurrentPath);
        return true;
    }

    /// <summary>
    /// 另存为并更新当前路径。
    /// </summary>
    /// <param name="filePath">目标路径。</param>
    public async Task SaveAsAsync(string filePath)
    {
        await ProjectVault.SaveAsync(ProjectSession.Live.Document, filePath).ConfigureAwait(false);
        CurrentPath = filePath;
        ProjectSession.Live.ClearDirty();
        UserSettingsStore.SaveLastProjectPath(filePath);
    }

    /// <summary>
    /// 尝试打开上次工程路径。
    /// </summary>
    /// <returns>成功返回 true。</returns>
    public async Task<bool> TryOpenLastProjectAsync()
    {
        var path = UserSettingsStore.LoadLastProjectPath();
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            return false;
        await OpenAsync(path).ConfigureAwait(false);
        return true;
    }
}
