using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using Microsoft.Win32;
using {{RootNamespace}}.Model.Domain;

namespace {{RootNamespace}}.Services;

/// <summary>
/// 工程文件扩展名关联（HKCU\Software\Classes，无需管理员）；双击 {Ext} 以命令行参数启动本程序。
/// </summary>
public static class FileAssociationUtilities
{
    private const string UserClassesRelativePath = @"Software\Classes";

    /// <summary>ProgId 根键，用于记录上次同步的图标哈希。</summary>
    private const string AssocStateRelativePath = @"Software\{{RootNamespace}}\ProjectFileAssoc";

    private const string AssocStateIconSha256Key = "ProjectFileIconSha256";

    /// <summary>注册表 ProgId。</summary>
    public static string ProgId => "{{RootNamespace}}.ProjectFile";

    /// <summary>资源管理器类型描述。</summary>
    public static string FileTypeDescription => "{{DisplayName}}工程文件";

    /// <summary>
    /// 启动时注册或刷新当前用户下的文件关联。
    /// </summary>
    public static void TryRegisterOnStartup()
    {
        try
        {
            Register(ResolveAssociationIconPath());
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"文件关联跳过: {ex.Message}");
        }
    }

    /// <summary>
    /// 解析用于 DefaultIcon 的磁盘路径；优先 project_file.ico，其次 exe 自身。
    /// </summary>
    /// <returns>绝对路径。</returns>
    public static string ResolveAssociationIconPath()
    {
        var baseDir = AppPaths.Root;
        var projectIco = Path.Combine(baseDir, "Resources", "icons", "project_file.ico");
        var projectPng = Path.Combine(baseDir, "Resources", "icons", "project_file.png");
        var candidate = File.Exists(projectIco)
            ? projectIco
            : File.Exists(projectPng) ? projectPng : Process.GetCurrentProcess().MainModule?.FileName ?? baseDir;
        return SafeGetFullPath(candidate);
    }

    /// <summary>
    /// 将扩展名与打开命令写入 HKCU；已一致则跳过。
    /// </summary>
    /// <param name="iconPath">DefaultIcon 指向的路径。</param>
    public static void Register(string iconPath)
    {
        var extension = ProjectFileFormat.Extension;
        if (!extension.StartsWith('.'))
            extension = "." + extension;

        var exeFromProcess = Process.GetCurrentProcess().MainModule?.FileName;
        if (string.IsNullOrEmpty(exeFromProcess))
            return;

        var normalizedExeFull = SafeGetFullPath(exeFromProcess);
        var resolvedIconFull = SafeGetFullPath(iconPath.Trim().Trim('"').Trim('\''));

        var exeMatch = ResolveRegisteredOpenCommandExePath();
        var iconPathMatch =
            NormalizeDefaultIconDiskPath(NormalizeDefaultIconRaw(TryReadRegisteredDefaultIconRaw()))
            == NormalizeDefaultIconDiskPath(resolvedIconFull);
        var contentMatch = PersistedIconContentMatchesDisk(resolvedIconFull);

        if (exeMatch is not null
            && string.Equals(exeMatch, normalizedExeFull, StringComparison.OrdinalIgnoreCase)
            && iconPathMatch
            && contentMatch)
        {
            return;
        }

        WriteAssociationRegistry(extension, resolvedIconFull, normalizedExeFull);
        WritePersistedIconContentHash(resolvedIconFull);
        SHChangeNotify(0x08000000, 0x0, IntPtr.Zero, IntPtr.Zero);
    }

    private static string? ResolveRegisteredOpenCommandExePath()
    {
        using var key = Registry.CurrentUser.OpenSubKey(
            $@"{UserClassesRelativePath}\{ProgId}\shell\open\command");
        var command = key?.GetValue(null) as string;
        var raw = ExtractCommandExePath(command);
        if (string.IsNullOrEmpty(raw))
            return null;
        try
        {
            return SafeGetFullPath(raw);
        }
        catch
        {
            return raw;
        }
    }

    private static string? TryReadRegisteredDefaultIconRaw()
    {
        using var key = Registry.CurrentUser.OpenSubKey($@"{UserClassesRelativePath}\{ProgId}\DefaultIcon");
        return key?.GetValue(null) as string;
    }

    private static string NormalizeDefaultIconRaw(string? raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
            return string.Empty;
        raw = raw.Trim();
        var lastComma = raw.LastIndexOf(',');
        if (lastComma > 0)
        {
            var tail = raw[(lastComma + 1)..].Trim();
            if (tail.Length != 0 && int.TryParse(tail, NumberStyles.Integer, CultureInfo.InvariantCulture, out _))
                return raw[..lastComma].Trim('"', '\'', ' ', '\t');
        }
        return raw.Trim('"', '\'', ' ', '\t');
    }

    private static string NormalizeDefaultIconDiskPath(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return string.Empty;
        try
        {
            return SafeGetFullPath(path);
        }
        catch
        {
            return path.TrimEnd('\\');
        }
    }

    private static string? ExtractCommandExePath(string? command)
    {
        if (string.IsNullOrEmpty(command))
            return null;
        var firstQuote = command.IndexOf('\"');
        if (firstQuote < 0)
            return null;
        var secondQuote = command.IndexOf('\"', firstQuote + 1);
        if (secondQuote < 0)
            return null;
        var innerPath = command.Substring(firstQuote + 1, secondQuote - firstQuote - 1).Trim();
        try
        {
            return SafeGetFullPath(innerPath);
        }
        catch
        {
            return innerPath.TrimEnd('\\');
        }
    }

    private static bool PersistedIconContentMatchesDisk(string resolvedIconFull)
    {
        var currentSha = Sha256HexForFileOrEmpty(resolvedIconFull);
        var storedSha = TryReadStoredIconSha256();
        return string.Equals(storedSha, currentSha, StringComparison.OrdinalIgnoreCase);
    }

    private static string Sha256HexForFileOrEmpty(string path)
    {
        if (!File.Exists(path))
            return string.Empty;
        try
        {
            using var stream = File.OpenRead(path);
            using var sha256 = SHA256.Create();
            return Convert.ToHexString(sha256.ComputeHash(stream));
        }
        catch
        {
            return string.Empty;
        }
    }

    private static string? TryReadStoredIconSha256()
    {
        using var state = Registry.CurrentUser.OpenSubKey(AssocStateRelativePath);
        return state?.GetValue(AssocStateIconSha256Key) as string;
    }

    private static void WritePersistedIconContentHash(string resolvedIconFull)
    {
        using var state = Registry.CurrentUser.CreateSubKey(AssocStateRelativePath)
            ?? throw new InvalidOperationException("无法写入关联状态键。");
        state.SetValue(AssocStateIconSha256Key, Sha256HexForFileOrEmpty(resolvedIconFull), RegistryValueKind.String);
    }

    private static string SafeGetFullPath(string path) =>
        Path.GetFullPath(Path.TrimEndingDirectorySeparator(path));

    private static string FormatDefaultIconRegistryValue(string resolvedIconFull)
    {
        var ext = Path.GetExtension(resolvedIconFull);
        if (string.Equals(ext, ".png", StringComparison.OrdinalIgnoreCase)
            || string.Equals(ext, ".ico", StringComparison.OrdinalIgnoreCase)
            || string.Equals(ext, ".bmp", StringComparison.OrdinalIgnoreCase))
            return $"{resolvedIconFull},0";
        return $"{resolvedIconFull},0";
    }

    private static void WriteAssociationRegistry(string extension, string resolvedIconFull, string normalizedExeFullPath)
    {
        using var classesRoot = Registry.CurrentUser.CreateSubKey(UserClassesRelativePath, true)
            ?? throw new InvalidOperationException("无法创建 Software\\Classes 键。");
        using (var extKey = classesRoot.CreateSubKey(extension, true))
        {
            extKey.SetValue(null, ProgId);
        }
        using (var progKey = classesRoot.CreateSubKey(ProgId, true))
        {
            progKey.SetValue(null, FileTypeDescription);
            using (var iconKey = progKey.CreateSubKey("DefaultIcon", true))
            {
                iconKey.SetValue(null, FormatDefaultIconRegistryValue(resolvedIconFull));
            }
            using (var commandKey = progKey.CreateSubKey(@"shell\open\command", true))
            {
                commandKey.SetValue(null, $"\"{normalizedExeFullPath}\" \"%1\"");
            }
        }
    }

    [DllImport("shell32.dll")]
    private static extern void SHChangeNotify(int wEventId, uint uFlags, IntPtr dwItem1, IntPtr dwItem2);
}
