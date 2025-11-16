---
name: flutter-explicit-animations
description: Comprehensive guide for implementing explicit animations in Flutter using AnimationController, Tween, and CurvedAnimation. This skill should be used when creating custom animations, complex motion sequences, coordinated multi-property animations, or any animation requiring precise timing control. Covers AnimationController lifecycle, Tween configuration, Material Motion 3 curves, AnimatedBuilder optimization, and advanced animation patterns.
---

# Flutter Explicit Animations and Motion

## Overview

Explicit animations in Flutter provide full programmatic control over animation timing, curves, and behavior. Unlike implicit animations (AnimatedContainer, AnimatedOpacity), explicit animations require manual setup and management, offering the precision needed for complex motion, custom effects, and choreographed sequences.

**Core Components:**
- **AnimationController** - Manages animation timeline and playback
- **Animation<T>** - Abstract animation value producer
- **Tween<T>** - Defines value range (begin to end)
- **CurvedAnimation** - Applies easing curves
- **AnimatedBuilder** - Efficient widget rebuilding for animations

**Version Compatibility:**
- Available in all Flutter versions
- Updated for Material Motion 3 (Flutter 3.16+)
- Documentation reflects Flutter 3.38.0 (updated October 28, 2025)

**Official Resources:**
- Animations Tutorial: https://docs.flutter.dev/ui/animations/tutorial
- Animations Overview: https://docs.flutter.dev/ui/animations/overview
- API Reference: https://api.flutter.dev/flutter/animation/

**Use Cases:**
- Custom widget transitions
- Complex multi-property animations
- Coordinated animation sequences
- Custom progress indicators
- Page transitions and navigation animations
- Interactive gestures with animation
- Physics-based motion (springs, friction)

## Core Concepts

### 1. Animation Architecture

**Animation Flow:**

```
AnimationController (timeline)
    ↓
Tween (value range)
    ↓
CurvedAnimation (easing)
    ↓
Animation<T> (current value)
    ↓
Widget (consumes value)
```

### 2. AnimationController Lifecycle

#### Basic Setup

```dart
import 'package:flutter/material.dart';

class AnimatedWidget extends StatefulWidget {
  @override
  _AnimatedWidgetState createState() => _AnimatedWidgetState();
}

class _AnimatedWidgetState extends State<AnimatedWidget>
    with SingleTickerProviderStateMixin { // Required for vsync
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();

    // Create controller
    _controller = AnimationController(
      duration: Duration(milliseconds: 500),
      vsync: this, // Synchronizes with screen refresh
    );

    // Start animation
    _controller.forward();
  }

  @override
  void dispose() {
    // CRITICAL: Always dispose controller
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Opacity(
          opacity: _controller.value, // 0.0 to 1.0
          child: child,
        );
      },
      child: Container(
        width: 200,
        height: 200,
        color: Colors.blue,
      ),
    );
  }
}
```

**Key Requirements:**
1. **TickerProviderStateMixin** - Provides vsync for smooth animation
2. **vsync parameter** - Synchronizes animation with screen refresh rate (60fps/120fps)
3. **dispose()** - Prevents memory leaks

#### TickerProvider Variants

```dart
// Single animation
class _MyState extends State<MyWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
}

// Multiple animations
class _MyState extends State<MyWidget>
    with TickerProviderStateMixin {
  late AnimationController _controller1;
  late AnimationController _controller2;
  late AnimationController _controller3;
}
```

### 3. AnimationController Methods

#### Playback Control

```dart
final controller = AnimationController(
  duration: Duration(seconds: 2),
  vsync: this,
);

// Start from beginning to end
controller.forward();

// Start from end to beginning
controller.reverse();

// Jump to specific value (0.0 to 1.0)
controller.value = 0.5;

// Animate to specific value
controller.animateTo(0.75, duration: Duration(milliseconds: 500));

// Animate from current value to beginning
controller.animateBack(0.0, duration: Duration(milliseconds: 300));

// Repeat animation
controller.repeat(reverse: true); // Oscillate

// Stop animation
controller.stop();

// Reset to beginning
controller.reset();
```

#### Status Listening

```dart
controller.addStatusListener((status) {
  switch (status) {
    case AnimationStatus.dismissed:
      print('Animation at start (value = 0.0)');
      break;
    case AnimationStatus.forward:
      print('Animation running forward');
      break;
    case AnimationStatus.reverse:
      print('Animation running backward');
      break;
    case AnimationStatus.completed:
      print('Animation at end (value = 1.0)');
      // Auto-reverse when completed
      controller.reverse();
      break;
  }
});
```

#### Value Listening

```dart
// Listen to every value change
controller.addListener(() {
  print('Current value: ${controller.value}');
  // Can call setState() here, but AnimatedBuilder is more efficient
});
```

### 4. Tween: Value Interpolation

Tween defines the range of animated values:

```dart
// Double values
final opacityTween = Tween<double>(begin: 0.0, end: 1.0);
final sizeTween = Tween<double>(begin: 50.0, end: 200.0);

// Colors
final colorTween = ColorTween(
  begin: Colors.blue,
  end: Colors.red,
);

// Offsets (positions)
final positionTween = Tween<Offset>(
  begin: Offset(-1.0, 0.0), // Off-screen left
  end: Offset.zero,          // On-screen
);

// Borders
final borderTween = BorderRadiusTween(
  begin: BorderRadius.circular(4.0),
  end: BorderRadius.circular(24.0),
);

// Alignment
final alignmentTween = AlignmentTween(
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
);

// Creating Animation from Tween
final animation = sizeTween.animate(_controller);

// With curve
final curvedAnimation = CurvedAnimation(
  parent: _controller,
  curve: Curves.easeInOut,
);
final animation = sizeTween.animate(curvedAnimation);

// Usage in build
Container(
  width: animation.value,
  height: animation.value,
  color: Colors.blue,
)
```

**Common Tween Types:**

| Tween Type | Begin/End Types | Use Case |
|------------|----------------|----------|
| `Tween<double>` | double | Size, opacity, rotation |
| `ColorTween` | Color | Color transitions |
| `Tween<Offset>` | Offset | Slide transitions |
| `BorderRadiusTween` | BorderRadius | Border animations |
| `AlignmentTween` | Alignment | Position animations |
| `DecorationTween` | Decoration | Complex style changes |
| `TextStyleTween` | TextStyle | Text style transitions |

### 5. CurvedAnimation: Easing and Timing

Apply easing curves for natural motion:

```dart
final curvedAnimation = CurvedAnimation(
  parent: _controller,
  curve: Curves.easeInOut,        // Forward curve
  reverseCurve: Curves.easeIn,    // Reverse curve (optional)
);

final animation = Tween<double>(
  begin: 0.0,
  end: 300.0,
).animate(curvedAnimation);
```

**Material Motion 3 Recommended Curves:**

```dart
// Standard easing (most common)
Curves.easeInOut        // Accelerate and decelerate
Curves.easeOut          // Enter screen (decelerate only)
Curves.easeIn           // Exit screen (accelerate only)

// Material Motion 3 curves
Curves.easeInOutCubicEmphasized  // Material 3 emphasized
Curves.fastOutSlowIn             // Material standard

// Bouncy / Elastic
Curves.elasticOut       // Elastic bounce effect
Curves.bounceOut        // Bounce at end

// Linear
Curves.linear           // No easing

// Custom cubic bezier
Cubic(0.42, 0.0, 0.58, 1.0)  // Custom curve
```

**Material 3 Motion Durations:**

```dart
// Recommended durations for Material 3
const Duration short = Duration(milliseconds: 100);   // 100ms
const Duration medium = Duration(milliseconds: 250);  // 250ms
const Duration long = Duration(milliseconds: 500);    // 500ms
const Duration extraLong = Duration(milliseconds: 1000); // 1000ms

// Usage by transition type
Duration.short:      // Small UI changes (checkbox, switch)
Duration.medium:     // Standard transitions (dialog, sheet)
Duration.long:       // Full-screen transitions (page navigation)
Duration.extraLong:  // Emphasis animations (onboarding)
```

## Efficient Widget Rebuilding

### 1. AnimatedBuilder Pattern

**Best Practice:** Use AnimatedBuilder to minimize rebuild scope:

```dart
class FadeInWidget extends StatefulWidget {
  final Widget child;

  FadeInWidget({required this.child});

  @override
  _FadeInWidgetState createState() => _FadeInWidgetState();
}

class _FadeInWidgetState extends State<FadeInWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 500),
      vsync: this,
    );
    _animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // ✅ AnimatedBuilder only rebuilds its builder function
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Opacity(
          opacity: _animation.value,
          child: child, // Child passed through, not rebuilt
        );
      },
      child: widget.child, // Built once, reused on every frame
    );
  }
}

// ❌ BAD: Using setState causes full widget rebuild
@override
Widget build(BuildContext context) {
  _controller.addListener(() {
    setState(() {}); // Rebuilds entire widget tree - inefficient!
  });

  return Opacity(
    opacity: _controller.value,
    child: ExpensiveWidget(), // Rebuilt every frame!
  );
}
```

**AnimatedBuilder Benefits:**
- Only rebuilds builder function (minimal scope)
- Child widget built once, reused across frames
- No setState() needed
- Optimal performance for 60fps animations

### 2. Pre-built Animated Widgets

Flutter provides pre-built explicit animated widgets:

```dart
// Fade transition
FadeTransition(
  opacity: _animation,
  child: MyWidget(),
)

// Scale transition
ScaleTransition(
  scale: _animation,
  child: MyWidget(),
)

// Slide transition
SlideTransition(
  position: _offsetAnimation,
  child: MyWidget(),
)

// Rotation transition
RotationTransition(
  turns: _animation, // 0.0 to 1.0 = 0° to 360°
  child: MyWidget(),
)

// Size transition (vertical)
SizeTransition(
  sizeFactor: _animation,
  axisAlignment: -1.0, // Top alignment
  child: MyWidget(),
)

// Positioned transition (absolute positioning)
PositionedTransition(
  rect: _rectAnimation,
  child: MyWidget(),
)
```

**Advantages:**
- Pre-optimized for performance
- Less boilerplate code
- Automatic handling of edge cases

## Advanced Patterns

### 1. Staggered Animations

Animate multiple properties with different timings:

```dart
class StaggeredAnimation extends StatefulWidget {
  @override
  _StaggeredAnimationState createState() => _StaggeredAnimationState();
}

class _StaggeredAnimationState extends State<StaggeredAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacity;
  late Animation<double> _size;
  late Animation<Offset> _position;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      duration: Duration(milliseconds: 2000),
      vsync: this,
    );

    // Opacity: 0% to 40% of duration
    _opacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Interval(0.0, 0.4, curve: Curves.easeIn),
      ),
    );

    // Size: 30% to 70% of duration
    _size = Tween<double>(begin: 50.0, end: 200.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Interval(0.3, 0.7, curve: Curves.easeOut),
      ),
    );

    // Position: 60% to 100% of duration
    _position = Tween<Offset>(
      begin: Offset(0, -1),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Interval(0.6, 1.0, curve: Curves.elasticOut),
      ),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return SlideTransition(
          position: _position,
          child: Opacity(
            opacity: _opacity.value,
            child: Container(
              width: _size.value,
              height: _size.value,
              color: Colors.blue,
            ),
          ),
        );
      },
    );
  }
}
```

**Interval Parameters:**
- `begin`: Start time (0.0 to 1.0)
- `end`: End time (0.0 to 1.0)
- `curve`: Easing curve for this interval

### 2. Chained Animations (Sequences)

Run animations sequentially:

```dart
class ChainedAnimation extends StatefulWidget {
  @override
  _ChainedAnimationState createState() => _ChainedAnimationState();
}

class _ChainedAnimationState extends State<ChainedAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 500),
      vsync: this,
    );

    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        // First animation complete, start second
        Future.delayed(Duration(milliseconds: 200), () {
          if (mounted) {
            _controller.reverse();
          }
        });
      } else if (status == AnimationStatus.dismissed) {
        // Second animation complete, start again
        Future.delayed(Duration(milliseconds: 200), () {
          if (mounted) {
            _controller.forward();
          }
        });
      }
    });

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: Tween<double>(begin: 0.8, end: 1.2).animate(
        CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
      ),
      child: Container(
        width: 100,
        height: 100,
        color: Colors.blue,
      ),
    );
  }
}
```

### 3. Hero Animations (Page Transitions)

Shared element transitions between routes:

```dart
// Page 1
class ListPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: 10,
      itemBuilder: (context, index) {
        return Hero(
          tag: 'item-$index', // Unique tag
          child: ListTile(
            leading: CircleAvatar(
              child: Text('$index'),
            ),
            title: Text('Item $index'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => DetailPage(index: index),
                ),
              );
            },
          ),
        );
      },
    );
  }
}

// Page 2 (matching Hero tag creates automatic transition)
class DetailPage extends StatelessWidget {
  final int index;

  DetailPage({required this.index});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Detail $index')),
      body: Center(
        child: Hero(
          tag: 'item-$index', // Same tag as origin
          child: CircleAvatar(
            radius: 100,
            child: Text('$index', style: TextStyle(fontSize: 48)),
          ),
        ),
      ),
    );
  }
}
```

**Hero Requirements:**
- Matching `tag` on both pages
- Automatic animation when navigating
- Customizable with `flightShuttleBuilder`

### 4. Physics-Based Animations

Simulate real-world physics:

```dart
import 'package:flutter/physics.dart';

class PhysicsAnimation extends StatefulWidget {
  @override
  _PhysicsAnimationState createState() => _PhysicsAnimationState();
}

class _PhysicsAnimationState extends State<PhysicsAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: 2),
    );
  }

  void _animateWithSpring() {
    final spring = SpringDescription(
      mass: 1.0,
      stiffness: 100.0,
      damping: 10.0,
    );

    final simulation = SpringSimulation(
      spring,
      0.0,  // Starting position
      1.0,  // Ending position
      0.0,  // Initial velocity
    );

    _controller.animateWith(simulation);
  }

  void _animateWithGravity() {
    final gravity = GravitySimulation(
      9.8,   // Acceleration (m/s²)
      0.0,   // Starting position
      400.0, // Ending position
      0.0,   // Initial velocity
    );

    _controller.animateWith(gravity);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _animateWithSpring,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Transform.translate(
            offset: Offset(0, _controller.value * 300),
            child: Container(
              width: 100,
              height: 100,
              color: Colors.blue,
            ),
          );
        },
      ),
    );
  }
}
```

**Physics Simulation Types:**
- **SpringSimulation** - Bouncy, elastic motion
- **GravitySimulation** - Falling objects
- **FrictionSimulation** - Deceleration

## Performance Optimization

### 1. Controller Optimization

```dart
// ✅ GOOD: Reuse controller for repeated animations
class OptimizedWidget extends StatefulWidget {
  @override
  _OptimizedWidgetState createState() => _OptimizedWidgetState();
}

class _OptimizedWidgetState extends State<OptimizedWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 500),
      vsync: this,
    );
  }

  void _animate() {
    _controller.forward(from: 0.0); // Reset and animate
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _animate,
      child: FadeTransition(
        opacity: _controller,
        child: Container(
          width: 200,
          height: 200,
          color: Colors.blue,
        ),
      ),
    );
  }
}
```

### 2. Custom Painter Integration

Combine with CustomPainter for optimal rendering:

```dart
class AnimatedCustomPainter extends CustomPainter {
  final Animation<double> animation;

  AnimatedCustomPainter({required this.animation})
      : super(repaint: animation); // Auto-repaint on animation change

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.fill;

    final radius = 50 + (animation.value * 100);

    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2),
      radius,
      paint,
    );
  }

  @override
  bool shouldRepaint(AnimatedCustomPainter oldDelegate) {
    return false; // Handled by repaint parameter
  }
}

// Usage
CustomPaint(
  size: Size(300, 300),
  painter: AnimatedCustomPainter(animation: _controller),
)
```

**Benefits:**
- Skips build() and layout() phases
- Only paint() executes per frame
- Optimal for 60fps performance

## Complete Example: Card Flip Animation

```dart
import 'package:flutter/material.dart';
import 'dart:math' as math;

class FlipCard extends StatefulWidget {
  final Widget front;
  final Widget back;

  FlipCard({required this.front, required this.back});

  @override
  _FlipCardState createState() => _FlipCardState();
}

class _FlipCardState extends State<FlipCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  bool _showFront = true;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 600),
      vsync: this,
    );

    _animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );

    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        setState(() {
          _showFront = !_showFront;
        });
        _controller.reset();
      }
    });
  }

  void _flip() {
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _flip,
      child: AnimatedBuilder(
        animation: _animation,
        builder: (context, child) {
          final angle = _animation.value * math.pi;
          final transform = Matrix4.identity()
            ..setEntry(3, 2, 0.001) // Perspective
            ..rotateY(angle);

          return Transform(
            transform: transform,
            alignment: Alignment.center,
            child: _animation.value < 0.5
                ? widget.front
                : Transform(
                    transform: Matrix4.rotationY(math.pi),
                    alignment: Alignment.center,
                    child: widget.back,
                  ),
          );
        },
      ),
    );
  }
}

// Usage
FlipCard(
  front: Container(
    width: 200,
    height: 300,
    color: Colors.blue,
    child: Center(child: Text('Front', style: TextStyle(fontSize: 24))),
  ),
  back: Container(
    width: 200,
    height: 300,
    color: Colors.red,
    child: Center(child: Text('Back', style: TextStyle(fontSize: 24))),
  ),
)
```

## Troubleshooting

### Animation Not Starting

**Check:**
1. Controller initialized in initState()
2. Called forward(), reverse(), or repeat()
3. vsync provider implemented (SingleTickerProviderStateMixin)
4. Widget mounted when starting animation

### Choppy Animation / Low FPS

**Solutions:**
1. Use AnimatedBuilder (not setState in listener)
2. Reduce build() complexity
3. Use RepaintBoundary for static content
4. Profile with Flutter DevTools Performance view
5. Consider shorter duration or simpler animation

### Memory Leaks

**Symptoms:** App crashes after many navigations

**Solution:** Always dispose controllers:

```dart
@override
void dispose() {
  _controller1.dispose();
  _controller2.dispose();
  // Dispose ALL controllers
  super.dispose();
}
```

### Animation Continues After Widget Disposal

**Solution:** Check mounted before animating:

```dart
void _delayedAnimation() async {
  await Future.delayed(Duration(seconds: 1));
  if (mounted) { // Check before animating
    _controller.forward();
  }
}
```

## Integration with Other Skills

Combine with:

- **flutter-custom-painter** - Animate custom graphics efficiently
- **flutter-fragment-shaders** - Animate shader uniforms
- **flutter-performance-optimization** - Profile and optimize animation performance
- **material-design-3-flutter** - Use Material Motion 3 curves and durations
- **flutter-widget-previewer** - Preview animated components

## Additional Resources

- **Animations Tutorial:** https://docs.flutter.dev/ui/animations/tutorial
- **Animations API Overview:** https://docs.flutter.dev/ui/animations/overview
- **AnimationController API:** https://api.flutter.dev/flutter/animation/AnimationController-class.html
- **Material Motion Guidelines:** https://m3.material.io/styles/motion/overview
- **Implicit Animations:** https://docs.flutter.dev/ui/animations/implicit-animations

Explicit animations provide the precision and control needed for creating polished, professional motion in Flutter applications.
