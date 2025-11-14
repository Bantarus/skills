# DOTween API Reference

This document provides detailed API class references for DOTween and DOTween Pro.

## Core Classes

### DOTween Class

The main static class for DOTween initialization and global control.

#### Initialization Methods

```csharp
// Initialize with default settings
DOTween.Init()

// Initialize with custom settings
DOTween.Init(bool useSafeMode, LogBehaviour logBehaviour)

// Set capacity for tweeners and sequences
DOTween.SetCapacity(int tweenersCapacity, int sequencesCapacity)
```

#### Global Control Methods

```csharp
// Play all tweens
int DOTween.PlayAll()

// Play tweens by target
int DOTween.Play(object targetOrId)

// Play tweens by ID
int DOTween.Play(string id)

// Pause all tweens
int DOTween.PauseAll()

// Pause tweens by target
int DOTween.Pause(object targetOrId)

// Kill all tweens
int DOTween.KillAll()

// Kill tweens by target
int DOTween.Kill(object targetOrId, bool complete = false)

// Restart all tweens
int DOTween.RestartAll()

// Rewind all tweens
int DOTween.RewindAll()

// Complete all tweens
int DOTween.CompleteAll()

// Complete tweens by target
int DOTween.Complete(object targetOrId)
```

#### Query Methods

```csharp
// Check if target has active tweens
bool DOTween.IsTweening(object targetOrId)

// Get total number of active tweens
int DOTween.TotalPlayingTweens()

// Get list of all playing tweens
List<Tween> DOTween.PlayingTweens()

// Validate tween
bool DOTween.Validate()
```

#### Global Settings

```csharp
// Global timescale
DOTween.timeScale = 1.0f;

// Timescale for unscaled tweens only
DOTween.unscaledTimeScale = 1.0f;

// Default ease type
DOTween.defaultEaseType = Ease.OutQuad;

// Enable safe mode globally
DOTween.useSafeMode = false;

// Debug mode (logs all tween operations)
DOTween.debugMode = false;

// Max smoothness for path resolution
DOTween.maxSmoothness = 300;

// Default update type
DOTween.defaultUpdateType = UpdateType.Normal;

// Default auto-kill behavior
DOTween.defaultAutoKill = true;

// Default auto-play behavior
DOTween.defaultAutoPlay = AutoPlay.All;
```

#### Sequence Creation

```csharp
// Create a new sequence
Sequence DOTween.Sequence()
```

#### Clear Methods

```csharp
// Clear cached tweens
DOTween.Clear()

// Clear cached tweens and reset to default
DOTween.Clear(bool destroy)
```

---

## Tween Class

Base class for all tweens (Tweeners and Sequences).

### Properties

```csharp
// Target object
object target { get; }

// Tween ID
object id { get; set; }

// Time scale for this tween
float timeScale { get; set; }

// Duration of single loop (excluding loops)
float duration { get; }

// Total loops
int loops { get; }

// Loop type
LoopType loopType { get; }

// Delay before starting
float delay { get; }

// Is tween active
bool active { get; }

// Is tween playing
bool isPlaying { get; }

// Is tween playing backwards
bool isBackwards { get; }

// Is tween complete
bool isComplete { get; }

// Ease type
Ease easeType { get; }

// Update type
UpdateType updateType { get; }
```

### Methods

```csharp
// Play tween
Tween Play()

// Pause tween
Tween Pause()

// Kill tween
void Kill(bool complete = false)

// Restart tween
Tween Restart(bool includeDelay = true)

// Rewind tween
Tween Rewind(bool includeDelay = true)

// Complete tween
Tween Complete(bool withCallbacks = false)

// Toggle pause
Tween TogglePause()

// Play forward
Tween PlayForward()

// Play backwards
Tween PlayBackwards()

// Go to specific time position
Tween Goto(float to, bool andPlay = false)

// Get elapsed time
float Elapsed(bool includeLoops = true)

// Get elapsed percentage (0-1)
float ElapsedPercentage(bool includeLoops = true)

// Get elapsed directional percentage (-1 to 1)
float ElapsedDirectionalPercentage()

// Get completed loops
int CompletedLoops()

// Duration including loops
float Duration(bool includeLoops = true)

// Is active
bool IsActive()

// Is playing
bool IsPlaying()

// Is backwards
bool IsBackwards()

// Is complete
bool IsComplete()

// Is initialized
bool IsInitialized()

// Is timescale independent
bool IsTimeScaleIndependent()
```

---

## TweenSettingsExtensions Class

Extension methods for configuring tween settings.

### Settings Methods

```csharp
// Set ease type
T SetEase<T>(this T tween, Ease ease) where T : Tween

// Set ease with AnimationCurve
T SetEase<T>(this T tween, AnimationCurve animCurve) where T : Tween

// Set ease with custom function
T SetEase<T>(this T tween, EaseFunction customEase) where T : Tween

// Set loops
T SetLoops<T>(this T tween, int loops, LoopType loopType = LoopType.Restart) where T : Tween

// Set delay
T SetDelay<T>(this T tween, float delay) where T : Tween

// Set relative
T SetRelative<T>(this T tween, bool isRelative = true) where T : Tween

// Set speed based
T SetSpeedBased<T>(this T tween, bool isSpeedBased = true) where T : Tween

// Set update type
T SetUpdate<T>(this T tween, UpdateType updateType, bool isIndependentUpdate = false) where T : Tween

// Set update (timescale independent only)
T SetUpdate<T>(this T tween, bool isIndependentUpdate) where T : Tween

// Set auto-kill
T SetAutoKill<T>(this T tween, bool autoKillOnComplete = true) where T : Tween

// Set ID
T SetId<T>(this T tween, object id) where T : Tween

// Set target
T SetTarget<T>(this T tween, object target) where T : Tween

// Set link
T SetLink<T>(this T tween, GameObject gameObject, LinkBehaviour linkBehaviour = LinkBehaviour.KillOnDestroy) where T : Tween

// Set recyclable
T SetRecyclable<T>(this T tween, bool recyclable = true) where T : Tween

// Set inverted
T SetInverted<T>(this T tween, bool isInverted = true) where T : Tween
```

### Callback Methods

```csharp
// On start callback
T OnStart<T>(this T tween, TweenCallback callback) where T : Tween

// On play callback
T OnPlay<T>(this T tween, TweenCallback callback) where T : Tween

// On pause callback
T OnPause<T>(this T tween, TweenCallback callback) where T : Tween

// On rewind callback
T OnRewind<T>(this T tween, TweenCallback callback) where T : Tween

// On update callback
T OnUpdate<T>(this T tween, TweenCallback callback) where T : Tween

// On step complete callback (called each loop)
T OnStepComplete<T>(this T tween, TweenCallback callback) where T : Tween

// On complete callback (called after all loops)
T OnComplete<T>(this T tween, TweenCallback callback) where T : Tween

// On kill callback
T OnKill<T>(this T tween, TweenCallback callback) where T : Tween

// On waypoint change callback (for path tweens)
T OnWaypointChange<T>(this T tween, TweenCallback<int> callback) where T : Tween
```

---

## TweenExtensions Class

Extension methods for controlling tweens.

### Control Methods

```csharp
// Play tween
T Play<T>(this T t) where T : Tween

// Pause tween
T Pause<T>(this T t) where T : Tween

// Kill tween
void Kill<T>(this T t, bool complete = false) where T : Tween

// Restart tween
T Restart<T>(this T t, bool includeDelay = true, float changeDelayTo = -1) where T : Tween

// Rewind tween
T Rewind<T>(this T t, bool includeDelay = true) where T : Tween

// Complete tween
T Complete<T>(this T t, bool withCallbacks = false) where T : Tween

// Flip tween direction
T Flip<T>(this T t) where T : Tween

// Go to time position
T Goto<T>(this T t, float to, bool andPlay = false) where T : Tween

// Toggle pause
T TogglePause<T>(this T t) where T : Tween

// Play forward
T PlayForward<T>(this T t) where T : Tween

// Play backwards
T PlayBackwards<T>(this T t) where T : Tween

// Smooth rewind
T SmoothRewind<T>(this T t) where T : Tween
```

### Modification Methods

```csharp
// Change end value
T ChangeEndValue<T>(this T t, object newEndValue, bool snapStartValue = false) where T : Tween

// Change end value with duration
T ChangeEndValue<T>(this T t, object newEndValue, float newDuration, bool snapStartValue = false) where T : Tween

// Change start value
T ChangeStartValue<T>(this T t, object newStartValue) where T : Tween

// Change values
T ChangeValues<T>(this T t, object newStartValue, object newEndValue, float newDuration = -1) where T : Tween
```

### Wait Methods (for Coroutines)

```csharp
// Wait for completion
YieldInstruction WaitForCompletion(this Tween t)

// Wait for kill
YieldInstruction WaitForKill(this Tween t)

// Wait for rewind
YieldInstruction WaitForRewind(this Tween t)

// Wait for elapsed loops
YieldInstruction WaitForElapsedLoops(this Tween t, int elapsedLoops)

// Wait for position (time)
YieldInstruction WaitForPosition(this Tween t, float position)

// Wait for start
YieldInstruction WaitForStart(this Tween t)
```

### Async Methods (Unity 2021+)

```csharp
// Async wait for completion
Task AsyncWaitForCompletion(this Tween t)

// Async wait for kill
Task AsyncWaitForKill(this Tween t)

// Async wait for rewind
Task AsyncWaitForRewind(this Tween t)

// Async wait for elapsed loops
Task AsyncWaitForElapsedLoops(this Tween t, int elapsedLoops)

// Async wait for position
Task AsyncWaitForPosition(this Tween t, float position)

// Async wait for start
Task AsyncWaitForStart(this Tween t)
```

---

## Sequence Class

Container for grouping tweens.

### Methods

```csharp
// Append tween to end
Sequence Append(Tween tween)

// Prepend tween to beginning
Sequence Prepend(Tween tween)

// Join tween (play with previous)
Sequence Join(Tween tween)

// Insert tween at specific time
Sequence Insert(float atPosition, Tween tween)

// Append interval (delay)
Sequence AppendInterval(float interval)

// Prepend interval
Sequence PrependInterval(float interval)

// Append callback
Sequence AppendCallback(TweenCallback callback)

// Prepend callback
Sequence PrependCallback(TweenCallback callback)

// Insert callback
Sequence InsertCallback(float atPosition, TweenCallback callback)
```

---

## DOVirtual Class

Static class for virtual property tweening and delayed calls.

### Float Tweening

```csharp
// Tween float value
Tweener DOVirtual.Float(float from, float to, float duration, TweenCallback<float> onVirtualUpdate)
```

### Color Tweening

```csharp
// Tween color value
Tweener DOVirtual.Color(Color from, Color to, float duration, TweenCallback<Color> onVirtualUpdate)
```

### Vector Tweening

```csharp
// Tween Vector2
Tweener DOVirtual.Vector2(Vector2 from, Vector2 to, float duration, TweenCallback<Vector2> onVirtualUpdate)

// Tween Vector3
Tweener DOVirtual.Vector3(Vector3 from, Vector3 to, float duration, TweenCallback<Vector3> onVirtualUpdate)

// Tween Vector4
Tweener DOVirtual.Vector4(Vector4 from, Vector4 to, float duration, TweenCallback<Vector4> onVirtualUpdate)
```

### Delayed Calls

```csharp
// Delayed call
Tween DOVirtual.DelayedCall(float delay, TweenCallback callback, bool ignoreTimeScale = false)
```

### Easing

```csharp
// Evaluate ease curve
float DOVirtual.EasedValue(float from, float to, float elapsed, float duration, Ease easeType)

// Evaluate ease curve with overshoot/amplitude and period
float DOVirtual.EasedValue(float from, float to, float elapsed, float duration, Ease easeType, float overshoot, float period)

// Evaluate ease curve with AnimationCurve
float DOVirtual.EasedValue(float from, float to, float elapsed, float duration, AnimationCurve easeCurve)
```

---

## Enumerations

### Ease

Easing curve types:

```csharp
enum Ease
{
    Unset,
    Linear,
    InSine, OutSine, InOutSine,
    InQuad, OutQuad, InOutQuad,
    InCubic, OutCubic, InOutCubic,
    InQuart, OutQuart, InOutQuart,
    InQuint, OutQuint, InOutQuint,
    InExpo, OutExpo, InOutExpo,
    InCirc, OutCirc, InOutCirc,
    InElastic, OutElastic, InOutElastic,
    InBack, OutBack, InOutBack,
    InBounce, OutBounce, InOutBounce,
    InFlash, OutFlash, InOutFlash,
    Flash
}
```

### UpdateType

When the tween should update:

```csharp
enum UpdateType
{
    Normal,      // During Update
    Late,        // During LateUpdate
    Fixed,       // During FixedUpdate
    Manual       // Manual update only
}
```

### LoopType

How the tween should loop:

```csharp
enum LoopType
{
    Restart,     // Restart from beginning
    Yoyo,        // Ping-pong back and forth
    Incremental  // Add end value each loop
}
```

### PathType

Type of path interpolation:

```csharp
enum PathType
{
    Linear,       // Straight lines between waypoints
    CatmullRom,   // Smooth curved path
    CubicBezier   // Bezier curves with control points
}
```

### PathMode

Orientation for path movement:

```csharp
enum PathMode
{
    Full3D,        // Full 3D movement
    TopDown2D,     // 2D top-down (XZ plane)
    Sidescroller2D // 2D sidescroller (XY plane)
}
```

### RotateMode

How rotation should be calculated:

```csharp
enum RotateMode
{
    Fast,             // Shortest rotation
    FastBeyond360,    // Shortest rotation, no 360 clamping
    WorldAxisAdd,     // Add to current rotation (world axis)
    LocalAxisAdd      // Add to current rotation (local axis)
}
```

### AxisConstraint

Lock specific axes:

```csharp
[Flags]
enum AxisConstraint
{
    None = 0,
    X = 1,
    Y = 2,
    Z = 4,
    W = 8
}
```

### ScrambleMode

Text scrambling modes:

```csharp
enum ScrambleMode
{
    None,
    All,
    Uppercase,
    Lowercase,
    Numerals,
    Custom
}
```

### LinkBehaviour

How tweens should link to GameObjects:

```csharp
enum LinkBehaviour
{
    KillOnDestroy,        // Kill tween when GameObject destroyed
    KillOnDisable,        // Kill when destroyed or disabled
    PauseOnDisable,       // Pause when disabled, resume when enabled
    PauseOnDisablePlayOnEnable,
    PauseOnDisableRestartOnEnable,
    CompleteOnDisable,
    CompleteAndKillOnDisable,
    RestartOnEnable
}
```

### LogBehaviour

Logging behavior:

```csharp
enum LogBehaviour
{
    Default,      // Errors and warnings
    Verbose,      // Everything
    ErrorsOnly    // Only errors
}
```

### AutoPlay

Auto-play behavior:

```csharp
enum AutoPlay
{
    None,
    All,
    AutoPlaySequences,
    AutoPlayTweeners
}
```

---

## Performance Considerations

### Memory Pooling

DOTween automatically pools tweens for reuse. Configure pooling:

```csharp
// Set capacity (recommended during initialization)
DOTween.SetCapacity(200, 50);

// Enable/disable recycling
tween.SetRecyclable(true);
```

### Safe Mode

Safe mode provides extra safety checks but has slight performance cost:

```csharp
// Enable globally
DOTween.Init(useSafeMode: true);

// Or per tween with SetLink
tween.SetLink(gameObject, LinkBehaviour.KillOnDestroy);
```

### Update Optimization

Choose appropriate update type:

```csharp
// Use Normal for most tweens
tween.SetUpdate(UpdateType.Normal);

// Use Late for camera follow
tween.SetUpdate(UpdateType.Late);

// Use Fixed for physics
tween.SetUpdate(UpdateType.Fixed);
```

### Callback Optimization

Avoid heavy operations in OnUpdate:

```csharp
// BAD: Heavy operation every frame
tween.OnUpdate(() => {
    DoExpensiveCalculation();
});

// GOOD: Only on completion
tween.OnComplete(() => {
    DoExpensiveCalculation();
});
```

---

## Version Information

This documentation is based on DOTween for Unity 6.2. For the latest version information and updates, visit:

- Official Documentation: https://dotween.demigiant.com/documentation.php
- API Reference: http://dotween.demigiant.com/api/
- Changelog: https://dotween.demigiant.com/download.php
