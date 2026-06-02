using System.IO;
using System.Windows;
using {{RootNamespace}}.ViewModel;

namespace {{RootNamespace}}.Services;

/// <summary>
/// archive 模式应用启动与窗口偏好恢复。
/// </summary>
public static class ApplicationBootstrap
{
    private static string? _pendingStartupProjectPath;

    /// <summary>
    /// 由 <see cref="App"/> 在创建主窗口前设置；优先于「打开最近工程」。
    /// </summary>
    /// <param name="projectFilePath">命令行或双击传入的工程路径；null 表示无。</param>
    public static void ConfigureStartupProjectPath(string? projectFilePath) =>
        _pendingStartupProjectPath = projectFilePath;

    /// <summary>
    /// 启动时初始化会话：命令行工程 &gt; 最近工程 &gt; 新工程。
    /// </summary>
    /// <param name="viewModel">主窗口视图模型。</param>
    public static async void OnStartup(MainWindowViewModel viewModel)
    {
        ProjectSession.Live.EnsureInitialized();
        var fileService = CompositionRoot.ProjectFileService;
        var startupPath = _pendingStartupProjectPath;
        _pendingStartupProjectPath = null;

        if (!string.IsNullOrWhiteSpace(startupPath))
        {
            await OpenProjectAtStartupAsync(viewModel, fileService, startupPath).ConfigureAwait(true);
            return;
        }

        var opened = await fileService.TryOpenLastProjectAsync().ConfigureAwait(true);
        viewModel.RefreshProjectStatus(opened ? fileService.CurrentPath : null);
    }

    /// <summary>
    /// 从 user_settings 恢复窗口尺寸、位置与 WindowState（须在 Loaded 后调用）。
    /// </summary>
    /// <param name="window">主窗口。</param>
    public static void ApplyWindowGeometry(Window window)
    {
        var placement = UserSettingsStore.LoadWindowPlacement();
        if (placement.Width is > 200 && placement.Height is > 150)
        {
            window.Width = placement.Width.Value;
            window.Height = placement.Height.Value;
        }
        if (placement.Left.HasValue && placement.Top.HasValue)
        {
            window.WindowStartupLocation = WindowStartupLocation.Manual;
            window.Left = placement.Left.Value;
            window.Top = placement.Top.Value;
        }
        if (!string.IsNullOrEmpty(placement.State) &&
            Enum.TryParse<WindowState>(placement.State, out var state))
        {
            window.WindowState = state;
        }
    }

    /// <summary>
    /// 保存窗口布局到 user_settings。
    /// </summary>
    /// <param name="window">主窗口。</param>
    public static void SaveWindowGeometry(Window window)
    {
        var bounds = window.WindowState == WindowState.Normal
            ? new Rect(window.Left, window.Top, window.Width, window.Height)
            : window.RestoreBounds;
        UserSettingsStore.SaveWindowPlacement(
            bounds.Width,
            bounds.Height,
            bounds.Left,
            bounds.Top,
            window.WindowState.ToString());
    }

    private static async Task OpenProjectAtStartupAsync(
        MainWindowViewModel viewModel,
        ProjectFileService fileService,
        string filePath)
    {
        if (!File.Exists(filePath))
        {
            MessageBox.Show(
                $"工程文件不存在：\r\n{filePath}",
                "{{DisplayName}}",
                MessageBoxButton.OK,
                MessageBoxImage.Warning);
            viewModel.RefreshProjectStatus(null);
            return;
        }

        try
        {
            await fileService.OpenAsync(filePath).ConfigureAwait(true);
            viewModel.RefreshProjectStatus(fileService.CurrentPath);
        }
        catch (Exception ex)
        {
            viewModel.RefreshProjectStatus(null);
            MessageBox.Show(
                ex.Message,
                "{{DisplayName}}",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
        }
    }
}
