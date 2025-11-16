---
name: flutter-performance-optimization
description: Comprehensive guide for optimizing Flutter application performance to achieve smooth 60fps (or 120fps) rendering. This skill should be used when addressing performance issues, frame drops (jank), slow build times, or optimizing for production deployment. Covers the 16ms frame budget, build() optimization, efficient rendering, RepaintBoundary usage, profiling with DevTools, and best practices for maintaining optimal performance.
---

# Flutter Performance Optimization

## Overview

Flutter's performance goal is to deliver smooth, fluid user experiences at 60 frames per second (fps) on standard displays, or 120fps on high refresh rate screens. Achieving this requires understanding the rendering pipeline, optimizing expensive operations, and following performance best practices throughout development.

**Core Performance Principle:**
Each frame must render in approximately **16 milliseconds (ms)** for 60fps (or 8ms for 120fps). Any frame exceeding this budget results in "jank" (dropped frames causing stuttering motion).

**Version Compatibility:**
- All Flutter versions
- Latest guidance: Flutter 3.38 (2025)
- Performance tools: Flutter DevTools

**Official Resources:**
- Performance Best Practices: https://docs.flutter.dev/perf/best-practices
- Performance View: https://docs.flutter.dev/tools/devtools/performance
- Performance Documentation: https://docs.flutter.dev/perf

**Key Performance Metrics:**
- **Frame Time:** Should be ≤16ms for 60fps
- **Build Time:** Time spent in widget build() methods
- **Layout Time:** Time calculating widget sizes and positions
- **Paint Time:** Time rendering to screen
- **Raster Time:** GPU time for final frame composition

## The 16ms Frame Budget

### Understanding the Rendering Pipeline

Flutter's rendering has two threads:

**1. UI Thread (Dart):**
```
Build → Layout → Paint → Compose Layers
```

**2. Raster Thread (GPU):**
```
Rasterize Layers → Display
```

**Critical:** Both threads must complete within 16ms for 60fps.

```
Frame 1: |←---- 16ms ---->|
         [UI Thread: 12ms ][Raster: 4ms ]  ✅ Good

Frame 2: |←---- 16ms ---->|
         [UI Thread: 18ms ][Raster: 5ms ]  ❌ Jank!
         Exceeds budget by 7ms
```

### Measuring Performance

**Always profile on physical devices in profile mode:**

```bash
# Profile mode (optimized, with performance tools)
flutter run --profile

# NEVER profile in debug mode (adds expensive checks)
# NEVER profile on emulators/simulators (not representative)
```

**Profile Mode Characteristics:**
- Optimizations enabled (like release mode)
- Performance overlay available
- DevTools profiling enabled
- More accurate performance measurements

## Build() Method Optimization

### 1. Const Constructors

**Impact:** Prevents unnecessary widget rebuilds

```dart
// ❌ BAD: Widget rebuilt every time parent rebuilds
class ParentWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Title'),              // Rebuilt unnecessarily
        Container(color: Colors.blue),  // Rebuilt unnecessarily
        DynamicWidget(),            // Actually needs rebuild
      ],
    );
  }
}

// ✅ GOOD: Static widgets marked const
class ParentWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: const [
        Text('Title'),              // Const: Never rebuilt
        SizedBox(height: 16),       // Const: Never rebuilt
        // DynamicWidget() cannot be const - that's okay
      ] + [
        DynamicWidget(),            // Only this rebuilds
      ],
    );
  }
}

// ✅ BETTER: Extract static content
class ParentWidget extends StatelessWidget {
  static const _header = Text('Title');
  static const _spacer = SizedBox(height: 16);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _header,
        _spacer,
        DynamicWidget(),
      ],
    );
  }
}
```

**When to Use Const:**
- Static text, icons, padding
- Fixed-size boxes (SizedBox)
- Widgets with all const parameters
- Decorations and borders with fixed values

### 2. Avoid Expensive Operations in build()

```dart
// ❌ BAD: Expensive operations in build()
class BadWidget extends StatelessWidget {
  final List<int> data;

  BadWidget(this.data);

  @override
  Widget build(BuildContext context) {
    // ❌ Complex computation in build
    final processedData = data
        .where((x) => x > 0)
        .map((x) => x * 2)
        .toList()
      ..sort();

    // ❌ DateTime.now() reads system clock every build
    final currentTime = DateTime.now();

    // ❌ Creating new objects every build
    final controller = TextEditingController(text: 'Default');

    return ListView.builder(
      itemCount: processedData.length,
      itemBuilder: (context, index) {
        return Text('${processedData[index]} at $currentTime');
      },
    );
  }
}

// ✅ GOOD: Pre-compute or cache expensive operations
class GoodWidget extends StatefulWidget {
  final List<int> data;

  GoodWidget(this.data);

  @override
  _GoodWidgetState createState() => _GoodWidgetState();
}

class _GoodWidgetState extends State<GoodWidget> {
  late List<int> _processedData;
  late TextEditingController _controller;
  late String _timestamp;

  @override
  void initState() {
    super.initState();
    // ✅ Compute once in initState
    _processedData = widget.data
        .where((x) => x > 0)
        .map((x) => x * 2)
        .toList()
      ..sort();

    _controller = TextEditingController(text: 'Default');
    _timestamp = DateTime.now().toString();
  }

  @override
  void didUpdateWidget(GoodWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    // ✅ Recompute only when data changes
    if (oldWidget.data != widget.data) {
      _processedData = widget.data
          .where((x) => x > 0)
          .map((x) => x * 2)
          .toList()
        ..sort();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: _processedData.length,
      itemBuilder: (context, index) {
        return Text('${_processedData[index]} at $_timestamp');
      },
    );
  }
}
```

**Build() Golden Rules:**
1. No expensive computations
2. No network calls or file I/O
3. No object creation that persists (controllers, animators)
4. Minimal work - just compose widgets

### 3. Widget Extraction and Separation

```dart
// ❌ BAD: Monolithic build method
class ComplexScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Complex Screen'),
        actions: [
          IconButton(icon: Icon(Icons.search), onPressed: () {}),
          IconButton(icon: Icon(Icons.settings), onPressed: () {}),
        ],
      ),
      body: Column(
        children: [
          Container(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(Icons.person, size: 48),
                SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('John Doe', style: TextStyle(fontSize: 24)),
                    Text('john@example.com'),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: 100,
              itemBuilder: (context, index) {
                return Card(
                  child: ListTile(
                    leading: CircleAvatar(child: Text('$index')),
                    title: Text('Item $index'),
                    subtitle: Text('Subtitle for item $index'),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

// ✅ GOOD: Extracted components
class ComplexScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(),
      body: Column(
        children: [
          const UserHeader(), // Extracted as separate widget
          Expanded(child: ItemList()),
        ],
      ),
    );
  }

  AppBar _buildAppBar() {
    return AppBar(
      title: const Text('Complex Screen'),
      actions: const [
        _SearchButton(),
        _SettingsButton(),
      ],
    );
  }
}

class UserHeader extends StatelessWidget {
  const UserHeader();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: const [
          Icon(Icons.person, size: 48),
          SizedBox(width: 16),
          _UserInfo(),
        ],
      ),
    );
  }
}

class _UserInfo extends StatelessWidget {
  const _UserInfo();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Text('John Doe', style: TextStyle(fontSize: 24)),
        Text('john@example.com'),
      ],
    );
  }
}

class _SearchButton extends StatelessWidget {
  const _SearchButton();

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.search),
      onPressed: () {},
    );
  }
}

class _SettingsButton extends StatelessWidget {
  const _SettingsButton();

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.settings),
      onPressed: () {},
    );
  }
}

class ItemList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: 100,
      itemBuilder: (context, index) {
        return ItemCard(index: index);
      },
    );
  }
}

class ItemCard extends StatelessWidget {
  final int index;

  const ItemCard({required this.index});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(child: Text('$index')),
        title: Text('Item $index'),
        subtitle: Text('Subtitle for item $index'),
      ),
    );
  }
}
```

**Benefits of Extraction:**
- Smaller build() methods
- Independent rebuilds (only changed widgets rebuild)
- Better code organization
- Easier testing
- Const optimization opportunities

## Efficient List and Grid Rendering

### 1. Builder Constructors (Lazy Loading)

```dart
// ❌ BAD: Creates all widgets upfront
ListView(
  children: List.generate(
    10000,
    (index) => ListTile(title: Text('Item $index')),
  ),
)
// Creates 10,000 widgets immediately - massive memory waste!

// ✅ GOOD: Lazy instantiation
ListView.builder(
  itemCount: 10000,
  itemBuilder: (context, index) {
    return ListTile(title: Text('Item $index'));
  },
)
// Only creates visible widgets (~10-20), rest on-demand

// ✅ GOOD: GridView builder
GridView.builder(
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 2,
  ),
  itemCount: 10000,
  itemBuilder: (context, index) {
    return Card(child: Center(child: Text('$index')));
  },
)
```

**Builder Benefits:**
- Only visible items created
- Automatic widget recycling
- Constant memory usage regardless of list length
- Smooth scrolling performance

### 2. ListView.separated for Dividers

```dart
// ❌ BAD: Manually adding dividers
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return Column(
      children: [
        ListTile(title: Text(items[index])),
        if (index != items.length - 1) Divider(), // Conditional divider
      ],
    );
  },
)

// ✅ GOOD: Automatic separator
ListView.separated(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(title: Text(items[index]));
  },
  separatorBuilder: (context, index) {
    return Divider();
  },
)
```

### 3. ListView Optimization Settings

```dart
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(items[index]),

  // Cache extent (pixels to keep alive outside viewport)
  cacheExtent: 100, // Default: viewport height * 2

  // Item extent (if all items same height)
  itemExtent: 80, // Skips expensive height calculations

  // Scroll physics
  physics: const AlwaysScrollableScrollPhysics(),
)
```

**itemExtent Benefits:**
- Skips layout phase for each item
- Instant scroll position calculations
- Significant performance improvement for long lists

## RepaintBoundary for Isolation

### When to Use RepaintBoundary

RepaintBoundary isolates widgets to prevent unnecessary repaints:

```dart
// Scenario: Animated widget alongside static content
class MixedContent extends StatefulWidget {
  @override
  _MixedContentState createState() => _MixedContentState();
}

class _MixedContentState extends State<MixedContent>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(seconds: 2),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // ✅ Static content isolated from animation repaints
        RepaintBoundary(
          child: ComplexStaticWidget(), // Won't repaint during animation
        ),

        // Animated content
        AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Transform.rotate(
              angle: _controller.value * 2 * 3.14159,
              child: Container(
                width: 100,
                height: 100,
                color: Colors.blue,
              ),
            );
          },
        ),

        // ✅ Another static section isolated
        RepaintBoundary(
          child: AnotherComplexWidget(),
        ),
      ],
    );
  }
}
```

**RepaintBoundary Use Cases:**
- Static content near animations
- Complex widgets that rarely change
- Isolating expensive CustomPaint widgets
- ListView items with independent repaints

**Cost-Benefit Analysis:**
- **Cost:** Additional memory for cached layer
- **Benefit:** Avoids expensive repaints
- **Rule:** Use when repaint cost > memory cost

```dart
// ❌ DON'T overuse RepaintBoundary
// Every widget doesn't need isolation
Container(
  child: RepaintBoundary( // Unnecessary overhead
    child: Text('Static Text'),
  ),
)

// ✅ DO use for expensive, independent content
CustomPaint(
  painter: ExpensiveChartPainter(),
  child: RepaintBoundary( // Justified: expensive chart
    child: child,
  ),
)
```

## Expensive Operations to Avoid

### 1. Opacity Widget

```dart
// ❌ BAD: Opacity widget (expensive, forces offscreen buffer)
Opacity(
  opacity: 0.5,
  child: ComplexWidget(),
)

// ✅ GOOD: Use color with alpha instead
Container(
  color: Colors.blue.withOpacity(0.5), // Direct alpha, no offscreen buffer
  child: ComplexWidget(),
)

// ✅ For animations, use specialized widgets
FadeTransition(
  opacity: _animation,
  child: ComplexWidget(),
)

// ✅ Or AnimatedOpacity for implicit animations
AnimatedOpacity(
  opacity: _isVisible ? 1.0 : 0.0,
  duration: Duration(milliseconds: 300),
  child: ComplexWidget(),
)
```

**Why Opacity is Expensive:**
- Renders child to offscreen buffer
- Applies alpha, then composites back
- Use color alpha or FadeTransition instead

### 2. ClipPath and ClipRRect

```dart
// ❌ EXPENSIVE: Complex clipping paths
ClipPath(
  clipper: ComplexCustomClipper(), // Custom path calculation + clipping
  child: Image.network('...'),
)

// ✅ BETTER: Use built-in, optimized clipping when possible
ClipRRect(
  borderRadius: BorderRadius.circular(12),
  child: Image.network('...'),
)

// ✅ BEST: No clipping if possible
Container(
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(12),
    image: DecorationImage(
      image: NetworkImage('...'),
      fit: BoxFit.cover,
    ),
  ),
)
```

### 3. saveLayer() in CustomPainter

```dart
// ❌ EXPENSIVE: saveLayer forces offscreen rendering
class ExpensivePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    canvas.saveLayer(null, Paint()..color = Colors.blue.withOpacity(0.5));
    // ... drawing operations
    canvas.restore();
  }

  @override
  bool shouldRepaint(ExpensivePainter oldDelegate) => false;
}

// ✅ BETTER: Apply effects directly to Paint
class OptimizedPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = Colors.blue.withOpacity(0.5);
    // ... drawing operations with configured paint
  }

  @override
  bool shouldRepaint(OptimizedPainter oldDelegate) => false;
}
```

**Only use saveLayer when:**
- Applying multiple blend modes
- Complex compositing required
- No alternative approach exists

## Image Optimization

### 1. Proper Image Sizing

```dart
// ❌ BAD: Loading full-resolution image for small display
Image.network(
  'https://example.com/4k-image.jpg', // 4K image
  width: 100, // Displayed at 100x100
  height: 100,
)
// Wastes memory and bandwidth

// ✅ GOOD: Load appropriately sized image
Image.network(
  'https://example.com/thumbnail-100.jpg', // Pre-sized thumbnail
  width: 100,
  height: 100,
)

// ✅ Use cacheWidth/cacheHeight to resize during decode
Image.network(
  'https://example.com/large-image.jpg',
  cacheWidth: 100, // Decode at smaller size
  cacheHeight: 100,
)
```

### 2. Image Caching

```dart
// ✅ Use cached_network_image package
import 'package:cached_network_image/cached_network_image.dart';

CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
  // Automatic disk and memory caching
)
```

### 3. Lazy Image Loading

```dart
// ✅ Load images only when visible
ListView.builder(
  itemCount: images.length,
  itemBuilder: (context, index) {
    return CachedNetworkImage(
      imageUrl: images[index],
      // Only loads when item scrolls into view
    );
  },
)
```

## Profiling with Flutter DevTools

### 1. Performance Overlay

```dart
// Enable in-app performance overlay
MaterialApp(
  showPerformanceOverlay: true, // Shows FPS and frame time
  // ...
)
```

**Overlay Metrics:**
- **Green bar:** UI thread time (should be <16ms)
- **Red bar:** Raster thread time (should be <16ms)
- **Graph:** Frame time history

### 2. DevTools Performance View

**Accessing DevTools:**

```bash
# Start app in profile mode
flutter run --profile

# DevTools automatically opens in browser
# Or manually open: http://localhost:port/
```

**Performance View Features:**
- Frame timeline
- CPU profiler
- Memory profiler
- GPU metrics

**Identifying Bottlenecks:**

1. **Build Phase Slow:**
   - Expensive build() methods
   - Too many widgets
   - Missing const constructors

2. **Layout Phase Slow:**
   - Complex nested layouts
   - Missing itemExtent in lists
   - Intrinsic sizing widgets

3. **Paint Phase Slow:**
   - Complex CustomPainter
   - Missing RepaintBoundary
   - Expensive opacity/clipping

4. **Raster Phase Slow:**
   - Too many layers
   - Shader compilation
   - Complex paths or gradients

## Checklist for Production

**Before Release:**

```yaml
# ✅ Build in release mode
flutter build apk --release
flutter build ios --release

# ✅ Enable code shrinking (Android)
# android/app/build.gradle
buildTypes {
  release {
    minifyEnabled true
    shrinkResources true
  }
}

# ✅ Optimize images
# Use compressed formats (WebP for Android, HEIC for iOS)
# Generate multiple resolutions (@2x, @3x)
```

**Performance Checklist:**

- [ ] Profiled on slowest target device
- [ ] No frames >16ms in common scenarios
- [ ] Const constructors used extensively
- [ ] ListView/GridView use .builder()
- [ ] No expensive operations in build()
- [ ] Images appropriately sized
- [ ] RepaintBoundary used for expensive static content
- [ ] Animations use AnimatedBuilder (not setState)
- [ ] No Opacity widget (use FadeTransition)
- [ ] Minimal ClipPath usage
- [ ] Controllers disposed properly

## Troubleshooting

### High Build Time

**Solutions:**
1. Extract widgets into separate classes
2. Add const constructors
3. Cache expensive computations
4. Reduce widget tree depth

### High Paint Time

**Solutions:**
1. Add RepaintBoundary around static content
2. Optimize CustomPainter (return false from shouldRepaint when possible)
3. Reduce complexity of drawn shapes
4. Use cached images

### High Raster Time

**Solutions:**
1. Reduce number of layers
2. Simplify gradients and shaders
3. Warm up shaders at startup
4. Use simpler blend modes

### Memory Growth

**Solutions:**
1. Dispose controllers and listeners
2. Use ListView.builder (not ListView with all children)
3. Implement image caching
4. Check for memory leaks with DevTools memory profiler

## Integration with Other Skills

Combine with:

- **flutter-explicit-animations** - Optimize animation performance with AnimatedBuilder
- **flutter-custom-painter** - Efficient CustomPainter implementation
- **flutter-fragment-shaders** - GPU shader optimization
- **flutter-widget-previewer** - Test component performance in isolation
- **material-design-3-flutter** - Use performant Material components

## Additional Resources

- **Performance Best Practices:** https://docs.flutter.dev/perf/best-practices
- **Performance View Guide:** https://docs.flutter.dev/tools/devtools/performance
- **Flutter Performance Documentation:** https://docs.flutter.dev/perf
- **Rendering Pipeline:** https://docs.flutter.dev/resources/architectural-overview#rendering-and-layout

Maintaining 60fps performance requires continuous attention throughout development, profiling on real devices, and applying optimization best practices.
