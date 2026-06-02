using System.IO;
using System.Linq;
using System.Windows;
using {{RootNamespace}}.Model.Domain;
using {{RootNamespace}}.Services;
using {{RootNamespace}}.ViewModel;

namespace {{RootNamespace}};

/// <summary>
/// WPF 应用程序入口：注册 {Ext} 关联、解析命令行工程路径并显示主窗口。
/// </summary>
public partial class App : Application
{
    /// <summary>
    /// 应用启动：文件关联、命令行打开工程、创建主窗口。
    /// </summary>
    /// <param name="sender">事件源。</param>
    /// <param name="e">启动参数。</param>
    private void Application_Startup(object sender, StartupEventArgs e)
    {
        FileAssociationUtilities.TryRegisterOnStartup();
        ApplicationBootstrap.ConfigureStartupProjectPath(TryGetStartupProjectFilePath(e));
        var mainWindow = new MainWindow();
        MainWindow = mainWindow;
        mainWindow.Show();
    }

    /// <summary>
    /// 从启动参数解析工程文件路径（资源管理器双击或 <c>app.exe path.ast</c>）。
    /// </summary>
    /// <param name="e">启动事件参数。</param>
    /// <returns>规范化绝对路径；无有效参数时 null。</returns>
    private static string? TryGetStartupProjectFilePath(StartupEventArgs e)
    {
        var raw = e.Args.FirstOrDefault(a =>
            !string.IsNullOrWhiteSpace(a)
            && !a.StartsWith("--", StringComparison.Ordinal));
        if (raw is null)
            return null;
        var trimmed = raw.Trim().Trim('"');
        if (!trimmed.EndsWith(ProjectFileFormat.Extension, StringComparison.OrdinalIgnoreCase))
            return null;
        try
        {
            return Path.GetFullPath(trimmed);
        }
        catch (IOException)
        {
            return null;
        }
        catch (ArgumentException)
        {
            return null;
        }
    }
}
