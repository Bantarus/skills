using UnityEngine;
using UnityEngine.UI;
using DG.Tweening;
using System.Collections;

/// <summary>
/// Template for common UI animation patterns using DOTween.
/// Attach to UI elements or use as a reference for custom animations.
/// </summary>
public class UIAnimations : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private CanvasGroup canvasGroup;
    [SerializeField] private RectTransform rectTransform;
    [SerializeField] private Image image;

    [Header("Animation Settings")]
    [SerializeField] private float fadeDuration = 0.5f;
    [SerializeField] private float moveDuration = 0.3f;
    [SerializeField] private Ease fadeEase = Ease.OutQuad;
    [SerializeField] private Ease moveEase = Ease.OutBack;

    private Vector2 originalPosition;
    private Sequence currentSequence;

    void Awake()
    {
        if (!canvasGroup) canvasGroup = GetComponent<CanvasGroup>();
        if (!rectTransform) rectTransform = GetComponent<RectTransform>();
        if (!image) image = GetComponent<Image>();

        originalPosition = rectTransform.anchoredPosition;
    }

    /// <summary>
    /// Fade in the UI element
    /// </summary>
    public void FadeIn()
    {
        canvasGroup.DOFade(1f, fadeDuration).SetEase(fadeEase);
    }

    /// <summary>
    /// Fade out the UI element
    /// </summary>
    public void FadeOut()
    {
        canvasGroup.DOFade(0f, fadeDuration).SetEase(fadeEase);
    }

    /// <summary>
    /// Fade in and enable interaction
    /// </summary>
    public void Show()
    {
        canvasGroup.interactable = true;
        canvasGroup.blocksRaycasts = true;
        canvasGroup.DOFade(1f, fadeDuration).SetEase(fadeEase);
    }

    /// <summary>
    /// Fade out and disable interaction
    /// </summary>
    public void Hide()
    {
        canvasGroup.interactable = false;
        canvasGroup.blocksRaycasts = false;
        canvasGroup.DOFade(0f, fadeDuration).SetEase(fadeEase);
    }

    /// <summary>
    /// Slide in from the right
    /// </summary>
    public void SlideInFromRight()
    {
        rectTransform.anchoredPosition = originalPosition + Vector2.right * 1000f;
        rectTransform.DOAnchorPos(originalPosition, moveDuration).SetEase(moveEase);
    }

    /// <summary>
    /// Slide in from the left
    /// </summary>
    public void SlideInFromLeft()
    {
        rectTransform.anchoredPosition = originalPosition + Vector2.left * 1000f;
        rectTransform.DOAnchorPos(originalPosition, moveDuration).SetEase(moveEase);
    }

    /// <summary>
    /// Slide in from the top
    /// </summary>
    public void SlideInFromTop()
    {
        rectTransform.anchoredPosition = originalPosition + Vector2.up * 1000f;
        rectTransform.DOAnchorPos(originalPosition, moveDuration).SetEase(moveEase);
    }

    /// <summary>
    /// Slide in from the bottom
    /// </summary>
    public void SlideInFromBottom()
    {
        rectTransform.anchoredPosition = originalPosition + Vector2.down * 1000f;
        rectTransform.DOAnchorPos(originalPosition, moveDuration).SetEase(moveEase);
    }

    /// <summary>
    /// Scale in (pop effect)
    /// </summary>
    public void ScaleIn()
    {
        rectTransform.localScale = Vector3.zero;
        rectTransform.DOScale(Vector3.one, moveDuration).SetEase(Ease.OutBack);
    }

    /// <summary>
    /// Scale out
    /// </summary>
    public void ScaleOut()
    {
        rectTransform.DOScale(Vector3.zero, moveDuration).SetEase(Ease.InBack);
    }

    /// <summary>
    /// Button press effect
    /// </summary>
    public void ButtonPressEffect()
    {
        Sequence seq = DOTween.Sequence();
        seq.Append(rectTransform.DOScale(0.9f, 0.1f));
        seq.Append(rectTransform.DOScale(1f, 0.1f));
    }

    /// <summary>
    /// Pulse effect (continuous)
    /// </summary>
    public void StartPulse()
    {
        rectTransform.DOScale(1.1f, 0.5f)
            .SetEase(Ease.InOutSine)
            .SetLoops(-1, LoopType.Yoyo);
    }

    /// <summary>
    /// Stop pulse effect
    /// </summary>
    public void StopPulse()
    {
        DOTween.Kill(rectTransform);
        rectTransform.localScale = Vector3.one;
    }

    /// <summary>
    /// Shake effect for errors or impacts
    /// </summary>
    public void Shake()
    {
        rectTransform.DOShakeAnchorPos(0.5f, 20f, 10, 90f, false, true);
    }

    /// <summary>
    /// Flash color effect
    /// </summary>
    public void FlashColor(Color color, float duration = 0.2f)
    {
        Color originalColor = image.color;
        Sequence seq = DOTween.Sequence();
        seq.Append(image.DOColor(color, duration));
        seq.Append(image.DOColor(originalColor, duration));
    }

    /// <summary>
    /// Complete intro animation sequence
    /// </summary>
    public void PlayIntroSequence()
    {
        currentSequence = DOTween.Sequence();

        // Start invisible and scaled down
        canvasGroup.alpha = 0f;
        rectTransform.localScale = Vector3.zero;

        // Animate in
        currentSequence.Append(canvasGroup.DOFade(1f, fadeDuration));
        currentSequence.Join(rectTransform.DOScale(Vector3.one, moveDuration).SetEase(Ease.OutBack));

        // Optional: Add a slight bounce at the end
        currentSequence.Append(rectTransform.DOPunchScale(Vector3.one * 0.1f, 0.3f, 5, 0.5f));
    }

    /// <summary>
    /// Complete outro animation sequence
    /// </summary>
    public void PlayOutroSequence()
    {
        currentSequence = DOTween.Sequence();

        // Animate out
        currentSequence.Append(rectTransform.DOScale(Vector3.zero, moveDuration).SetEase(Ease.InBack));
        currentSequence.Join(canvasGroup.DOFade(0f, fadeDuration));
    }

    void OnDestroy()
    {
        // Clean up tweens on destroy
        DOTween.Kill(transform);
        DOTween.Kill(rectTransform);
        DOTween.Kill(canvasGroup);
        DOTween.Kill(image);
        currentSequence?.Kill();
    }
}
