using System.Windows;
using System.Windows.Threading;
using CommunityToolkit.Mvvm.Input;
using {{RootNamespace}}.Model.Domain;
using {{RootNamespace}}.Services;

namespace {{RootNamespace}}.ViewModel;

/// <summary>
/// 主窗口视图模型（memory + form-demo）：状态文本、样本计算与测试表单自动保存。
/// </summary>
public sealed class MainWindowViewModel : ViewModelBase
{
    private static bool _snapshotNoticeShown;
    private readonly SampleCalculationService _calculationService;
    private readonly CalculationRunCoordinator _coordinator;
    private readonly DispatcherTimer _formAutoSaveTimer;
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
    public MainWindowViewModel(SampleCalculationService calculationService, CalculationRunCoordinator coordinator)
    {
        _calculationService = calculationService;
        _coordinator = coordinator;
        RunSampleCommand = new AsyncRelayCommand(RunSampleAsync, () => !IsBusy);
        _formAutoSaveTimer = new DispatcherTimer(
            TimeSpan.FromMilliseconds(500),
            DispatcherPriority.Background,
            OnFormAutoSaveTimerTick,
            Application.Current.Dispatcher);
    }

    /// <summary>项目名称（写入 dataTables「测试表单」）。</summary>
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
                RunSampleCommand.NotifyCanExecuteChanged();
        }
    }

    /// <summary>运行样本计算命令。</summary>
    public AsyncRelayCommand RunSampleCommand { get; }

    /// <summary>
    /// 刷盘前同步未落盘的表单编辑（关窗或计算前调用）。
    /// </summary>
    public void FlushPendingFormEdits()
    {
        _formAutoSaveTimer.Stop();
        if (_isLoadingForm)
            return;
        SyncFormToSession();
        ProjectSession.Live.SaveSnapshot(ProjectSession.BuildUiState(StatusText));
    }

    /// <summary>
    /// 从当前会话文档加载测试表单字段。
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
    /// 将测试表单字段写回会话文档。
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
    /// 刷新会话状态摘要（启动时调用）。
    /// </summary>
    /// <param name="restoredFromSnapshot">启动前是否存在快照文件。</param>
    /// <param name="savedStatusText">快照 uiState 中保存的状态栏文本。</param>
    public void RefreshSessionStatus(bool restoredFromSnapshot, string? savedStatusText = null)
    {
        if (restoredFromSnapshot && !string.IsNullOrWhiteSpace(savedStatusText))
        {
            StatusText = savedStatusText;
            LoadFormFromSession();
            return;
        }
        var doc = ProjectSession.Live.Document;
        var tableCount = doc.DataTables.Count + doc.MaterialTables.Count;
        var hasResult = doc.DataTables.ContainsKey(ProjectFileFormat.SampleResultTable);
        var snapPath = SessionSnapshotStore.SnapshotFilePath;
        if (restoredFromSnapshot)
        {
            StatusText = hasResult
                ? $"已恢复上次会话（含 {ProjectFileFormat.SampleResultTable}，共 {tableCount} 张表）\n快照：{snapPath}"
                : $"已恢复上次会话（{tableCount} 张表）\n快照：{snapPath}";
        }
        else
        {
            StatusText =
                $"新会话（memory 模式：编辑与计算后自动写入 AppData 快照）\n共 {tableCount} 张表";
        }
        LoadFormFromSession();
    }

    private void OnFormAutoSaveTimerTick(object? sender, EventArgs e)
    {
        _formAutoSaveTimer.Stop();
        SyncFormToSession();
        ProjectSession.Live.SaveSnapshot(ProjectSession.BuildUiState(StatusText));
    }

    private void OnFormFieldEdited()
    {
        if (_isLoadingForm)
            return;
        SyncFormToSession();
        _formAutoSaveTimer.Stop();
        _formAutoSaveTimer.Start();
    }

    private async Task RunSampleAsync()
    {
        IsBusy = true;
        StatusText = "计算中…";
        var token = _coordinator.BeginRun();
        try
        {
            var ok = await _calculationService.RunSampleAsync(
                line => StatusText = line.StartsWith("<log>") ? line[5..] : line,
                token).ConfigureAwait(true);
            if (ok)
            {
                FlushPendingFormEdits();
                var snapPath = SessionSnapshotStore.SnapshotFilePath;
                var hasResult = ProjectSession.Live.Document.DataTables.ContainsKey(ProjectFileFormat.SampleResultTable);
                StatusText = hasResult
                    ? $"样本计算完成，已写入会话快照（含 {ProjectFileFormat.SampleResultTable}）\n{snapPath}"
                    : $"样本计算完成，已写入会话快照\n{snapPath}";
                ProjectSession.Live.SaveSnapshot(ProjectSession.BuildUiState(StatusText));
                MaybeShowSnapshotNoticeOnce(snapPath);
            }
            else
            {
                StatusText = "样本计算失败";
            }
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

    private static void MaybeShowSnapshotNoticeOnce(string snapPath)
    {
        if (_snapshotNoticeShown)
            return;
        _snapshotNoticeShown = true;
        MessageBox.Show(
            $"会话数据已保存至：\n{snapPath}\n\n下次启动将自动恢复（memory 模式，无工程文件菜单）。",
            "{{DisplayName}}",
            MessageBoxButton.OK,
            MessageBoxImage.Information);
    }
}
