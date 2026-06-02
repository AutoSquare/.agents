using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using {{RootNamespace}}.Services;
using {{RootNamespace}}.ViewModel;

namespace {{RootNamespace}};

/// <summary>
/// 主窗口：archive 工程文件菜单、Ctrl+S 保存与 form-demo 绑定提交。
/// </summary>
public partial class MainWindow : Window
{
    private readonly MainWindowViewModel _viewModel;

    /// <summary>
    /// 初始化主窗口并注入视图模型。
    /// </summary>
    public MainWindow()
    {
        InitializeComponent();
        Loaded += OnMainWindowLoaded;
        _viewModel = CompositionRoot.BuildViewModel();
        DataContext = _viewModel;
        ApplicationBootstrap.OnStartup(_viewModel);
    }

    /// <summary>
    /// 窗口加载完成后恢复尺寸与位置（避免被 XAML 默认值覆盖）。
    /// </summary>
    private void OnMainWindowLoaded(object sender, RoutedEventArgs e)
    {
        ApplicationBootstrap.ApplyWindowGeometry(this);
    }

    /// <summary>
    /// 窗口关闭前终止活跃计算子进程并持久化工程。
    /// </summary>
    /// <param name="e">关闭事件参数。</param>
    protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
    {
        if (_viewModel.IsBusy)
        {
            var result = MessageBox.Show(
                "计算正在进行，确定要退出吗？",
                "{{DisplayName}}",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning);
            if (result != MessageBoxResult.Yes)
            {
                e.Cancel = true;
                return;
            }
        }
        CompositionRoot.CalculationRunCoordinator.CancelAndKillAll();
        ApplicationBootstrap.SaveWindowGeometry(this);
        CommitTextBoxBindings();
        _viewModel.FlushPendingFormEdits();
        ProjectSession.Live.PersistOnExit(ProjectSession.BuildUiState(_viewModel.StatusText));
        ProjectSession.Live.CleanupPythonWorkspaceDirectory();
        base.OnClosing(e);
    }

    /// <summary>
    /// 关窗前强制提交文本框绑定，避免未落盘导致 .ast 内表单字段缺失。
    /// </summary>
    private void CommitTextBoxBindings()
    {
        ProjectNameBox.GetBindingExpression(TextBox.TextProperty)?.UpdateSource();
        OwnerNameBox.GetBindingExpression(TextBox.TextProperty)?.UpdateSource();
        MemoBox.GetBindingExpression(TextBox.TextProperty)?.UpdateSource();
        ContactPhoneBox.GetBindingExpression(TextBox.TextProperty)?.UpdateSource();
        DepartmentBox.GetBindingExpression(TextBox.TextProperty)?.UpdateSource();
        SiteAddressBox.GetBindingExpression(TextBox.TextProperty)?.UpdateSource();
    }
}
