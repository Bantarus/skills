using UnityEngine;
using DG.Tweening;
using System.Collections;

/// <summary>
/// Template for common gameplay animation patterns using DOTween.
/// Use as a reference or extend for your specific game needs.
/// </summary>
public class GameplayAnimations : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private Transform targetTransform;

    [Header("Movement Settings")]
    [SerializeField] private float moveDuration = 1f;
    [SerializeField] private Ease moveEase = Ease.OutQuad;

    [Header("Combat Settings")]
    [SerializeField] private float hitDuration = 0.2f;
    [SerializeField] private float hitStrength = 0.5f;

    private Vector3 originalScale;
    private Vector3 originalPosition;

    void Start()
    {
        if (!targetTransform) targetTransform = transform;
        originalScale = targetTransform.localScale;
        originalPosition = targetTransform.position;
    }

    /// <summary>
    /// Move to a target position with smooth easing
    /// </summary>
    public Tween MoveTo(Vector3 targetPosition, float duration = -1)
    {
        float d = duration > 0 ? duration : moveDuration;
        return targetTransform.DOMove(targetPosition, d).SetEase(moveEase);
    }

    /// <summary>
    /// Jump to a target position with arc
    /// </summary>
    public Tween JumpTo(Vector3 targetPosition, float jumpPower = 2f, int numJumps = 1, float duration = -1)
    {
        float d = duration > 0 ? duration : moveDuration;
        return targetTransform.DOJump(targetPosition, jumpPower, numJumps, d).SetEase(moveEase);
    }

    /// <summary>
    /// Follow a path with waypoints
    /// </summary>
    public Tween FollowPath(Vector3[] waypoints, PathType pathType = PathType.CatmullRom, float duration = -1)
    {
        float d = duration > 0 ? duration : moveDuration * 2;
        return targetTransform.DOPath(waypoints, d, pathType)
            .SetEase(Ease.Linear)
            .SetLookAt(0.01f);
    }

    /// <summary>
    /// Patrol between two points infinitely
    /// </summary>
    public Tween Patrol(Vector3 pointA, Vector3 pointB, float duration = -1)
    {
        float d = duration > 0 ? duration : moveDuration;
        return targetTransform.DOMove(pointB, d)
            .SetEase(Ease.Linear)
            .SetLoops(-1, LoopType.Yoyo);
    }

    /// <summary>
    /// Circle around a point
    /// </summary>
    public void CircleAround(Vector3 center, float radius, float duration)
    {
        int segments = 36;
        Vector3[] path = new Vector3[segments];

        for (int i = 0; i < segments; i++)
        {
            float angle = i * 360f / segments * Mathf.Deg2Rad;
            path[i] = center + new Vector3(Mathf.Cos(angle) * radius, 0, Mathf.Sin(angle) * radius);
        }

        targetTransform.DOPath(path, duration, PathType.CatmullRom)
            .SetEase(Ease.Linear)
            .SetLoops(-1, LoopType.Restart);
    }

    /// <summary>
    /// Hit reaction - knock back and scale
    /// </summary>
    public Sequence HitReaction(Vector3 knockbackDirection)
    {
        Sequence seq = DOTween.Sequence();

        // Knockback
        Vector3 knockbackPos = targetTransform.position + knockbackDirection.normalized * hitStrength;
        seq.Append(targetTransform.DOMove(knockbackPos, hitDuration * 0.3f));
        seq.Append(targetTransform.DOMove(originalPosition, hitDuration * 0.7f).SetEase(Ease.OutBounce));

        // Scale squash
        seq.Join(targetTransform.DOScale(originalScale * 0.8f, hitDuration * 0.3f));
        seq.Append(targetTransform.DOScale(originalScale, hitDuration * 0.7f).SetEase(Ease.OutBounce));

        return seq;
    }

    /// <summary>
    /// Death animation - scale down and fade
    /// </summary>
    public Sequence DeathAnimation()
    {
        Sequence seq = DOTween.Sequence();

        // Shrink and rotate
        seq.Append(targetTransform.DOScale(Vector3.zero, 0.5f).SetEase(Ease.InBack));
        seq.Join(targetTransform.DORotate(new Vector3(0, 360, 0), 0.5f, RotateMode.FastBeyond360));

        // Optional: Add material fade if you have a renderer
        Renderer renderer = targetTransform.GetComponent<Renderer>();
        if (renderer && renderer.material.HasProperty("_Color"))
        {
            seq.Join(renderer.material.DOFade(0f, 0.5f));
        }

        return seq;
    }

    /// <summary>
    /// Spawn/appear animation
    /// </summary>
    public Sequence SpawnAnimation()
    {
        Sequence seq = DOTween.Sequence();

        // Start from small and grow
        targetTransform.localScale = Vector3.zero;
        seq.Append(targetTransform.DOScale(originalScale, 0.5f).SetEase(Ease.OutBack));

        // Add a little bounce
        seq.Append(targetTransform.DOPunchScale(Vector3.one * 0.2f, 0.3f, 5, 0.5f));

        return seq;
    }

    /// <summary>
    /// Floating/hovering idle animation
    /// </summary>
    public void StartFloating(float height = 0.5f, float duration = 2f)
    {
        targetTransform.DOMoveY(originalPosition.y + height, duration)
            .SetEase(Ease.InOutSine)
            .SetLoops(-1, LoopType.Yoyo)
            .SetId("Floating");
    }

    /// <summary>
    /// Stop floating animation
    /// </summary>
    public void StopFloating()
    {
        DOTween.Kill("Floating");
        targetTransform.DOMoveY(originalPosition.y, 0.5f).SetEase(Ease.OutQuad);
    }

    /// <summary>
    /// Rotate continuously
    /// </summary>
    public void StartRotating(Vector3 rotation, float duration = 2f)
    {
        targetTransform.DORotate(rotation, duration, RotateMode.FastBeyond360)
            .SetEase(Ease.Linear)
            .SetLoops(-1, LoopType.Restart)
            .SetId("Rotating");
    }

    /// <summary>
    /// Stop rotating
    /// </summary>
    public void StopRotating()
    {
        DOTween.Kill("Rotating");
        targetTransform.DORotate(Vector3.zero, 0.5f).SetEase(Ease.OutQuad);
    }

    /// <summary>
    /// Shake effect (e.g., for explosions nearby)
    /// </summary>
    public void Shake(float duration = 0.5f, float strength = 1f, int vibrato = 10)
    {
        targetTransform.DOShakePosition(duration, strength, vibrato, 90f, false, true);
    }

    /// <summary>
    /// Look at target smoothly
    /// </summary>
    public Tween LookAtTarget(Vector3 target, float duration = 0.5f)
    {
        return targetTransform.DOLookAt(target, duration);
    }

    /// <summary>
    /// Camera shake effect
    /// </summary>
    public static void ShakeCamera(Camera cam, float duration = 0.5f, float strength = 0.3f)
    {
        cam.transform.DOShakePosition(duration, strength, 10, 90f, false, true)
            .SetUpdate(true); // Unscaled time for pause menus
    }

    /// <summary>
    /// Collect item animation - move to target and scale down
    /// </summary>
    public Sequence CollectAnimation(Vector3 targetPosition, System.Action onComplete = null)
    {
        Sequence seq = DOTween.Sequence();

        // Move to target with ease in
        seq.Append(targetTransform.DOMove(targetPosition, 0.6f).SetEase(Ease.InQuad));

        // Scale down while moving
        seq.Join(targetTransform.DOScale(Vector3.zero, 0.6f).SetEase(Ease.InQuad));

        // Callback when complete
        if (onComplete != null)
        {
            seq.OnComplete(() => onComplete());
        }

        return seq;
    }

    void OnDestroy()
    {
        // Clean up all tweens on this object
        DOTween.Kill(targetTransform);
        DOTween.Kill("Floating");
        DOTween.Kill("Rotating");
    }
}
