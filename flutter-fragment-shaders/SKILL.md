---
name: flutter-fragment-shaders
description: Comprehensive guide for writing and using GLSL fragment shaders in Flutter for GPU-accelerated graphics. This skill should be used when implementing advanced visual effects, procedural graphics, GPU-based animations, or custom shader-based rendering. Covers GLSL shader authoring, FragmentProgram API, uniform configuration, shader compilation, integration with CustomPainter, and performance optimization.
---

# Flutter Fragment Shaders and GPU Programming

## Overview

Fragment shaders enable Flutter applications to leverage GPU-accelerated graphics by executing custom GLSL code directly on the graphics processor. This allows creation of advanced visual effects, procedural textures, and high-performance graphical computations that would be prohibitively expensive on the CPU.

**Core Concepts:**
- **Shader** - Small program written in GLSL, executed on the GPU
- **Fragment** - Individual pixel being processed
- **Uniforms** - Configuration parameters passed from Dart to shader
- **Samplers** - Texture/image inputs for shader processing

**Version Compatibility:**
- Available in Flutter 2.10+
- GLSL ES 3.0 specification
- Compiled to platform-specific formats (SPIR-V, Metal Shading Language, etc.)
- Cross-platform support (iOS, Android, Web, Desktop)

**Official Resources:**
- Documentation: https://docs.flutter.dev/ui/design/graphics/fragment-shaders
- Last updated: November 3, 2025 (Flutter 3.35.5)

**Use Cases:**
- Procedural backgrounds and textures
- Real-time visual effects (blur, distortion, color grading)
- GPU-based particle systems
- Custom image filters
- Animated gradients and patterns
- Transition effects
- Data visualization with GPU acceleration

## Setup and Configuration

### 1. Declaring Shaders in pubspec.yaml

All shader files must be explicitly declared in the `shaders:` section:

```yaml
flutter:
  # Regular assets
  assets:
    - assets/images/
    - assets/icons/

  # Shader files (separate section)
  shaders:
    - shaders/gradient.frag
    - shaders/ripple.frag
    - shaders/blur.frag
```

**Shader File Requirements:**
- Must have `.frag` extension
- Written in GLSL ES 3.0
- Must be listed individually (no directory wildcards)
- Compiled during build process to platform-specific formats

### 2. Project Structure

**Recommended Organization:**

```
lib/
├── components/
│   └── shader_button/
│       ├── shader_button.dart           # Widget implementation
│       ├── shader_painter.dart          # CustomPainter with shader
│       └── shaders/
│           └── button_effect.frag       # GLSL shader
├── shaders/                             # Global shaders
│   ├── water_ripple.frag
│   └── gradient_noise.frag
└── main.dart

pubspec.yaml                             # Shader declarations
```

## GLSL Shader Authoring

### 1. Basic Shader Structure

Every fragment shader follows this template:

```glsl
#version 460 core

// REQUIRED: Precision qualifier (usually highp for Flutter)
precision highp float;

// REQUIRED: Import Flutter's shader library
#include <flutter/runtime_effects.glsl>

// Uniforms: Configuration from Dart
uniform float u_time;
uniform vec2 u_resolution;
uniform vec4 u_color;

// Samplers: Image/texture inputs
uniform sampler2D u_texture;

// OUTPUT: Fragment color
out vec4 fragColor;

// REQUIRED: Entry point
void main() {
    // Get normalized coordinates (0.0 to 1.0)
    vec2 uv = FlutterFragCoord().xy / u_resolution;

    // Example: Simple gradient
    fragColor = vec4(uv.x, uv.y, 0.5, 1.0);
}
```

**Key Components:**

1. **Version Declaration:** `#version 460 core` - GLSL version
2. **Precision:** `precision highp float;` - Floating-point precision
3. **Flutter Include:** `#include <flutter/runtime_effects.glsl>` - Required utilities
4. **Uniforms:** Variables set from Dart code
5. **Samplers:** Texture/image inputs
6. **Output:** `out vec4 fragColor` - Final pixel color (RGBA)
7. **FlutterFragCoord():** Gets current fragment's coordinate

### 2. Uniform Types and Usage

#### Supported Uniform Types

```glsl
// Scalar (single value)
uniform float u_time;              // Time in seconds
uniform float u_intensity;         // Effect strength

// Vectors
uniform vec2 u_resolution;         // Screen/canvas size (width, height)
uniform vec2 u_mouse;              // Mouse/touch position
uniform vec3 u_color_rgb;          // RGB color
uniform vec4 u_color_rgba;         // RGBA color with alpha

// Samplers (textures/images)
uniform sampler2D u_image;         // 2D texture input
```

**Setting Uniforms from Dart (covered in Section 3):**
- `setFloat(index, value)` for float, vec2, vec3, vec4
- `setImageSampler(index, image)` for sampler2D

#### Uniform Best Practices

```glsl
// ✅ GOOD: Descriptive names with u_ prefix
uniform float u_time;
uniform vec2 u_resolution;
uniform vec4 u_primary_color;

// ❌ AVOID: Generic or ambiguous names
uniform float t;
uniform vec2 res;
uniform vec4 c;
```

### 3. Common Shader Patterns

#### Animated Gradient

```glsl
#version 460 core
precision highp float;
#include <flutter/runtime_effects.glsl>

uniform float u_time;
uniform vec2 u_resolution;
uniform vec4 u_color1;
uniform vec4 u_color2;

out vec4 fragColor;

void main() {
    vec2 uv = FlutterFragCoord().xy / u_resolution;

    // Animated gradient based on time
    float mixValue = 0.5 + 0.5 * sin(u_time + uv.x * 3.14159);

    fragColor = mix(u_color1, u_color2, mixValue);
}
```

#### Ripple Effect

```glsl
#version 460 core
precision highp float;
#include <flutter/runtime_effects.glsl>

uniform float u_time;
uniform vec2 u_resolution;
uniform vec2 u_center;        // Ripple origin
uniform float u_intensity;

uniform sampler2D u_image;

out vec4 fragColor;

void main() {
    vec2 uv = FlutterFragCoord().xy / u_resolution;

    // Distance from center
    vec2 center = u_center / u_resolution;
    float dist = distance(uv, center);

    // Ripple wave
    float ripple = sin(dist * 30.0 - u_time * 5.0) * u_intensity * (1.0 - dist);

    // Offset UV coordinates based on ripple
    vec2 offset = normalize(uv - center) * ripple * 0.02;
    vec2 distortedUV = uv + offset;

    // Sample texture with distorted coordinates
    fragColor = texture(u_image, distortedUV);
}
```

#### Procedural Noise Pattern

```glsl
#version 460 core
precision highp float;
#include <flutter/runtime_effects.glsl>

uniform float u_time;
uniform vec2 u_resolution;
uniform float u_scale;

out vec4 fragColor;

// Simple hash function for pseudo-random noise
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// Smooth noise
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f); // Smoothstep

    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

void main() {
    vec2 uv = FlutterFragCoord().xy / u_resolution;

    // Animated noise
    float n = noise(uv * u_scale + u_time * 0.5);

    fragColor = vec4(vec3(n), 1.0);
}
```

#### Color Grading / Filter

```glsl
#version 460 core
precision highp float;
#include <flutter/runtime_effects.glsl>

uniform sampler2D u_image;
uniform vec2 u_resolution;
uniform float u_brightness;    // -1.0 to 1.0
uniform float u_contrast;      // 0.0 to 2.0
uniform float u_saturation;    // 0.0 to 2.0

out vec4 fragColor;

void main() {
    vec2 uv = FlutterFragCoord().xy / u_resolution;
    vec4 color = texture(u_image, uv);

    // Apply brightness
    color.rgb += u_brightness;

    // Apply contrast
    color.rgb = ((color.rgb - 0.5) * u_contrast) + 0.5;

    // Apply saturation
    float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    color.rgb = mix(vec3(gray), color.rgb, u_saturation);

    fragColor = color;
}
```

## Dart Integration: FragmentProgram API

### 1. Loading Shaders Asynchronously

```dart
import 'dart:ui' as ui;
import 'package:flutter/material.dart';

class ShaderLoader {
  static Future<ui.FragmentProgram> loadShader(String assetPath) async {
    // Load the compiled shader from assets
    return await ui.FragmentProgram.fromAsset(assetPath);
  }
}

// Usage in StatefulWidget
class ShaderWidget extends StatefulWidget {
  @override
  _ShaderWidgetState createState() => _ShaderWidgetState();
}

class _ShaderWidgetState extends State<ShaderWidget> {
  ui.FragmentProgram? _program;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadShader();
  }

  Future<void> _loadShader() async {
    _program = await ShaderLoader.loadShader('shaders/gradient.frag');
    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return CircularProgressIndicator();
    }

    return CustomPaint(
      size: Size(300, 300),
      painter: ShaderPainter(program: _program!),
    );
  }
}
```

**FragmentProgram Characteristics:**
- Asynchronous loading required
- Represents compiled shader program
- Can create multiple FragmentShader instances
- One-time load, reusable across frames

### 2. Creating and Configuring FragmentShader

```dart
import 'dart:ui' as ui;

class ShaderPainter extends CustomPainter {
  final ui.FragmentProgram program;
  final double time;
  final Color color1;
  final Color color2;

  ShaderPainter({
    required this.program,
    required this.time,
    required this.color1,
    required this.color2,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Create shader instance
    final shader = program.fragmentShader();

    // Set uniforms
    // Order must match shader uniform declarations
    shader.setFloat(0, time);                    // u_time
    shader.setFloat(1, size.width);              // u_resolution.x
    shader.setFloat(2, size.height);             // u_resolution.y
    shader.setFloat(3, color1.red / 255.0);      // u_color1.r
    shader.setFloat(4, color1.green / 255.0);    // u_color1.g
    shader.setFloat(5, color1.blue / 255.0);     // u_color1.b
    shader.setFloat(6, color1.alpha / 255.0);    // u_color1.a
    shader.setFloat(7, color2.red / 255.0);      // u_color2.r
    shader.setFloat(8, color2.green / 255.0);    // u_color2.g
    shader.setFloat(9, color2.blue / 255.0);     // u_color2.b
    shader.setFloat(10, color2.alpha / 255.0);   // u_color2.a

    // Create Paint with shader
    final paint = Paint()..shader = shader;

    // Draw rectangle filled with shader
    canvas.drawRect(
      Rect.fromLTWH(0, 0, size.width, size.height),
      paint,
    );
  }

  @override
  bool shouldRepaint(ShaderPainter oldDelegate) {
    return oldDelegate.time != time ||
           oldDelegate.color1 != color1 ||
           oldDelegate.color2 != color2;
  }
}
```

**Setting Uniforms:**

```dart
// setFloat(index, value) - For all numeric types
shader.setFloat(0, floatValue);           // float
shader.setFloat(1, vec2.x);               // vec2 (2 consecutive indices)
shader.setFloat(2, vec2.y);
shader.setFloat(3, vec3.r);               // vec3 (3 consecutive indices)
shader.setFloat(4, vec3.g);
shader.setFloat(5, vec3.b);
shader.setFloat(6, vec4.r);               // vec4 (4 consecutive indices)
shader.setFloat(7, vec4.g);
shader.setFloat(8, vec4.b);
shader.setFloat(9, vec4.a);

// setImageSampler(index, image) - For sampler2D
shader.setImageSampler(10, uiImage);      // ui.Image object
```

**Critical: Uniform Index Order**
- Indices must match the order of uniform declarations in GLSL
- Each vec2 consumes 2 indices, vec3 consumes 3, vec4 consumes 4
- Count from 0, incrementing for each float component

### 3. Setting Image Samplers

```dart
import 'dart:ui' as ui;

class ImageShaderPainter extends CustomPainter {
  final ui.FragmentProgram program;
  final ui.Image image;
  final double intensity;

  ImageShaderPainter({
    required this.program,
    required this.image,
    required this.intensity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final shader = program.fragmentShader();

    // Set scalar uniforms
    shader.setFloat(0, size.width);
    shader.setFloat(1, size.height);
    shader.setFloat(2, intensity);

    // Set image sampler (must be ui.Image, not ImageProvider)
    shader.setImageSampler(3, image);

    final paint = Paint()..shader = shader;
    canvas.drawRect(Offset.zero & size, paint);
  }

  @override
  bool shouldRepaint(ImageShaderPainter oldDelegate) {
    return oldDelegate.image != image ||
           oldDelegate.intensity != intensity;
  }
}

// Loading ui.Image from asset
Future<ui.Image> loadUiImage(String assetPath) async {
  final data = await rootBundle.load(assetPath);
  final codec = await ui.instantiateImageCodec(data.buffer.asUint8List());
  final frame = await codec.getNextFrame();
  return frame.image;
}
```

**Image Sampler Requirements:**
- Must be `ui.Image` (not `ImageProvider` or `Image` widget)
- Load asynchronously using `instantiateImageCodec`
- Store in State to avoid reloading every frame

## Animated Shaders

### Complete Example: Animated Ripple Effect

```dart
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class AnimatedRippleShader extends StatefulWidget {
  @override
  _AnimatedRippleShaderState createState() => _AnimatedRippleShaderState();
}

class _AnimatedRippleShaderState extends State<AnimatedRippleShader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  ui.FragmentProgram? _program;
  ui.Image? _image;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();

    // Initialize animation controller
    _controller = AnimationController(
      duration: Duration(seconds: 3),
      vsync: this,
    )..repeat();

    _loadResources();
  }

  Future<void> _loadResources() async {
    // Load shader
    _program = await ui.FragmentProgram.fromAsset('shaders/ripple.frag');

    // Load image
    final data = await rootBundle.load('assets/images/background.png');
    final codec = await ui.instantiateImageCodec(data.buffer.asUint8List());
    final frame = await codec.getNextFrame();
    _image = frame.image;

    setState(() {
      _isLoading = false;
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Center(child: CircularProgressIndicator());
    }

    return GestureDetector(
      onTapDown: (details) {
        // Could trigger ripple at tap position
      },
      child: CustomPaint(
        size: Size(400, 400),
        painter: RipplePainter(
          program: _program!,
          image: _image!,
          animation: _controller,
        ),
      ),
    );
  }
}

class RipplePainter extends CustomPainter {
  final ui.FragmentProgram program;
  final ui.Image image;
  final Animation<double> animation;

  RipplePainter({
    required this.program,
    required this.image,
    required this.animation,
  }) : super(repaint: animation); // KEY: Optimized repainting

  @override
  void paint(Canvas canvas, Size size) {
    final shader = program.fragmentShader();

    // Set uniforms
    shader.setFloat(0, animation.value * 10.0);  // u_time
    shader.setFloat(1, size.width);              // u_resolution.x
    shader.setFloat(2, size.height);             // u_resolution.y
    shader.setFloat(3, size.width / 2);          // u_center.x
    shader.setFloat(4, size.height / 2);         // u_center.y
    shader.setFloat(5, 0.3);                     // u_intensity
    shader.setImageSampler(6, image);            // u_image

    final paint = Paint()..shader = shader;
    canvas.drawRect(Offset.zero & size, paint);
  }

  @override
  bool shouldRepaint(RipplePainter oldDelegate) {
    // Animation handled by repaint parameter
    return false;
  }
}
```

**Performance Pattern:**
1. Pass AnimationController as `repaint` parameter to CustomPainter
2. Update shader uniforms in paint() using animation.value
3. Return `false` from shouldRepaint (animation triggers repaints)
4. Result: Only paint() executes per frame, skipping build/layout

## Performance Optimization

### 1. Shader Compilation and Caching

**Shader Warm-up Strategy:**

```dart
class ShaderCache {
  static final Map<String, ui.FragmentProgram> _cache = {};

  static Future<ui.FragmentProgram> load(String assetPath) async {
    if (_cache.containsKey(assetPath)) {
      return _cache[assetPath]!;
    }

    final program = await ui.FragmentProgram.fromAsset(assetPath);
    _cache[assetPath] = program;
    return program;
  }

  static Future<void> warmUp(List<String> shaderPaths) async {
    await Future.wait(
      shaderPaths.map((path) => load(path)),
    );
  }
}

// In app initialization
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Warm up shaders before app starts
  await ShaderCache.warmUp([
    'shaders/gradient.frag',
    'shaders/ripple.frag',
    'shaders/blur.frag',
  ]);

  runApp(MyApp());
}
```

**Benefits:**
- Prevents first-frame stutter from shader compilation
- Reuses FragmentProgram instances
- Reduces memory overhead

### 2. Uniform Update Optimization

```dart
// ❌ BAD: Creating new shader instance every frame
@override
void paint(Canvas canvas, Size size) {
  final shader = program.fragmentShader(); // Allocation every frame
  shader.setFloat(0, time);
  // ...
}

// ✅ GOOD: Reuse shader instance
class OptimizedShaderPainter extends CustomPainter {
  final ui.FragmentProgram program;
  final Animation<double> animation;
  late final ui.FragmentShader _shader; // Persistent shader instance

  OptimizedShaderPainter({
    required this.program,
    required this.animation,
  }) : super(repaint: animation) {
    _shader = program.fragmentShader();
  }

  @override
  void paint(Canvas canvas, Size size) {
    // Only update uniforms, reuse shader instance
    _shader.setFloat(0, animation.value);
    _shader.setFloat(1, size.width);
    _shader.setFloat(2, size.height);

    final paint = Paint()..shader = _shader;
    canvas.drawRect(Offset.zero & size, paint);
  }

  @override
  bool shouldRepaint(OptimizedShaderPainter oldDelegate) => false;
}
```

### 3. Complexity Management

**GLSL Performance Tips:**

```glsl
// ✅ GOOD: Minimize complex math operations
float distance_squared(vec2 a, vec2 b) {
    vec2 diff = a - b;
    return dot(diff, diff); // Faster than sqrt(distance())
}

// ❌ AVOID: Expensive operations in loops
for (int i = 0; i < 100; i++) {
    color += sin(uv.x * float(i)) * cos(uv.y * float(i)); // Very slow
}

// ✅ BETTER: Precompute or simplify
float noise_approx = sin(uv.x * 10.0) * cos(uv.y * 10.0); // Single calculation

// Use built-in functions when possible
float smoothValue = smoothstep(0.0, 1.0, value); // Optimized by GPU
```

**Branching Considerations:**
- Avoid divergent branches (different execution paths for neighboring fragments)
- Prefer `mix()` over `if/else` when possible
- Uniform-based branches are okay (all fragments take same path)

## Troubleshooting

### Shader Not Rendering

**Check:**
1. Shader declared in `pubspec.yaml` under `shaders:` (not `assets:`)
2. File has `.frag` extension
3. Shader loaded successfully (check for exceptions)
4. Uniform indices match GLSL declaration order
5. FragmentShader assigned to Paint.shader
6. Canvas drawing call executed (drawRect, drawPath, etc.)

### Black or Incorrect Output

**Common Causes:**
```glsl
// ❌ Forgot to set alpha channel
fragColor = vec3(r, g, b); // Wrong: vec3, should be vec4
// ✅ Correct
fragColor = vec4(r, g, b, 1.0);

// ❌ Values out of range [0.0, 1.0]
fragColor = vec4(255, 128, 64, 1.0); // Wrong: 0-255 scale
// ✅ Correct: Normalize to 0.0-1.0
fragColor = vec4(1.0, 0.5, 0.25, 1.0);

// ❌ Uninitialized uniforms from Dart
shader.setFloat(0, time); // Only set index 0
// shader still has garbage data at indices 1, 2, 3...
// ✅ Set ALL uniforms used in shader
```

### Performance Issues

**Symptoms:** Low FPS, stuttering

**Solutions:**
1. Simplify shader logic (reduce math operations)
2. Cache FragmentProgram and FragmentShader instances
3. Use `repaint` parameter for animations
4. Warm up shaders at app start
5. Profile with Flutter DevTools GPU metrics

### Uniform Index Confusion

**Solution:** Document uniform indices clearly:

```dart
// ShaderUniforms.dart - Centralized uniform management
class RippleUniforms {
  static const int time = 0;
  static const int resolutionX = 1;
  static const int resolutionY = 2;
  static const int centerX = 3;
  static const int centerY = 4;
  static const int intensity = 5;
  static const int imageSampler = 6;

  static void apply(
    ui.FragmentShader shader,
    double time,
    Size size,
    Offset center,
    double intensity,
    ui.Image image,
  ) {
    shader.setFloat(RippleUniforms.time, time);
    shader.setFloat(RippleUniforms.resolutionX, size.width);
    shader.setFloat(RippleUniforms.resolutionY, size.height);
    shader.setFloat(RippleUniforms.centerX, center.dx);
    shader.setFloat(RippleUniforms.centerY, center.dy);
    shader.setFloat(RippleUniforms.intensity, intensity);
    shader.setImageSampler(RippleUniforms.imageSampler, image);
  }
}
```

## Integration with Other Skills

This skill combines with:

- **flutter-custom-painter** - Apply shaders to Paint objects in CustomPainter
- **flutter-explicit-animations** - Animate shader uniforms smoothly
- **flutter-performance-optimization** - Profile and optimize shader performance
- **flutter-widget-previewer** - Preview shader-based components
- **flutter-asset-codegen** - Type-safe shader asset references

## Additional Resources

- **Official Shader Documentation:** https://docs.flutter.dev/ui/design/graphics/fragment-shaders
- **GLSL ES 3.0 Specification:** https://www.khronos.org/registry/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf
- **Shader Toy (inspiration and examples):** https://www.shadertoy.com/
- **The Book of Shaders:** https://thebookofshaders.com/
- **Flutter FragmentProgram API:** https://api.flutter.dev/flutter/dart-ui/FragmentProgram-class.html

Fragment shaders unlock GPU-accelerated graphics capabilities, enabling Flutter applications to achieve visual effects previously impossible with CPU-only rendering.
