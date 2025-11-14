using UnityEngine;
using DG.Tweening;

/// <summary>
/// Template for DOTween initialization and global management.
/// Add this to a GameObject in your first scene.
/// </summary>
public class DOTweenManager : MonoBehaviour
{
    [Header("DOTween Settings")]
    [SerializeField] private bool useSafeMode = true;
    [SerializeField] private LogBehaviour logBehaviour = LogBehaviour.ErrorsOnly;
    [SerializeField] private int tweenersCapacity = 200;
    [SerializeField] private int sequencesCapacity = 50;

    [Header("Global Settings")]
    [SerializeField] private float globalTimeScale = 1f;
    [SerializeField] private Ease defaultEaseType = Ease.OutQuad;
    [SerializeField] private bool debugMode = false;

    void Awake()
    {
        // Initialize DOTween with custom settings
        DOTween.Init(useSafeMode, logBehaviour)
            .SetCapacity(tweenersCapacity, sequencesCapacity);

        // Apply global settings
        DOTween.timeScale = globalTimeScale;
        DOTween.defaultEaseType = defaultEaseType;
        DOTween.debugMode = debugMode;

        Debug.Log($"DOTween initialized - Safe Mode: {useSafeMode}, " +
                  $"Capacity: {tweenersCapacity} tweeners, {sequencesCapacity} sequences");
    }

    void OnApplicationQuit()
    {
        // Clean up all tweens on quit
        DOTween.KillAll();
    }

    /// <summary>
    /// Pause all active tweens (useful for pause menus)
    /// </summary>
    public void PauseAllTweens()
    {
        DOTween.PauseAll();
    }

    /// <summary>
    /// Resume all paused tweens
    /// </summary>
    public void ResumeAllTweens()
    {
        DOTween.PlayAll();
    }

    /// <summary>
    /// Get debug information about active tweens
    /// </summary>
    public string GetDebugInfo()
    {
        int activeTweens = DOTween.TotalPlayingTweens();
        return $"Active Tweens: {activeTweens}";
    }

#if UNITY_EDITOR
    void OnGUI()
    {
        if (debugMode)
        {
            GUI.Label(new Rect(10, 10, 300, 20), GetDebugInfo());
        }
    }
#endif
}
