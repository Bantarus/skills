---
name: flutter-custom-painter
description: Comprehensive guide for creating custom graphics and shapes using Flutter's CustomPainter and Canvas APIs. This skill should be used when implementing custom drawings, complex shapes, procedural graphics, or low-level rendering that goes beyond standard Flutter widgets. Covers CustomPainter implementation, Canvas API, Paint configuration, efficient repainting, and performance optimization for custom graphics.
---

# Flutter CustomPainter and Canvas Drawing

## Overview

CustomPainter is Flutter's low-level rendering API that provides direct access to the Canvas for creating custom graphics, complex shapes, and procedural drawings. This enables implementation of designs that cannot be achieved with standard widgets, such as custom charts, diagrams, procedural art, and complex geometric shapes.

**Core Components:**
- **CustomPaint** - Widget that provides the canvas surface
- **CustomPainter** - Delegate that defines the drawing logic
- **Canvas** - Low-level drawing API with primitives (lines, paths, circles, etc.)
- **Paint** - Configuration object for visual attributes (color, stroke, shader)

**Version Compatibility:**
- Available in all Flutter versions
- API Reference: https://api.flutter.dev/flutter/rendering/CustomPainter-class.html
- Canvas API: https://api.flutter.dev/flutter/dart-ui/Canvas-class.html
- Paint API: https://api.flutter.dev/flutter/dart-ui/Paint-class.html

**Use Cases:**
- Custom charts and data visualizations
- Complex geometric shapes and patterns
- Procedural graphics and generative art
- Custom progress indicators
- Signature pads and drawing applications
- Game graphics and particle systems

## Core Concepts

### 1. CustomPainter Lifecycle

#### Basic CustomPainter Implementation

```dart
import 'package:flutter/material.dart';

class CirclePainter extends CustomPainter {
  final Color color;
  final double radius;

  CirclePainter({
    required this.color,
    required this.radius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Create Paint object for visual attributes
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    // Calculate center point
    final center = Offset(size.width / 2, size.height / 2);

    // Draw circle
    canvas.drawCircle(center, radius, paint);
  }

  @override
  bool shouldRepaint(CirclePainter oldDelegate) {
    // Return true if any visual property changed
    return oldDelegate.color != color || oldDelegate.radius != radius;
  }
}

// Usage in widget tree
class CircleWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(200, 200),
      painter: CirclePainter(
        color: Colors.blue,
        radius: 50,
      ),
    );
  }
}
```

#### The paint() Method

The `paint(Canvas canvas, Size size)` method is called whenever the custom painter needs to render:

```dart
@override
void paint(Canvas canvas, Size size) {
  // 1. Canvas coordinate system:
  //    - Origin (0, 0) is at top-left corner
  //    - X-axis increases to the right
  //    - Y-axis increases downward
  //    - Available drawing area: (0, 0) to (size.width, size.height)

  // 2. Create Paint objects for different visual styles
  final fillPaint = Paint()
    ..color = Colors.blue
    ..style = PaintingStyle.fill;

  final strokePaint = Paint()
    ..color = Colors.red
    ..style = PaintingStyle.stroke
    ..strokeWidth = 2.0;

  // 3. Use canvas primitives to draw
  canvas.drawRect(
    Rect.fromLTWH(10, 10, size.width - 20, size.height - 20),
    strokePaint,
  );

  canvas.drawCircle(
    Offset(size.width / 2, size.height / 2),
    50,
    fillPaint,
  );
}
```

**Key Points:**
- Canvas is scoped to the rendering box
- Size parameter defines available drawing area
- Origin is always at top-left (0, 0)
- Drawing outside bounds is clipped

#### The shouldRepaint() Method

Determines whether the painting logic needs to execute again:

```dart
@override
bool shouldRepaint(covariant CirclePainter oldDelegate) {
  // Compare current instance with previous instance
  // Return true ONLY if visual output would differ
  return oldDelegate.color != color ||
         oldDelegate.radius != radius;
}
```

**Performance Impact:**
- Return `false` for static, unchanging graphics
- Return `true` only when actual visual changes occurred
- Avoid expensive comparisons in this method
- Framework may cache the painted result when `false`

### 2. Canvas Drawing Primitives

#### Lines and Paths

```dart
class PathPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    // Draw single line
    canvas.drawLine(
      Offset(0, 0),
      Offset(size.width, size.height),
      paint,
    );

    // Draw complex path
    final path = Path();
    path.moveTo(20, 20); // Starting point
    path.lineTo(size.width - 20, 20); // Line to
    path.lineTo(size.width / 2, size.height - 20); // Line to
    path.close(); // Close path (creates triangle)

    canvas.drawPath(path, paint);

    // Bezier curves
    final curvePath = Path();
    curvePath.moveTo(0, size.height / 2);
    curvePath.quadraticBezierTo(
      size.width / 2, 0, // Control point
      size.width, size.height / 2, // End point
    );
    canvas.drawPath(curvePath, paint);

    // Cubic bezier for smoother curves
    final smoothPath = Path();
    smoothPath.moveTo(0, size.height);
    smoothPath.cubicTo(
      size.width * 0.25, size.height * 0.8, // Control point 1
      size.width * 0.75, size.height * 0.2, // Control point 2
      size.width, 0, // End point
    );
    canvas.drawPath(smoothPath, paint);
  }

  @override
  bool shouldRepaint(PathPainter oldDelegate) => false;
}
```

#### Shapes and Primitives

```dart
class ShapesPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final fillPaint = Paint()
      ..color = Colors.blue.withOpacity(0.5)
      ..style = PaintingStyle.fill;

    final strokePaint = Paint()
      ..color = Colors.red
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    // Rectangle
    canvas.drawRect(
      Rect.fromLTWH(10, 10, 100, 80),
      fillPaint,
    );

    // Rounded rectangle
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(120, 10, 100, 80),
        Radius.circular(12),
      ),
      strokePaint,
    );

    // Circle
    canvas.drawCircle(
      Offset(60, 150),
      40,
      fillPaint,
    );

    // Oval
    canvas.drawOval(
      Rect.fromLTWH(120, 110, 100, 80),
      strokePaint,
    );

    // Arc (portion of circle/ellipse)
    canvas.drawArc(
      Rect.fromLTWH(10, 210, 100, 100),
      0, // Start angle (radians)
      3.14159, // Sweep angle (radians, π = 180°)
      true, // Use center (creates pie slice if true)
      fillPaint,
    );

    // Points
    final points = [
      Offset(130, 250),
      Offset(140, 260),
      Offset(150, 255),
      Offset(160, 265),
      Offset(170, 258),
    ];
    canvas.drawPoints(
      PointMode.polygon, // or PointMode.points, PointMode.lines
      points,
      strokePaint..strokeWidth = 4,
    );
  }

  @override
  bool shouldRepaint(ShapesPainter oldDelegate) => false;
}
```

#### Text Rendering

```dart
class TextPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Create TextPainter for text rendering
    final textPainter = TextPainter(
      text: TextSpan(
        text: 'Custom Text',
        style: TextStyle(
          color: Colors.black,
          fontSize: 24,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    );

    // Layout the text
    textPainter.layout(
      minWidth: 0,
      maxWidth: size.width,
    );

    // Paint the text at specific position
    textPainter.paint(
      canvas,
      Offset(
        (size.width - textPainter.width) / 2,
        (size.height - textPainter.height) / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(TextPainter oldDelegate) => false;
}
```

### 3. Paint Configuration

#### Paint Properties

```dart
final paint = Paint()
  // Color and transparency
  ..color = Colors.blue.withOpacity(0.7)

  // Fill or stroke
  ..style = PaintingStyle.fill // or PaintingStyle.stroke

  // Stroke properties (when style = stroke)
  ..strokeWidth = 4.0
  ..strokeCap = StrokeCap.round // round, square, butt
  ..strokeJoin = StrokeJoin.round // round, miter, bevel

  // Anti-aliasing (smoother edges, slight performance cost)
  ..isAntiAlias = true

  // Blend modes
  ..blendMode = BlendMode.multiply

  // Filter quality for images
  ..filterQuality = FilterQuality.high;
```

#### Gradients

```dart
class GradientPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Linear gradient
    final linearGradient = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Colors.blue, Colors.purple, Colors.pink],
        stops: [0.0, 0.5, 1.0],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height / 2));

    canvas.drawRect(
      Rect.fromLTWH(0, 0, size.width, size.height / 2),
      linearGradient,
    );

    // Radial gradient
    final radialGradient = Paint()
      ..shader = RadialGradient(
        center: Alignment.center,
        radius: 0.5,
        colors: [Colors.yellow, Colors.orange, Colors.red],
      ).createShader(Rect.fromLTWH(0, size.height / 2, size.width, size.height / 2));

    canvas.drawRect(
      Rect.fromLTWH(0, size.height / 2, size.width, size.height / 2),
      radialGradient,
    );

    // Sweep gradient (circular)
    final sweepGradient = Paint()
      ..shader = SweepGradient(
        colors: [Colors.red, Colors.yellow, Colors.green, Colors.blue, Colors.red],
      ).createShader(Rect.fromCircle(
        center: Offset(size.width / 2, size.height / 2),
        radius: 100,
      ));

    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2),
      100,
      sweepGradient,
    );
  }

  @override
  bool shouldRepaint(GradientPainter oldDelegate) => false;
}
```

### 4. Advanced Techniques

#### Clipping

```dart
class ClipPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Save current canvas state
    canvas.save();

    // Create clipping path
    final clipPath = Path();
    clipPath.addOval(Rect.fromCircle(
      center: Offset(size.width / 2, size.height / 2),
      radius: 100,
    ));

    // Apply clip
    canvas.clipPath(clipPath);

    // All subsequent drawing is clipped to path
    final paint = Paint()..color = Colors.blue;
    canvas.drawRect(
      Rect.fromLTWH(0, 0, size.width, size.height),
      paint,
    );

    // Restore canvas state (removes clip)
    canvas.restore();
  }

  @override
  bool shouldRepaint(ClipPainter oldDelegate) => false;
}
```

#### Transformations

```dart
class TransformPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = Colors.blue;

    // Translation
    canvas.save();
    canvas.translate(100, 50);
    canvas.drawRect(Rect.fromLTWH(0, 0, 50, 50), paint);
    canvas.restore();

    // Rotation (radians)
    canvas.save();
    canvas.translate(size.width / 2, size.height / 2);
    canvas.rotate(0.785398); // 45 degrees = π/4 radians
    canvas.drawRect(
      Rect.fromCenter(center: Offset.zero, width: 80, height: 80),
      paint..color = Colors.red,
    );
    canvas.restore();

    // Scaling
    canvas.save();
    canvas.translate(size.width - 100, size.height - 100);
    canvas.scale(1.5, 1.5);
    canvas.drawCircle(Offset.zero, 30, paint..color = Colors.green);
    canvas.restore();

    // Combined transformations
    canvas.save();
    canvas.translate(size.width / 2, size.height - 80);
    canvas.rotate(-0.5);
    canvas.scale(0.8);
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(center: Offset.zero, width: 100, height: 50),
        Radius.circular(10),
      ),
      paint..color = Colors.purple,
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(TransformPainter oldDelegate) => false;
}
```

**Transformation Best Practices:**
- Always use `canvas.save()` before transformations
- Always call `canvas.restore()` after to restore state
- Transformations stack (later transforms affect earlier ones)
- Use `translate()` to move rotation/scale origin

## Performance Optimization

### 1. Efficient Repainting with Listenable

For animated custom painters, avoid triggering full widget rebuilds:

```dart
class AnimatedCirclePainter extends CustomPainter {
  final Animation<double> animation;

  AnimatedCirclePainter({required this.animation})
      : super(repaint: animation); // KEY: Pass animation as repaint Listenable

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.fill;

    // Use animation value
    final radius = 50 + (animation.value * 50);

    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2),
      radius,
      paint,
    );
  }

  @override
  bool shouldRepaint(AnimatedCirclePainter oldDelegate) {
    // Animation changes are handled by repaint Listenable
    return false;
  }
}

// Usage with AnimationController
class AnimatedCircleWidget extends StatefulWidget {
  @override
  _AnimatedCircleWidgetState createState() => _AnimatedCircleWidgetState();
}

class _AnimatedCircleWidgetState extends State<AnimatedCircleWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(200, 200),
      painter: AnimatedCirclePainter(animation: _controller),
    );
  }
}
```

**Why This is Optimal:**
- CustomPaint automatically listens to the animation
- Only the `paint()` method executes on animation tick
- Skips expensive build() and layout() phases
- Maintains 60fps performance for smooth animations

### 2. Optimizing shouldRepaint

```dart
class OptimizedPainter extends CustomPainter {
  final Color color;
  final double value;
  final String? text; // Nullable, may not affect rendering

  OptimizedPainter({
    required this.color,
    required this.value,
    this.text,
  });

  @override
  bool shouldRepaint(OptimizedPainter oldDelegate) {
    // Only compare properties that affect visual output
    return oldDelegate.color != color ||
           oldDelegate.value != value;
    // Intentionally omit text comparison if not rendered
  }

  @override
  void paint(Canvas canvas, Size size) {
    // Drawing logic...
  }
}
```

**Optimization Guidelines:**
- Only compare fields that affect visual output
- Avoid deep object comparisons
- For static painters (never change), always return false
- For dynamic painters, compare only visual properties

### 3. Reducing Drawing Complexity

```dart
class EfficientChartPainter extends CustomPainter {
  final List<double> data;

  EfficientChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    // Build path once
    final path = Path();
    final stepX = size.width / (data.length - 1);

    path.moveTo(0, size.height - data[0]);
    for (int i = 1; i < data.length; i++) {
      path.lineTo(i * stepX, size.height - data[i]);
    }

    // Single drawPath call (efficient)
    canvas.drawPath(path, paint);

    // ❌ AVOID: Multiple draw calls in loop
    // for (int i = 0; i < data.length - 1; i++) {
    //   canvas.drawLine(
    //     Offset(i * stepX, size.height - data[i]),
    //     Offset((i + 1) * stepX, size.height - data[i + 1]),
    //     paint,
    //   );
    // }
  }

  @override
  bool shouldRepaint(EfficientChartPainter oldDelegate) {
    return oldDelegate.data != data;
  }
}
```

**Performance Best Practices:**
- Batch drawing operations (use Path instead of multiple drawLine calls)
- Minimize canvas.save() / canvas.restore() pairs
- Cache expensive calculations outside paint() when possible
- Use simpler shapes when visual difference is negligible

### 4. RepaintBoundary for Isolation

```dart
class ComplexLayout extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Frequently changing content
        AnimatedWidget(),

        // Static custom-painted content
        RepaintBoundary(
          child: CustomPaint(
            size: Size(300, 200),
            painter: StaticComplexPainter(),
          ),
        ),

        // More dynamic content
        DynamicWidget(),
      ],
    );
  }
}
```

**RepaintBoundary Benefits:**
- Isolates custom painting from surrounding widget repaints
- Caches the painted result as a separate layer
- Critical for complex static graphics in dynamic layouts
- Trade-off: Additional memory for layer cache

## Complete Examples

### Example 1: Progress Circle with Animation

```dart
import 'package:flutter/material.dart';
import 'dart:math' as math;

class ProgressCirclePainter extends CustomPainter {
  final double progress; // 0.0 to 1.0
  final Color backgroundColor;
  final Color progressColor;
  final double strokeWidth;

  ProgressCirclePainter({
    required this.progress,
    required this.backgroundColor,
    required this.progressColor,
    this.strokeWidth = 8.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Background circle
    final backgroundPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;

    canvas.drawCircle(center, radius, backgroundPaint);

    // Progress arc
    final progressPaint = Paint()
      ..color = progressColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2, // Start at top (12 o'clock)
      2 * math.pi * progress, // Sweep angle based on progress
      false, // Don't use center (creates arc, not pie slice)
      progressPaint,
    );

    // Progress text
    final textPainter = TextPainter(
      text: TextSpan(
        text: '${(progress * 100).toInt()}%',
        style: TextStyle(
          color: progressColor,
          fontSize: 24,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    );

    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        center.dx - textPainter.width / 2,
        center.dy - textPainter.height / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(ProgressCirclePainter oldDelegate) {
    return oldDelegate.progress != progress ||
           oldDelegate.backgroundColor != backgroundColor ||
           oldDelegate.progressColor != progressColor ||
           oldDelegate.strokeWidth != strokeWidth;
  }
}

// Animated usage
class ProgressCircleWidget extends StatefulWidget {
  @override
  _ProgressCircleWidgetState createState() => _ProgressCircleWidgetState();
}

class _ProgressCircleWidgetState extends State<ProgressCircleWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(seconds: 3),
      vsync: this,
    );

    _animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
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
      animation: _animation,
      builder: (context, child) {
        return CustomPaint(
          size: Size(200, 200),
          painter: ProgressCirclePainter(
            progress: _animation.value,
            backgroundColor: Colors.grey.shade300,
            progressColor: Colors.blue,
            strokeWidth: 12,
          ),
        );
      },
    );
  }
}
```

### Example 2: Line Chart

```dart
class LineChartPainter extends CustomPainter {
  final List<double> dataPoints;
  final Color lineColor;
  final Color fillColor;

  LineChartPainter({
    required this.dataPoints,
    required this.lineColor,
    required this.fillColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (dataPoints.isEmpty) return;

    final paint = Paint()
      ..color = lineColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final fillPaint = Paint()
      ..color = fillColor.withOpacity(0.3)
      ..style = PaintingStyle.fill;

    // Calculate scales
    final maxValue = dataPoints.reduce(math.max);
    final minValue = dataPoints.reduce(math.min);
    final range = maxValue - minValue;
    final stepX = size.width / (dataPoints.length - 1);

    // Build line path
    final linePath = Path();
    final fillPath = Path();

    for (int i = 0; i < dataPoints.length; i++) {
      final x = i * stepX;
      final normalizedValue = (dataPoints[i] - minValue) / range;
      final y = size.height - (normalizedValue * size.height);

      if (i == 0) {
        linePath.moveTo(x, y);
        fillPath.moveTo(x, size.height);
        fillPath.lineTo(x, y);
      } else {
        linePath.lineTo(x, y);
        fillPath.lineTo(x, y);
      }
    }

    // Close fill path
    fillPath.lineTo(size.width, size.height);
    fillPath.close();

    // Draw fill area then line
    canvas.drawPath(fillPath, fillPaint);
    canvas.drawPath(linePath, paint);

    // Draw data points
    final pointPaint = Paint()
      ..color = lineColor
      ..style = PaintingStyle.fill;

    for (int i = 0; i < dataPoints.length; i++) {
      final x = i * stepX;
      final normalizedValue = (dataPoints[i] - minValue) / range;
      final y = size.height - (normalizedValue * size.height);
      canvas.drawCircle(Offset(x, y), 4, pointPaint);
    }
  }

  @override
  bool shouldRepaint(LineChartPainter oldDelegate) {
    return oldDelegate.dataPoints != dataPoints ||
           oldDelegate.lineColor != lineColor ||
           oldDelegate.fillColor != fillColor;
  }
}
```

## Troubleshooting

### Canvas Drawing Not Visible

**Common Causes:**
1. Paint style set to stroke but strokeWidth is 0
2. Drawing outside the visible size bounds
3. Color transparency is 1.0 (fully transparent)
4. Z-order issue (drawn behind other elements)

**Solution:**
```dart
// Check Paint configuration
final paint = Paint()
  ..color = Colors.blue.withOpacity(1.0) // Ensure visible
  ..style = PaintingStyle.fill; // Or stroke with strokeWidth

// Verify drawing within bounds
print('Canvas size: $size');
print('Drawing at: ${offset.dx}, ${offset.dy}');
```

### Performance Issues / Jank

**Symptoms:** Frame drops, stuttering animation

**Solutions:**
1. Use `repaint` parameter for animations (see Section 4.1)
2. Avoid expensive calculations in paint() - cache results
3. Simplify path complexity
4. Use RepaintBoundary
5. Profile with Flutter DevTools Performance view

### Transformations Not Applied Correctly

**Symptom:** Rotation/scaling appears wrong or in unexpected location

**Solution:** Translate to desired origin before rotation/scaling:

```dart
// ❌ Wrong: Rotates around (0, 0)
canvas.rotate(angle);
canvas.drawRect(rect, paint);

// ✅ Correct: Rotates around rect center
canvas.save();
canvas.translate(rect.center.dx, rect.center.dy);
canvas.rotate(angle);
canvas.translate(-rect.width / 2, -rect.height / 2);
canvas.drawRect(Rect.fromLTWH(0, 0, rect.width, rect.height), paint);
canvas.restore();
```

## Integration with Other Skills

This skill combines well with:

- **flutter-fragment-shaders** - Apply GPU shaders to Paint objects for advanced effects
- **flutter-explicit-animations** - Create smooth animated custom graphics
- **flutter-performance-optimization** - Profile and optimize custom painting performance
- **flutter-widget-previewer** - Preview custom-painted components in isolation

## Additional Resources

- **Official CustomPainter Documentation:** https://api.flutter.dev/flutter/rendering/CustomPainter-class.html
- **Canvas API Reference:** https://api.flutter.dev/flutter/dart-ui/Canvas-class.html
- **Paint API Reference:** https://api.flutter.dev/flutter/dart-ui/Paint-class.html
- **Flutter CustomPaint Tutorial:** https://docs.flutter.dev/ui/widgets/painting
- **Path Class Documentation:** https://api.flutter.dev/flutter/dart-ui/Path-class.html

CustomPainter provides the foundation for creating unique, high-performance custom graphics that go beyond standard Flutter widgets.
