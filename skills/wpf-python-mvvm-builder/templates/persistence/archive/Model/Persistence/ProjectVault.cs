using System.IO;
using System.IO.Compression;
using System.Text;
using System.Text.Json;
using {{RootNamespace}}.Model.Domain;

namespace {{RootNamespace}}.Model.Persistence;

/// <summary>
/// 工程 ZIP 包的保存与加载（archive 模式）。
/// </summary>
public static class ProjectVault
{
    /// <summary>
    /// 从磁盘加载工程文档。
    /// </summary>
    /// <param name="filePath">工程文件路径。</param>
    /// <returns>加载后的文档。</returns>
    public static async Task<ProjectDocument> LoadAsync(string filePath)
    {
        var doc = new ProjectDocument();
        await using var fs = File.OpenRead(filePath);
        using var archive = new ZipArchive(fs, ZipArchiveMode.Read);
        foreach (var entry in archive.Entries)
        {
            if (entry.FullName.EndsWith('/'))
                continue;
            await using var es = entry.Open();
            using var reader = new StreamReader(es, Encoding.UTF8);
            var text = await reader.ReadToEndAsync().ConfigureAwait(false);
            if (entry.FullName == ProjectFileFormat.ManifestFileName)
            {
                using var manifest = JsonDocument.Parse(text);
                if (manifest.RootElement.TryGetProperty("displayName", out var dn))
                    doc.DisplayName = dn.GetString() ?? doc.DisplayName;
                continue;
            }
            var parts = entry.FullName.Replace('\\', '/').Split('/', 2);
            if (parts.Length != 2)
                continue;
            var tableName = Path.GetFileNameWithoutExtension(parts[1]);
            if (parts[0] == ProjectFileFormat.DataFolder)
                doc.DataTables[tableName] = text;
            else if (parts[0] == ProjectFileFormat.MaterialFolder)
                doc.MaterialTables[tableName] = text;
        }
        return doc;
    }

    /// <summary>
    /// 将工程文档保存到磁盘。
    /// </summary>
    /// <param name="doc">工程文档。</param>
    /// <param name="filePath">目标路径。</param>
    public static async Task SaveAsync(ProjectDocument doc, string filePath)
    {
        if (File.Exists(filePath))
            File.Delete(filePath);
        await using var fs = File.Create(filePath);
        using var archive = new ZipArchive(fs, ZipArchiveMode.Create);
        var manifest = JsonSerializer.Serialize(new
        {
            formatVersion = 1,
            appId = "{{RootNamespace}}",
            displayName = doc.DisplayName,
            createdUtc = DateTime.UtcNow,
        });
        WriteEntry(archive, ProjectFileFormat.ManifestFileName, manifest);
        foreach (var pair in doc.DataTables)
            WriteEntry(archive, $"{ProjectFileFormat.DataFolder}/{pair.Key}.json", pair.Value);
        foreach (var pair in doc.MaterialTables)
            WriteEntry(archive, $"{ProjectFileFormat.MaterialFolder}/{pair.Key}.json", pair.Value);
    }

    private static void WriteEntry(ZipArchive archive, string name, string content)
    {
        var entry = archive.CreateEntry(name, CompressionLevel.Optimal);
        using var writer = new StreamWriter(entry.Open(), new UTF8Encoding(false));
        writer.Write(content);
    }
}
