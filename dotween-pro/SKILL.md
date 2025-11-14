---
name: dotween-pro
description: Comprehensive guide for implementing DOTween Pro in Unity 6.2 projects. Use when working with Unity animations, tweening, or when the user requests smooth interpolations, animations, sequences, paths, or DOTween-related features. Covers initialization, tweeners, sequences, settings, callbacks, control methods, coroutines, async/await, and editor components.
---

# DOTween Pro for Unity 6.2

## Overview

DOTween is a fast, efficient, and fully type-safe object-oriented animation engine for Unity. DOTween Pro extends the core library with additional scripting shortcuts, a visual animation editor, path editor, and extra features for 2D Toolkit and TextMesh Pro. This skill provides comprehensive guidance for implementing DOTween and DOTween Pro features in Unity 6.2 projects using C#.

Use this skill when:
- Implementing tweening animations in Unity projects
- Creating smooth transitions, movements, rotations, or scaling
- Building complex animation sequences
- Working with paths and bezier curves
- Setting up visual animations through the Unity Inspector
- Needing time-based interpolations for any property

## Core Concepts and Nomenclature

### Key Terms

**Tween**: A generic term for any DOTween animation. Every animation is a tween, whether it's a Tweener or a Sequence.

**Tweener**: The core animation unit that interpolates a single property or field from one value to another over time. When you create an animation like `transform.DOMove()`, you get a Tweener.

**Sequence**: A container for grouping multiple Tweeners and/or other Sequences together. Sequences can be nested without depth limits and allow for complex, choreographed animations.

**Target**: The object being animated (e.g., a Transform, Material, or custom object).

**Duration**: The time in seconds the animation takes to complete (excluding loops and delays).

**Ease**: The interpolation curve applied to the animation (e.g., linear, ease-in, ease-out, elastic, bounce).

### Method Naming Conventions

DOTween uses consistent prefixes for method categorization:

- **DO** prefix: Creates tweeners (e.g., `DOMove`, `DORotate`, `DOFade`)
- **Set** prefix: Configures tween settings (e.g., `SetEase`, `SetLoops`, `SetDelay`)
- **On** prefix: Registers callbacks (e.g., `OnComplete`, `OnUpdate`, `OnStart`)
- **WaitFor** prefix: Creates yield instructions for coroutines (e.g., `WaitForCompletion`, `WaitForKill`)

## DOTween.Init - Initialization and Setup

### Initial Setup Process

1. **Import DOTween**: After importing the package, open DOTween Utility Panel via `Tools > Demigiant > DOTween Utility Panel`
2. **Run Setup**: Click "Setup DOTween..." to configure the package for your Unity version
3. **Configure Preferences**: Optionally adjust initialization settings in the Utility Panel

### Initialization Methods

DOTween auto-initializes with default settings when you create your first tween. For custom configuration, manually initialize before creating any tweens:

```csharp
using DG.Tweening;

public class GameManager : MonoBehaviour
{
    void Awake()
    {
        // Simple initialization with default settings
        DOTween.Init();

        // OR: Initialize with custom settings
        DOTween.Init(useSafeMode: true, logBehaviour: LogBehaviour.ErrorsOnly)
            .SetCapacity(200, 50);
    }
}
```

### Initialization Parameters

**useSafeMode** (bool, default: false)
- When `true`, tweens are slightly slower but safer
- Automatically handles scenarios like targets being destroyed during animation
- Recommended for complex scenes with dynamic object lifecycles

**logBehaviour** (LogBehaviour enum)
- `LogBehaviour.ErrorsOnly`: Logs only errors (recommended for production)
- `LogBehaviour.Default`: Logs errors and warnings
- `LogBehaviour.Verbose`: Logs everything including additional information (useful for debugging)

### Capacity Configuration

```csharp
// Set maximum simultaneous tweens
// Parameters: maxTweeners, maxSequences
DOTween.SetCapacity(200, 50);
```

Setting capacity upfront prevents automatic expansion during runtime, improving performance.

### Global Settings

```csharp
// Global timescale for all tweens
DOTween.timeScale = 0.5f; // Half speed

// Timescale for only unscaled tweens
DOTween.unscaledTimeScale = 2f; // Double speed for unscaled tweens

// Default ease type for all tweens
DOTween.defaultEaseType = Ease.OutQuad;

// Enable/disable recycling (generally leave enabled)
DOTween.useSafeMode = true;
```

## Creating Tweeners

### Basic Tweener Creation

Tweeners are created using shortcut extension methods or DOTween static methods.

#### Transform Shortcuts

```csharp
using UnityEngine;
using DG.Tweening;

public class BasicTweening : MonoBehaviour
{
    void Start()
    {
        // Position tweening
        transform.DOMove(new Vector3(5, 2, 0), 2f);
        transform.DOMoveX(10f, 1f);
        transform.DOMoveY(5f, 1.5f);
        transform.DOMoveZ(-3f, 2f);
        transform.DOLocalMove(new Vector3(1, 1, 1), 2f);

        // Rotation tweening
        transform.DORotate(new Vector3(0, 180, 0), 1f);
        transform.DOLocalRotate(new Vector3(45, 0, 0), 1f);
        transform.DOLookAt(targetPosition, 1f);

        // Scale tweening
        transform.DOScale(new Vector3(2, 2, 2), 1f);
        transform.DOScale(1.5f, 1f); // Uniform scale
        transform.DOScaleX(2f, 0.5f);
        transform.DOScaleY(0.5f, 0.5f);
        transform.DOScaleZ(3f, 0.5f);
    }
}
```

#### Material and Color Tweening

```csharp
public class MaterialTweening : MonoBehaviour
{
    public Material material;
    public Renderer renderer;
    public SpriteRenderer spriteRenderer;

    void Start()
    {
        // Material color
        material.DOColor(Color.red, 1f);
        material.DOColor(Color.blue, "_EmissionColor", 2f);
        material.DOFade(0.5f, 1f); // Fade alpha

        // Renderer shortcuts
        renderer.material.DOColor(Color.green, 1f);

        // SpriteRenderer
        spriteRenderer.DOColor(Color.yellow, 1f);
        spriteRenderer.DOFade(0f, 1f);
    }
}
```

#### Rigidbody Tweening

```csharp
public class PhysicsTweening : MonoBehaviour
{
    public Rigidbody rb;
    public Rigidbody2D rb2D;

    void Start()
    {
        // 3D Rigidbody
        rb.DOMove(new Vector3(5, 0, 0), 2f);
        rb.DOMoveX(10f, 1f);
        rb.DORotate(new Vector3(0, 90, 0), 1f);
        rb.DOLookAt(targetPosition, 1f);

        // 2D Rigidbody
        rb2D.DOMove(new Vector2(5, 5), 2f);
        rb2D.DOMoveX(10f, 1f);
        rb2D.DORotate(90f, 1f);
    }
}
```

#### Camera Tweening

```csharp
public class CameraTweening : MonoBehaviour
{
    public Camera cam;

    void Start()
    {
        cam.DOFieldOfView(60f, 1f);
        cam.DOOrthoSize(8f, 2f);
        cam.DOColor(Color.gray, 1f); // Background color
        cam.DOShakePosition(1f, 0.5f); // Shake effect
    }
}
```

### DOVirtual - Virtual Property Tweening

Use DOVirtual when you need to tween a value without a direct property target:

```csharp
public class VirtualTweening : MonoBehaviour
{
    void Start()
    {
        // Float tweening with callback
        DOVirtual.Float(0f, 100f, 2f, (value) => {
            Debug.Log($"Current value: {value}");
        });

        // Color tweening with callback
        DOVirtual.Color(Color.white, Color.black, 1f, (color) => {
            material.color = color;
        });

        // Vector3 tweening
        DOVirtual.Vector3(Vector3.zero, Vector3.one, 1f, (vec) => {
            customObject.position = vec;
        });
    }
}
```

### Path Tweening

Create movement along paths with waypoints:

```csharp
public class PathTweening : MonoBehaviour
{
    void Start()
    {
        Vector3[] path = new Vector3[] {
            new Vector3(0, 0, 0),
            new Vector3(2, 2, 0),
            new Vector3(4, 0, 0),
            new Vector3(6, 3, 0)
        };

        // Linear path
        transform.DOPath(path, 3f, PathType.Linear)
            .SetEase(Ease.Linear);

        // Catmull-Rom smooth path
        transform.DOLocalPath(path, 3f, PathType.CatmullRom)
            .SetLookAt(0.01f); // Look along path direction

        // Cubic Bezier path (waypoints in groups of 3)
        Vector3[] bezierPath = new Vector3[] {
            new Vector3(1, 0, 0),    // IN control point
            new Vector3(2, 2, 0),    // Waypoint
            new Vector3(3, 0, 0),    // OUT control point
            new Vector3(3, 1, 0),    // IN control point
            new Vector3(5, 2, 0),    // Waypoint
            new Vector3(6, 0, 0)     // OUT control point
        };
        transform.DOPath(bezierPath, 4f, PathType.CubicBezier);
    }
}
```

### Special Effects Tweening

#### Punch Effects

Punches a value and returns to original elastically:

```csharp
public class PunchEffects : MonoBehaviour
{
    void Start()
    {
        // Punch scale (impact effect)
        transform.DOPunchScale(Vector3.one * 0.5f, 1f, vibrato: 10, elasticity: 1f);

        // Punch position (hit effect)
        transform.DOPunchPosition(Vector3.up * 2f, 1f, vibrato: 10, elasticity: 1f);

        // Punch rotation (shake effect)
        transform.DOPunchRotation(new Vector3(0, 0, 45f), 1f, vibrato: 10, elasticity: 1f);
    }
}
```

#### Shake Effects

Shakes a value with randomness:

```csharp
public class ShakeEffects : MonoBehaviour
{
    void Start()
    {
        // Shake position (earthquake, camera shake)
        transform.DOShakePosition(
            duration: 2f,
            strength: 1f,
            vibrato: 10,
            randomness: 90f,
            fadeOut: true
        );

        // Shake rotation (rumble effect)
        transform.DOShakeRotation(1f, strength: new Vector3(45, 45, 45));

        // Shake scale (wobble effect)
        transform.DOShakeScale(1f, 0.5f);
    }
}
```

## Creating Sequences

Sequences group multiple tweens together for complex, choreographed animations.

### Basic Sequence Creation

```csharp
public class SequenceExample : MonoBehaviour
{
    void Start()
    {
        Sequence mySequence = DOTween.Sequence();

        // Append adds tweens to the end
        mySequence.Append(transform.DOMoveX(5f, 1f));
        mySequence.Append(transform.DOMoveY(3f, 1f));
        mySequence.Append(transform.DOScale(2f, 0.5f));

        // Add callbacks
        mySequence.OnComplete(() => Debug.Log("Sequence complete!"));
    }
}
```

### Advanced Sequence Methods

```csharp
public class AdvancedSequence : MonoBehaviour
{
    public Transform cube, sphere;

    void Start()
    {
        Sequence seq = DOTween.Sequence();

        // Append: Add to end
        seq.Append(cube.DOMoveX(5f, 1f));

        // Join: Play simultaneously with previous tween
        seq.Join(cube.DORotate(new Vector3(0, 180, 0), 1f));

        // Prepend: Add to beginning (pushes everything forward)
        seq.Prepend(sphere.DOScale(1.5f, 0.5f));

        // Insert: Add at specific time position
        seq.Insert(0.5f, cube.DOScale(2f, 0.5f));

        // AppendInterval: Add delay
        seq.AppendInterval(1f);

        // AppendCallback: Add callback at specific point
        seq.AppendCallback(() => Debug.Log("Middle of sequence"));

        // PrependInterval: Add delay at beginning
        seq.PrependInterval(0.5f);

        // Nest sequences
        Sequence innerSeq = DOTween.Sequence();
        innerSeq.Append(sphere.DOMoveY(3f, 1f));
        innerSeq.Append(sphere.DOMoveY(0f, 1f));
        seq.Append(innerSeq);
    }
}
```

### Sequence with Relative Positioning

```csharp
public class RelativeSequence : MonoBehaviour
{
    void Start()
    {
        Sequence seq = DOTween.Sequence();

        // Use negative insert time for relative positioning
        seq.Append(transform.DOMoveX(5f, 1f));
        seq.Insert(-0.5f, transform.DOMoveY(3f, 1f)); // Starts 0.5s before previous tween ends

        // This creates overlapping animations
    }
}
```

## Settings, Options, and Callbacks

### Chaining Settings

Settings start with "Set" prefix and can be chained together:

```csharp
public class TweenSettings : MonoBehaviour
{
    void Start()
    {
        transform.DOMove(new Vector3(5, 2, 0), 2f)
            .SetEase(Ease.OutBounce)
            .SetLoops(3, LoopType.Yoyo)
            .SetDelay(0.5f)
            .SetAutoKill(false)
            .SetUpdate(UpdateType.Fixed)
            .SetRecyclable(true)
            .SetId("MyTween");
    }
}
```

### Common Settings

#### SetEase

Controls the interpolation curve:

```csharp
// Ease types
transform.DOMove(target, 1f).SetEase(Ease.Linear);
transform.DOMove(target, 1f).SetEase(Ease.InQuad);
transform.DOMove(target, 1f).SetEase(Ease.OutQuad);
transform.DOMove(target, 1f).SetEase(Ease.InOutQuad);
transform.DOMove(target, 1f).SetEase(Ease.InCubic);
transform.DOMove(target, 1f).SetEase(Ease.OutCubic);
transform.DOMove(target, 1f).SetEase(Ease.InOutCubic);
transform.DOMove(target, 1f).SetEase(Ease.InQuart);
transform.DOMove(target, 1f).SetEase(Ease.OutQuart);
transform.DOMove(target, 1f).SetEase(Ease.InOutQuart);
transform.DOMove(target, 1f).SetEase(Ease.InQuint);
transform.DOMove(target, 1f).SetEase(Ease.OutQuint);
transform.DOMove(target, 1f).SetEase(Ease.InOutQuint);
transform.DOMove(target, 1f).SetEase(Ease.InSine);
transform.DOMove(target, 1f).SetEase(Ease.OutSine);
transform.DOMove(target, 1f).SetEase(Ease.InOutSine);
transform.DOMove(target, 1f).SetEase(Ease.InExpo);
transform.DOMove(target, 1f).SetEase(Ease.OutExpo);
transform.DOMove(target, 1f).SetEase(Ease.InOutExpo);
transform.DOMove(target, 1f).SetEase(Ease.InCirc);
transform.DOMove(target, 1f).SetEase(Ease.OutCirc);
transform.DOMove(target, 1f).SetEase(Ease.InOutCirc);
transform.DOMove(target, 1f).SetEase(Ease.InElastic);
transform.DOMove(target, 1f).SetEase(Ease.OutElastic);
transform.DOMove(target, 1f).SetEase(Ease.InOutElastic);
transform.DOMove(target, 1f).SetEase(Ease.InBack);
transform.DOMove(target, 1f).SetEase(Ease.OutBack);
transform.DOMove(target, 1f).SetEase(Ease.InOutBack);
transform.DOMove(target, 1f).SetEase(Ease.InBounce);
transform.DOMove(target, 1f).SetEase(Ease.OutBounce);
transform.DOMove(target, 1f).SetEase(Ease.InOutBounce);
transform.DOMove(target, 1f).SetEase(Ease.Flash); // Flashing effect
transform.DOMove(target, 1f).SetEase(Ease.InFlash);
transform.DOMove(target, 1f).SetEase(Ease.OutFlash);
transform.DOMove(target, 1f).SetEase(Ease.InOutFlash);

// Custom animation curve
transform.DOMove(target, 1f).SetEase(animationCurve);

// Custom ease function
transform.DOMove(target, 1f).SetEase((time, duration, overshootOrAmplitude, period) => {
    return time / duration; // Linear
});
```

#### SetLoops

```csharp
// Loop 3 times
transform.DOMove(target, 1f).SetLoops(3);

// Loop infinitely
transform.DOMove(target, 1f).SetLoops(-1);

// Loop with Yoyo (ping-pong)
transform.DOMove(target, 1f).SetLoops(-1, LoopType.Yoyo);

// Loop with Incremental (adds end value each loop)
transform.DOMoveX(5f, 1f).SetLoops(3, LoopType.Incremental);
// After 3 loops: x = 15 (5 + 5 + 5)
```

#### SetDelay

```csharp
// Delay before starting
transform.DOMove(target, 1f).SetDelay(2f);

// Delay applies to loops too
transform.DOMove(target, 1f).SetDelay(0.5f).SetLoops(3);
```

#### SetUpdate

Controls the update type and timescale independence:

```csharp
// Update during normal Update (default)
transform.DOMove(target, 1f).SetUpdate(UpdateType.Normal);

// Update during LateUpdate
transform.DOMove(target, 1f).SetUpdate(UpdateType.Late);

// Update during FixedUpdate (for physics)
rigidbody.DOMove(target, 1f).SetUpdate(UpdateType.Fixed);

// Independent of Time.timeScale (useful for pause menus)
transform.DOMove(target, 1f).SetUpdate(true);

// Combine update type with timescale independence
transform.DOMove(target, 1f).SetUpdate(UpdateType.Late, true);
```

#### SetId

Assign IDs for easy targeting in control methods:

```csharp
// String ID
transform.DOMove(target, 1f).SetId("PlayerMove");

// Object ID (typically int or enum)
transform.DOMove(target, 1f).SetId(1);

// Later: control by ID
DOTween.Play("PlayerMove");
DOTween.Pause(1);
```

#### SetAutoKill

```csharp
// Auto-kill when complete (default: true)
transform.DOMove(target, 1f).SetAutoKill(true);

// Keep alive after completion (allows rewinding/restarting)
transform.DOMove(target, 1f).SetAutoKill(false);
```

#### SetLink

Link tween lifecycle to a GameObject:

```csharp
// Kill tween when GameObject is destroyed
transform.DOMove(target, 1f).SetLink(gameObject);

// Kill when GameObject is destroyed or disabled
transform.DOMove(target, 1f).SetLink(gameObject, LinkBehaviour.KillOnDisable);

// Pause/resume when GameObject is disabled/enabled
transform.DOMove(target, 1f).SetLink(gameObject, LinkBehaviour.PauseOnDisable);
```

#### SetRelative

```csharp
// Tween relative to current value
transform.DOMove(new Vector3(5, 0, 0), 1f).SetRelative();
// If current position is (10, 0, 0), moves to (15, 0, 0)
```

#### SetSpeedBased

```csharp
// Use duration as speed instead of time
transform.DOMove(target, 5f).SetSpeedBased(true);
// Duration becomes units per second
```

### SetOptions

Some tween types have special options:

```csharp
// Rotation options
transform.DORotate(new Vector3(0, 180, 0), 1f)
    .SetOptions(RotateMode.FastBeyond360); // Don't clamp to 360

// String options
text.DOText("Hello World", 2f)
    .SetOptions(richTextEnabled: true, scrambleMode: ScrambleMode.All);

// Path options
transform.DOPath(path, 2f)
    .SetOptions(lockRotation: AxisConstraint.Y, closePath: true);
```

### Callbacks

Callbacks start with "On" prefix:

```csharp
public class CallbackExample : MonoBehaviour
{
    void Start()
    {
        transform.DOMove(target, 2f)
            .OnStart(() => {
                Debug.Log("Tween started");
            })
            .OnPlay(() => {
                Debug.Log("Tween played");
            })
            .OnUpdate(() => {
                Debug.Log($"Tween updating: {transform.position}");
            })
            .OnStepComplete(() => {
                Debug.Log("Single loop complete");
            })
            .OnComplete(() => {
                Debug.Log("All loops complete");
            })
            .OnPause(() => {
                Debug.Log("Tween paused");
            })
            .OnRewind(() => {
                Debug.Log("Tween rewound");
            })
            .OnKill(() => {
                Debug.Log("Tween killed");
            });
    }
}
```

### Callback Timing

- **OnStart**: Called the first time the tween starts playing, after any delay
- **OnPlay**: Called each time the tween is played (including after pauses)
- **OnUpdate**: Called every frame the tween updates
- **OnStepComplete**: Called each time a loop completes
- **OnComplete**: Called when all loops are complete
- **OnPause**: Called when the tween is paused
- **OnRewind**: Called when the tween is rewound
- **OnKill**: Called when the tween is killed

## Controlling Tweens

### Storing Tween References

```csharp
public class TweenReferences : MonoBehaviour
{
    private Tween myTween;

    void Start()
    {
        // Store reference
        myTween = transform.DOMove(target, 2f);
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            myTween.Kill();
        }
    }
}
```

### Instance Control Methods

Control a specific tween using its reference:

```csharp
public class TweenControl : MonoBehaviour
{
    private Tween tween;

    void Start()
    {
        tween = transform.DOMove(target, 5f)
            .SetAutoKill(false)
            .SetLoops(-1, LoopType.Yoyo);
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.P))
            tween.Play(); // Play from current position

        if (Input.GetKeyDown(KeyCode.Space))
            tween.Pause(); // Pause

        if (Input.GetKeyDown(KeyCode.R))
            tween.Restart(); // Restart from beginning

        if (Input.GetKeyDown(KeyCode.W))
            tween.Rewind(); // Return to beginning without playing

        if (Input.GetKeyDown(KeyCode.C))
            tween.Complete(); // Jump to end

        if (Input.GetKeyDown(KeyCode.K))
            tween.Kill(); // Destroy the tween

        if (Input.GetKeyDown(KeyCode.T))
            tween.TogglePause(); // Toggle pause state

        if (Input.GetKeyDown(KeyCode.F))
            tween.PlayForward(); // Play forward

        if (Input.GetKeyDown(KeyCode.B))
            tween.PlayBackwards(); // Play backward

        if (Input.GetKeyDown(KeyCode.G))
            tween.Goto(2.5f); // Jump to specific time
    }
}
```

### Static Control Methods

Control multiple tweens by target, ID, or all tweens:

```csharp
public class StaticControl : MonoBehaviour
{
    void Start()
    {
        // Control all tweens
        DOTween.PlayAll();
        DOTween.PauseAll();
        DOTween.RestartAll();
        DOTween.RewindAll();
        DOTween.KillAll();

        // Control by target
        DOTween.Play(transform);
        DOTween.Pause(transform);
        DOTween.Kill(transform);

        // Control by ID
        DOTween.Play("MyTweenID");
        DOTween.Pause(1); // Numeric ID
        DOTween.Kill("PlayerAnimation");

        // Complete all tweens
        DOTween.CompleteAll();

        // Complete tweens by target
        DOTween.Complete(transform);

        // Kill tweens by target and optionally complete them first
        DOTween.Kill(transform, complete: true);
    }
}
```

### Filtering Control Methods

Control specific subsets of tweens:

```csharp
public class FilteredControl : MonoBehaviour
{
    void Start()
    {
        // Kill all tweens affecting target's position
        DOTween.Kill(transform, complete: false);

        // Play all tweens with specific ID
        DOTween.Play("GroupID");

        // Pause all tweens on specific target
        DOTween.Pause(transform);
    }
}
```

### Dynamic Tween Modification

```csharp
public class DynamicModification : MonoBehaviour
{
    private Tween tween;

    void Start()
    {
        tween = transform.DOMove(target, 5f)
            .SetAutoKill(false);
    }

    void Update()
    {
        // Change end value dynamically
        if (Input.GetKeyDown(KeyCode.E))
        {
            tween.ChangeEndValue(newTarget, snapStartValue: true);
        }

        // Change duration
        if (Input.GetKeyDown(KeyCode.D))
        {
            tween.timeScale = 2f; // Double speed (instance timeScale)
        }
    }
}
```

## Getting Data from Tweens

### Tween Properties

```csharp
public class TweenData : MonoBehaviour
{
    void Start()
    {
        Tween tween = transform.DOMove(target, 5f)
            .SetLoops(3, LoopType.Yoyo);

        // Check if tween is active
        bool isActive = tween.IsActive();

        // Check if tween is playing
        bool isPlaying = tween.IsPlaying();

        // Check if tween is backwards
        bool isBackwards = tween.IsBackwards();

        // Check if tween is complete
        bool isComplete = tween.IsComplete();

        // Check if timescale independent
        bool isUnscaled = tween.IsTimeScaleIndependent();

        // Get elapsed time
        float elapsed = tween.Elapsed();

        // Get elapsed percentage (0 to 1)
        float percentage = tween.ElapsedPercentage();

        // Get current loop
        int currentLoop = tween.CompletedLoops();

        // Get total duration (including loops)
        float totalDuration = tween.Duration();

        // Get target
        object target = tween.target;

        // Get/set timeScale
        float timeScale = tween.timeScale;
        tween.timeScale = 2f;

        Debug.Log($"Tween data - Active: {isActive}, Playing: {isPlaying}, " +
                  $"Elapsed: {elapsed:F2}s, Progress: {percentage:F2}, Loop: {currentLoop}");
    }
}
```

### Querying Active Tweens

```csharp
public class QueryTweens : MonoBehaviour
{
    void Start()
    {
        // Count all active tweens
        int total = DOTween.TotalPlayingTweens();

        // Check if specific target has tweens
        bool hasTweens = DOTween.IsTweening(transform);

        // Check if specific ID has tweens
        bool hasIDTweens = DOTween.IsTweening("MyTweenID");

        // Count tweens on specific target
        List<Tween> tweensList = DOTween.PlayingTweens();
        int targetTweenCount = tweensList.Count(t => t.target == transform);

        Debug.Log($"Total tweens: {total}, Target has tweens: {hasTweens}");
    }
}
```

## WaitFor Coroutines and Async/Await

### Coroutine Integration

DOTween provides yield instructions for coroutines:

```csharp
public class CoroutineIntegration : MonoBehaviour
{
    void Start()
    {
        StartCoroutine(AnimationSequence());
    }

    IEnumerator AnimationSequence()
    {
        // Wait for tween to complete
        Tween moveTween = transform.DOMove(target1, 2f);
        yield return moveTween.WaitForCompletion();

        Debug.Log("Move complete");

        // Wait for tween to be killed
        Tween scaleTween = transform.DOScale(2f, 1f);
        yield return scaleTween.WaitForKill();

        // Wait for tween to rewind
        Tween rotateTween = transform.DORotate(new Vector3(0, 180, 0), 1f)
            .SetAutoKill(false);
        StartCoroutine(RewindAfterDelay(rotateTween, 2f));
        yield return rotateTween.WaitForRewind();

        // Wait for specific elapsed loops
        Tween loopTween = transform.DOMoveX(5f, 1f).SetLoops(3);
        yield return loopTween.WaitForElapsedLoops(2);
        Debug.Log("2 loops complete");

        // Wait for specific position (time)
        Tween timeTween = transform.DOMoveY(5f, 3f);
        yield return timeTween.WaitForPosition(1.5f);
        Debug.Log("1.5 seconds elapsed");

        // Wait for specific time (in seconds)
        yield return transform.DOMove(target2, 2f).WaitForElapsedLoops(1);

        Debug.Log("Animation sequence complete");
    }

    IEnumerator RewindAfterDelay(Tween tween, float delay)
    {
        yield return new WaitForSeconds(delay);
        tween.Rewind();
    }
}
```

### Async/Await Support (Unity 2021+)

```csharp
using System.Threading.Tasks;
using DG.Tweening;

public class AsyncAwaitTweening : MonoBehaviour
{
    async void Start()
    {
        await AnimateSequenceAsync();
    }

    async Task AnimateSequenceAsync()
    {
        // Wait for tween completion using async/await
        await transform.DOMove(target1, 2f).AsyncWaitForCompletion();

        Debug.Log("Move complete");

        // Chain multiple animations
        await transform.DORotate(new Vector3(0, 180, 0), 1f).AsyncWaitForCompletion();
        await transform.DOScale(2f, 1f).AsyncWaitForCompletion();

        Debug.Log("All animations complete");
    }

    // Combining multiple animations
    async Task ParallelAnimations()
    {
        Task move = transform.DOMove(target1, 2f).AsyncWaitForCompletion();
        Task rotate = transform.DORotate(new Vector3(0, 180, 0), 2f).AsyncWaitForCompletion();
        Task scale = transform.DOScale(2f, 2f).AsyncWaitForCompletion();

        // Wait for all to complete
        await Task.WhenAll(move, rotate, scale);

        Debug.Log("All parallel animations complete");
    }
}
```

### Cancellation Token Support

```csharp
using System.Threading;
using System.Threading.Tasks;

public class CancellationExample : MonoBehaviour
{
    private CancellationTokenSource cts;

    void Start()
    {
        cts = new CancellationTokenSource();
        _ = AnimateWithCancellation(cts.Token);
    }

    void OnDestroy()
    {
        cts?.Cancel();
        cts?.Dispose();
    }

    async Task AnimateWithCancellation(CancellationToken token)
    {
        try
        {
            await transform.DOMove(target, 5f)
                .AsyncWaitForCompletion()
                .WithCancellation(token);
        }
        catch (OperationCanceledException)
        {
            Debug.Log("Animation cancelled");
        }
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.C))
        {
            cts.Cancel();
        }
    }
}
```

## Additional Methods and Utilities

### Blendable Tweens

Create multiple tweens on the same property that blend together:

```csharp
public class BlendableTweens : MonoBehaviour
{
    void Start()
    {
        // Multiple position tweens that blend
        transform.DOBlendableMoveBy(Vector3.right * 3, 2f);
        transform.DOBlendableMoveBy(Vector3.up * 2, 1.5f);

        // Multiple rotation tweens that blend
        transform.DOBlendableRotateBy(new Vector3(0, 180, 0), 2f);
        transform.DOBlendableRotateBy(new Vector3(45, 0, 0), 1f);

        // Multiple scale tweens that blend
        transform.DOBlendableScaleBy(Vector3.one * 0.5f, 1f);
    }
}
```

### Delayed Calls

```csharp
public class DelayedCalls : MonoBehaviour
{
    void Start()
    {
        // Simple delayed call
        DOVirtual.DelayedCall(2f, () => {
            Debug.Log("Called after 2 seconds");
        });

        // Delayed call with ID and settings
        DOVirtual.DelayedCall(3f, () => {
            Debug.Log("Called after 3 seconds (unscaled)");
        }).SetUpdate(true).SetId("MyDelay");
    }
}
```

### Text Tweening (with TextMesh Pro)

```csharp
using TMPro;

public class TextTweening : MonoBehaviour
{
    public TextMeshProUGUI tmpText;

    void Start()
    {
        // Animate text characters appearing
        tmpText.DOText("Hello World!", 2f);

        // With scramble effect
        tmpText.DOText("Secret Message", 3f)
            .SetOptions(scrambleMode: ScrambleMode.All);

        // Fade text
        tmpText.DOFade(0f, 1f);

        // Color text
        tmpText.DOColor(Color.red, 1f);
    }
}
```

### UI Tweening

```csharp
using UnityEngine.UI;

public class UITweening : MonoBehaviour
{
    public Image image;
    public CanvasGroup canvasGroup;
    public RectTransform rectTransform;

    void Start()
    {
        // Image tweening
        image.DOFade(0f, 1f);
        image.DOColor(Color.blue, 1f);
        image.DOFillAmount(1f, 2f); // For filled images

        // CanvasGroup fade
        canvasGroup.DOFade(0f, 1f);

        // RectTransform tweening
        rectTransform.DOAnchorPos(new Vector2(100, 100), 1f);
        rectTransform.DOAnchorPosX(200f, 1f);
        rectTransform.DOSizeDelta(new Vector2(200, 200), 1f);
        rectTransform.DOPunchAnchorPos(Vector2.up * 50, 1f);
    }
}
```

### AudioSource Tweening

```csharp
public class AudioTweening : MonoBehaviour
{
    public AudioSource audioSource;

    void Start()
    {
        // Fade volume
        audioSource.DOFade(0f, 2f);

        // Change pitch
        audioSource.DOPitch(2f, 1f);

        // Fade in with callback
        audioSource.volume = 0;
        audioSource.Play();
        audioSource.DOFade(1f, 1f);
    }
}
```

### Light Tweening

```csharp
public class LightTweening : MonoBehaviour
{
    public Light lightComponent;

    void Start()
    {
        // Intensity
        lightComponent.DOIntensity(2f, 1f);

        // Color
        lightComponent.DOColor(Color.red, 1f);

        // Blinking effect
        Sequence blink = DOTween.Sequence();
        blink.Append(lightComponent.DOIntensity(0f, 0.1f));
        blink.Append(lightComponent.DOIntensity(1f, 0.1f));
        blink.SetLoops(-1);
    }
}
```

### LineRenderer Tweening (DOTween Pro)

```csharp
public class LineRendererTweening : MonoBehaviour
{
    public LineRenderer lineRenderer;

    void Start()
    {
        // Animate line color
        lineRenderer.DOColor(
            new Color2(Color.red, Color.blue),
            new Color2(Color.green, Color.yellow),
            1f
        );
    }
}
```

## Editor Methods and Components

### DOTweenAnimation Component

DOTween Pro includes a visual editor component that allows creating tweens without code.

#### Adding DOTweenAnimation

1. Select a GameObject in the Hierarchy
2. Click `Add Component` in the Inspector
3. Search for and add `DOTween Animation`
4. Configure the animation settings in the Inspector

#### DOTweenAnimation Settings

- **Animation Type**: Choose from dozens of tween types (Move, Rotate, Scale, Fade, etc.)
- **Duration**: Set animation duration
- **Ease**: Select easing curve from dropdown
- **Loops**: Configure loop count and type
- **Delay**: Set initial delay
- **Auto Play**: Choose when the animation starts
  - `None`: Don't auto-play
  - `OnEnable`: Play when GameObject is enabled
  - `OnStart`: Play on Start()
  - `OnAwake`: Play on Awake()
- **Auto Kill**: Whether to auto-kill on completion

#### Controlling DOTweenAnimation from Code

```csharp
using DG.Tweening;

public class DOTweenAnimationControl : MonoBehaviour
{
    public DOTweenAnimation dotweenAnim;

    void Start()
    {
        // Get component
        dotweenAnim = GetComponent<DOTweenAnimation>();

        // Control the animation
        dotweenAnim.DOPlay(); // Play
        dotweenAnim.DOPause(); // Pause
        dotweenAnim.DORewind(); // Rewind
        dotweenAnim.DORestart(); // Restart
        dotweenAnim.DOComplete(); // Complete
        dotweenAnim.DOKill(); // Kill

        // Access the underlying tween
        Tween tween = dotweenAnim.tween;
    }
}
```

### DOTweenPath Component

Visual path editor for creating movement paths in the Scene view.

#### Adding DOTweenPath

1. Select a GameObject
2. Add Component > `DOTween Path`
3. Configure path settings in Inspector
4. Edit path waypoints in Scene view

#### DOTweenPath Settings

- **Path Type**: Linear, CatmullRom, or CubicBezier
- **Duration**: Time to traverse path
- **Ease**: Easing curve
- **Loops**: Loop configuration
- **Path Mode**: Full3D, TopDown2D, or Sidescroller2D
- **Close Path**: Whether to close the path (loop back to start)
- **Lock Rotation**: Lock specific axes during path movement
- **Look At**: Make object look along path direction

#### Editing Paths in Scene View

- Click waypoints to select
- Drag waypoints to reposition
- Use the Inspector buttons:
  - `Add Waypoint`: Add new waypoint at end
  - `Remove Selected`: Delete selected waypoint
  - `Reset Path`: Clear all waypoints

#### Controlling DOTweenPath from Code

```csharp
using DG.Tweening;

public class DOTweenPathControl : MonoBehaviour
{
    public DOTweenPath dotweenPath;

    void Start()
    {
        // Get component
        dotweenPath = GetComponent<DOTweenPath>();

        // Get path array
        Vector3[] path = dotweenPath.wps;

        // Create tween from path
        dotweenPath.DOPlay();
        dotweenPath.DOPause();
        dotweenPath.DORestart();

        // Get underlying path tween
        Tween pathTween = dotweenPath.GetTween();
    }
}
```

### DOTweenVisualManager

Allows executing actions when a GameObject is enabled/disabled.

#### Adding DOTweenVisualManager

1. Select a GameObject with DOTweenAnimation or DOTweenPath
2. In the component Inspector, click `Add Manager` button
3. Configure On Enable and On Disable actions

#### Available Actions

- **Play**: Play all tweens on GameObject
- **Pause**: Pause all tweens
- **Rewind**: Rewind all tweens
- **Restart**: Restart all tweens
- **Complete**: Complete all tweens
- **Kill**: Kill all tweens

### DOTweenInspector

The DOTween Utility Panel provides project-wide settings and utilities.

#### Opening the Utility Panel

`Tools > Demigiant > DOTween Utility Panel`

#### Utility Panel Features

**Setup**
- `Setup DOTween`: Configure DOTween for your Unity version
- `Check Updates`: Check for DOTween updates

**Preferences**
- Default settings for all tweens
- Safe mode toggle
- Log behavior settings
- Capacity presets

**Tools**
- `Validate`: Check project setup
- `Clear Saved Preferences`: Reset to defaults

### Debugging in Editor

```csharp
public class DebugTweens : MonoBehaviour
{
    void Start()
    {
        // Enable debug mode
        DOTween.debugMode = true;

        // This logs all tween operations
        transform.DOMove(target, 2f);

        // Disable for production
        DOTween.debugMode = false;
    }

    void Update()
    {
        // Display tween count in Editor
        if (Application.isEditor)
        {
            int activeTweens = DOTween.TotalPlayingTweens();
            Debug.Log($"Active tweens: {activeTweens}");
        }
    }
}
```

## Best Practices and Performance

### Memory Management

```csharp
public class MemoryManagement : MonoBehaviour
{
    private Tween tween;

    void Start()
    {
        // Set capacity upfront for better performance
        DOTween.SetCapacity(500, 50);

        // Use SetLink to auto-kill on destroy
        tween = transform.DOMove(target, 5f)
            .SetLink(gameObject);
    }

    void OnDisable()
    {
        // Kill tweens when disabled
        DOTween.Kill(transform);
    }

    void OnDestroy()
    {
        // Kill tweens when destroyed (if not using SetLink)
        tween?.Kill();
    }
}
```

### Optimization Tips

1. **Set Capacity**: Initialize with `DOTween.SetCapacity()` to prevent runtime allocations
2. **Use SetLink**: Automatically manage tween lifecycle with GameObject
3. **Recycle Tweens**: Enable recycling with `SetRecyclable(true)` for frequently created tweens
4. **Avoid OnUpdate**: Use only when necessary, as it's called every frame
5. **Use IDs**: Group and control multiple tweens efficiently with IDs
6. **Kill Inactive Tweens**: Clean up tweens that are no longer needed
7. **Use SetAutoKill**: Let completed tweens auto-kill to free resources

### Common Patterns

```csharp
public class CommonPatterns : MonoBehaviour
{
    // Fade in/out pattern
    IEnumerator FadeInOut(CanvasGroup group)
    {
        yield return group.DOFade(1f, 0.5f).WaitForCompletion();
        yield return new WaitForSeconds(2f);
        yield return group.DOFade(0f, 0.5f).WaitForCompletion();
    }

    // Button press effect
    public void OnButtonPress(Transform button)
    {
        Sequence seq = DOTween.Sequence();
        seq.Append(button.DOScale(0.9f, 0.1f));
        seq.Append(button.DOScale(1f, 0.1f));
    }

    // Floating animation
    public void FloatAnimation(Transform obj)
    {
        obj.DOMoveY(obj.position.y + 1f, 1f)
            .SetEase(Ease.InOutSine)
            .SetLoops(-1, LoopType.Yoyo);
    }

    // Pulse effect
    public void PulseEffect(Transform obj)
    {
        obj.DOScale(1.2f, 0.5f)
            .SetEase(Ease.OutQuad)
            .SetLoops(-1, LoopType.Yoyo);
    }
}
```

## Resources

For comprehensive API documentation and additional information, refer to:

### References Directory

- `references/api_reference.md` - Detailed API class references
- `references/shortcuts.md` - Complete list of shortcut extensions
- `references/ease_types.md` - Visual guide to all ease types

### Assets Directory

- `assets/templates/` - Ready-to-use tween scripts and examples
- `assets/examples/` - Complete scene examples demonstrating features

### External Resources

- Official Documentation: https://dotween.demigiant.com/documentation.php
- API Reference: http://dotween.demigiant.com/api/
- Support Forum: https://dotween.demigiant.com/support.php
- Getting Started: https://dotween.demigiant.com/getstarted.php

## Implementation Workflow

When implementing DOTween features:

1. **Initialize**: Set up DOTween in your project's initialization script
2. **Plan**: Determine what properties need animation and create tweens/sequences
3. **Configure**: Apply appropriate settings (ease, loops, delays, callbacks)
4. **Control**: Implement play/pause/control logic as needed
5. **Integrate**: Connect with coroutines or async/await for complex sequences
6. **Test**: Verify animations in various scenarios and edge cases
7. **Optimize**: Use SetLink, SetCapacity, and proper cleanup for performance
8. **Polish**: Fine-tune easing curves and timing for best feel

Always consider the tween lifecycle and clean up appropriately to prevent memory leaks.
