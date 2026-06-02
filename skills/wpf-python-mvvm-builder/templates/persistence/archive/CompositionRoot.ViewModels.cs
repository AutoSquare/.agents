using {{RootNamespace}}.Services;
using {{RootNamespace}}.ViewModel;

namespace {{RootNamespace}};

public static partial class CompositionRoot
{
    /// <summary>
    /// 构建主窗口视图模型（archive 模式）。
    /// </summary>
    /// <returns>已注入依赖的主窗口视图模型。</returns>
    public static MainWindowViewModel BuildViewModel()
    {
        return new MainWindowViewModel(
            SampleCalculationService,
            CalculationRunCoordinator,
            ProjectFileService);
    }
}
