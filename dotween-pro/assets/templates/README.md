# DOTween Templates

This directory contains ready-to-use C# script templates for common DOTween use cases.

## Available Templates

### DOTweenManager.cs
A singleton-style manager for initializing and globally controlling DOTween.

**Features:**
- Centralized DOTween initialization with custom settings
- Global pause/resume functionality
- Debug information display
- Automatic cleanup on application quit

**Usage:**
1. Create an empty GameObject in your first scene
2. Attach the `DOTweenManager` component
3. Configure settings in the Inspector
4. The manager will automatically initialize DOTween on Awake

### UIAnimations.cs
Common UI animation patterns for game interfaces.

**Features:**
- Fade in/out animations
- Slide transitions (from all directions)
- Scale effects (pop in/out)
- Button press effects
- Pulse animations
- Shake effects
- Color flash effects
- Complete intro/outro sequences

**Usage:**
1. Attach to any UI element (Panel, Button, etc.)
2. Ensure the GameObject has required components (CanvasGroup, RectTransform, Image)
3. Call animation methods from buttons, code, or events
4. Customize durations and easing in the Inspector

**Example:**
```csharp
UIAnimations uiAnim = GetComponent<UIAnimations>();
uiAnim.Show(); // Fade in and enable interaction
uiAnim.ScaleIn(); // Pop in effect
uiAnim.PlayIntroSequence(); // Complete entrance animation
```

### GameplayAnimations.cs
Gameplay-related animation patterns for game objects.

**Features:**
- Movement animations (move, jump, follow path)
- Patrol behaviors
- Circle movement
- Hit reactions
- Death animations
- Spawn/appear effects
- Floating/hovering idle animations
- Continuous rotation
- Shake effects
- Camera shake
- Collect item animations

**Usage:**
1. Attach to any GameObject that needs animations
2. Call animation methods from game logic
3. Customize parameters for your specific needs

**Example:**
```csharp
GameplayAnimations anim = GetComponent<GameplayAnimations>();
anim.MoveTo(targetPosition); // Move to position
anim.JumpTo(targetPosition, jumpPower: 3f); // Jump to position
anim.HitReaction(Vector3.back); // React to hit
anim.StartFloating(); // Begin floating animation
```

## Integration Tips

### Combining Templates
These templates can work together in your project:

```csharp
// Pause all animations when opening pause menu
DOTweenManager.Instance.PauseAllTweens();

// Animate UI panel appearing
UIAnimations panelAnim = pausePanel.GetComponent<UIAnimations>();
panelAnim.Show();
```

### Extending Templates
Feel free to extend these templates with your own methods:

```csharp
public class MyUIAnimations : UIAnimations
{
    public void CustomAnimation()
    {
        // Add your custom animation here
        rectTransform.DORotate(Vector3.forward * 360f, 1f, RotateMode.FastBeyond360);
    }
}
```

### Memory Management
All templates include proper cleanup in `OnDestroy()`:

```csharp
void OnDestroy()
{
    // Kill all tweens on this object
    DOTween.Kill(transform);
}
```

## Best Practices

1. **Use SetLink()** for automatic cleanup:
   ```csharp
   transform.DOMove(target, 1f).SetLink(gameObject);
   ```

2. **Store tween references** when you need to control them:
   ```csharp
   private Tween myTween;
   myTween = transform.DOMove(target, 1f);
   // Later: myTween.Kill()
   ```

3. **Use IDs** for grouped control:
   ```csharp
   transform.DOMove(target, 1f).SetId("PlayerMovement");
   // Control all tweens with this ID
   DOTween.Kill("PlayerMovement");
   ```

4. **Set capacity** during initialization:
   ```csharp
   DOTween.Init().SetCapacity(200, 50);
   ```

5. **Use coroutines or async/await** for sequential animations:
   ```csharp
   IEnumerator AnimateSequence()
   {
       yield return transform.DOMove(pos1, 1f).WaitForCompletion();
       yield return transform.DOMove(pos2, 1f).WaitForCompletion();
   }
   ```

## Additional Resources

- Main skill documentation: `../SKILL.md`
- API Reference: `../references/api_reference.md`
- Official DOTween documentation: https://dotween.demigiant.com/documentation.php
