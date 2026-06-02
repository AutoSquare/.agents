using System.Windows;
using System.Windows.Threading;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Win32;
using {{RootNamespace}}.Model.Domain;
using {{RootNamespace}}.Services;

namespace {{RootNamespace}}.ViewModel;

/// <summary>
/// 主窗口视图模型（archive + form-demo）：工程文件菜单、Ctrl+S 与测试表单脏标记。
/// </summary>
public sealed class MainWindowViewModel : ViewModelBase
{
    private readonly SampleCalculationService _calculationService;
    private readonly CalculationRunCoordinator _coordinator;
    private readonly ProjectFileService _projectFileService;
    private readonly DispatcherTimer _formSyncTimer;
    private string _statusText = "就绪";
    private bool _isBusy;
    private string _projectName = string.Empty;
    private string _ownerName = string.Empty;
    private string _memo = string.Empty;
    private string _contactPhone = string.Empty;
    private string _department = string.Empty;
    private string _siteAddress = string.Empty;
    private bool _isLoadingForm;

    /// <summary>
    /// 初始化主窗口视图模型。
    /// </summary>
    /// <param name="calculationService">样本计算服务。</param>
    /// <param name="coordinator">计算协调器。</param>
    /// <param name="projectFileService">工程文件服务。</param>
    public MainWindowViewModel(
        SampleCalculationService calculationService,
        CalculationRunCoordinator coordinator,
        ProjectFileService projectFileService)
    {
        _calculationService = calculationService;
        _coordinator = coordinator;
        _projectFileService = projectFileService;
        RunSampleCommand = new AsyncRelayCommand(RunSampleAsync, () => !IsBusy);
        OpenProjectCommand = new AsyncRelayCommand(OpenProjectAsync, () => !IsBusy);
        SaveProjectCommand = new AsyncRelayCommand(SaveProjectAsync, () => !IsBusy);
        SaveProjectAsCommand = new AsyncRelayCommand(SaveProjectAsAsync, () => !IsBusy);
        _formSyncTimer = new DispatcherTimer(
            TimeSpan.FromMilliseconds(500),
            DispatcherPriority.Background,
            OnFormSyncTimerTick,
            Application.Current.Dispatcher);
    }

    /// <summary>项目名称。</summary>
    public string ProjectName
    {
        get => _projectName;
        set
        {
            if (SetProperty(ref _projectName, value))
                OnFormFieldEdited();
        }
    }

    /// <summary>负责人。</summary>
    public string OwnerName
    {
        get => _ownerName;
        set
        {
            if (SetProperty(ref _ownerName, value))
                OnFormFieldEdited();
        }
    }

    /// <summary>备注。</summary>
    public string Memo
    {
        get => _memo;
        set
        {
            if (SetProperty(ref _memo, value))
                OnFormFieldEdited();
        }
    }

    /// <summary>联系电话。</summary>
    public string ContactPhone
    {
        get => _contactPhone;
        set
        {
            if (SetProperty(ref _contactPhone, value))
                OnFormFieldEdited();
        }
    }

    /// <summary>所属部门。</summary>
    public string Department
    {
        get => _department;
        set
        {
            if (SetProperty(ref _department, value))
                OnFormFieldEdited();
        }
    }

    /// <summary>工程地点。</summary>
    public string SiteAddress
    {
        get => _siteAddress;
        set
        {
            if (SetProperty(ref _siteAddress, value))
                OnFormFieldEdited();
        }
    }

    /// <summary>状态栏文本。</summary>
    public string StatusText
    {
        get => _statusText;
        set => SetProperty(ref _statusText, value);
    }

    /// <summary>是否正在计算。</summary>
    public bool IsBusy
    {
        get => _isBusy;
        private set
        {
            if (SetProperty(ref _isBusy, value))
            {
                RunSampleCommand.NotifyCanExecuteChanged();
                OpenProjectCommand.NotifyCanExecuteChanged();
                SaveProjectCommand.NotifyCanExecuteChanged();
                SaveProjectAsCommand.NotifyCanExecuteChanged();
            }
        }
    }

    /// <summary>运行样本计算命令。</summary>
    public AsyncRelayCommand RunSampleCommand { get; }

    /// <summary>打开工程命令。</summary>
    public AsyncRelayCommand OpenProjectCommand { get; }

    /// <summary>保存工程命令。</summary>
    public AsyncRelayCommand SaveProjectCommand { get; }

    /// <summary>另存为命令。</summary>
    public AsyncRelayCommand SaveProjectAsCommand { get; }

    /// <summary>
    /// 刷盘前同步未落盘的表单编辑（关窗或计算前调用）。
    /// </summary>
    public void FlushPendingFormEdits()
    {
        _formSyncTimer.Stop();
        if (_isLoadingForm)
            return;
        SyncFormToSession();
    }

    /// <summary>
    /// 从当前工程文档加载测试表单字段。
    /// </summary>
    public void LoadFormFromSession()
    {
        _isLoadingForm = true;
        try
        {
            var form = SessionFormData.FromDocument(ProjectSession.Live.Document);
            ProjectName = form.ProjectName;
            OwnerName = form.OwnerName;
            Memo = form.Memo;
            ContactPhone = form.ContactPhone;
            Department = form.Department;
            SiteAddress = form.SiteAddress;
        }
        finally
        {
            _isLoadingForm = false;
        }
    }

    /// <summary>
    /// 将测试表单字段写回工程文档并标记未保存。
    /// </summary>
    public void SyncFormToSession()
    {
        new SessionFormData
        {
            ProjectName = ProjectName,
            OwnerName = OwnerName,
            Memo = Memo,
            ContactPhone = ContactPhone,
            Department = Department,
            SiteAddress = SiteAddress,
        }.ApplyToDocument(ProjectSession.Live.Document);
        ProjectSession.Live.MarkDirty();
    }

    /// <summary>
    /// 刷新工程路径状态摘要并加载表单。
    /// </summary>
    /// <param name="currentPath">当前工程路径。</param>
    public void RefreshProjectStatus(string? currentPath)
    {
        var tableCount = ProjectSession.Live.Document.DataTables.Count + ProjectSession.Live.Document.MaterialTables.Count;
        StatusText = string.IsNullOrWhiteSpace(currentPath)
            ? $"新工程（{tableCount} 张表，请另存为 {ProjectFileFormat.Extension} 或 Ctrl+S）"
            : $"已打开：{currentPath}（{tableCount} 张表）";
        LoadFormFromSession();
    }

    private void OnFormFieldEdited()
    {
        if (_isLoadingForm)
            return;
        SyncFormToSession();
        _formSyncTimer.Stop();
        _formSyncTimer.Start();
    }

    private void OnFormSyncTimerTick(object? sender, EventArgs e)
    {
        _formSyncTimer.Stop();
        SyncFormToSession();
    }

    private async Task RunSampleAsync()
    {
        IsBusy = true;
        StatusText = "计算中…";
        FlushPendingFormEdits();
        var token = _coordinator.BeginRun();
        try
        {
            var ok = await _calculationService.RunSampleAsync(
                line => StatusText = line.StartsWith("<log>") ? line[5..] : line,
                token).ConfigureAwait(true);
            StatusText = ok ? "样本计算完成（已标记未保存）" : "样本计算失败";
            if (ok)
                RefreshProjectStatus(_projectFileService.CurrentPath);
        }
        catch (OperationCanceledException)
        {
            StatusText = "已取消";
        }
        finally
        {
            _coordinator.EndRun();
            IsBusy = false;
        }
    }

    private async Task OpenProjectAsync()
    {
        var dialog = new OpenFileDialog
        {
            Filter = $"工程文件 (*{ProjectFileFormat.Extension})|*{ProjectFileFormat.Extension}|所有文件 (*.*)|*.*",
            Title = "打开工程",
        };
        if (dialog.ShowDialog() != true)
            return;
        try
        {
            await _projectFileService.OpenAsync(dialog.FileName).ConfigureAwait(true);
            RefreshProjectStatus(_projectFileService.CurrentPath);
        }
        catch (Exception ex)
        {
            StatusText = "打开失败";
            MessageBox.Show(ex.Message, "{{DisplayName}}", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private async Task SaveProjectAsync()
    {
        FlushPendingFormEdits();
        if (string.IsNullOrWhiteSpace(_projectFileService.CurrentPath))
        {
            await SaveProjectAsAsync().ConfigureAwait(true);
            return;
        }
        try
        {
            if (await _projectFileService.SaveAsync().ConfigureAwait(true))
                RefreshProjectStatus(_projectFileService.CurrentPath);
            else
                StatusText = "保存失败：请先另存为";
        }
        catch (Exception ex)
        {
            StatusText = "保存失败";
            MessageBox.Show(ex.Message, "{{DisplayName}}", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private async Task SaveProjectAsAsync()
    {
        FlushPendingFormEdits();
        var dialog = new SaveFileDialog
        {
            Filter = $"工程文件 (*{ProjectFileFormat.Extension})|*{ProjectFileFormat.Extension}",
            Title = "另存为工程",
            DefaultExt = ProjectFileFormat.Extension.TrimStart('.'),
        };
        if (dialog.ShowDialog() != true)
            return;
        try
        {
            await _projectFileService.SaveAsAsync(dialog.FileName).ConfigureAwait(true);
            RefreshProjectStatus(_projectFileService.CurrentPath);
        }
        catch (Exception ex)
        {
            StatusText = "另存为失败";
            MessageBox.Show(ex.Message, "{{DisplayName}}", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }
}
