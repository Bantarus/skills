---
name: flutter-asset-codegen
description: Comprehensive guide for implementing type-safe asset management in Flutter using flutter_gen and build_runner for code generation. This skill should be used when setting up asset management, eliminating string-based asset references, ensuring compile-time asset validation, or building professional Flutter applications with reliable asset access. Covers flutter_gen configuration, build_runner usage, generated API access, and integration with images, fonts, colors, and shaders.
---

# Flutter Type-Safe Asset Management with Code Generation

## Overview

Type-safe asset management eliminates runtime errors from typos in asset paths by generating compile-time checked Dart code for all project assets. Using flutter_gen with build_runner automatically creates strongly-typed classes for images, fonts, colors, and other assets declared in pubspec.yaml.

**Core Benefits:**
- **Compile-Time Safety:** Typos caught during development, not runtime
- **IDE Autocomplete:** Full IntelliSense support for all assets
- **Refactoring Support:** Rename detection and safe refactoring
- **Type Safety:** No string literals for asset paths
- **Maintainability:** Centralized asset management

**Key Packages:**
- **flutter_gen** - Asset code generator
- **flutter_gen_runner** - Build runner integration
- **build_runner** - Code generation execution

**Official Resources:**
- flutter_gen Package: https://pub.dev/packages/flutter_gen
- flutter_gen GitHub: https://github.com/FlutterGen/flutter_gen
- Build Runner: https://pub.dev/packages/build_runner

**Version Compatibility:**
- flutter_gen: Latest stable
- Dart: ≥2.12 (null safety)
- Flutter: All recent versions

**Use Cases:**
- Professional production applications
- Team projects requiring maintainability
- Apps with many assets (images, icons, fonts)
- Projects requiring compile-time validation
- Applications using shaders or custom fonts

## Setup and Configuration

### 1. Installation

Add dependencies to `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_gen_runner: ^5.3.1
  build_runner: ^2.4.6
```

**Note:** flutter_gen_runner and build_runner are dev dependencies (code generation happens during development, not runtime).

### 2. Asset Declaration

Declare assets in `pubspec.yaml` as usual:

```yaml
flutter:
  uses-material-design: true

  assets:
    - assets/images/
    - assets/images/icons/
    - assets/images/backgrounds/
    - assets/json/
    - assets/data/

  fonts:
    - family: Roboto
      fonts:
        - asset: assets/fonts/Roboto-Regular.ttf
        - asset: assets/fonts/Roboto-Bold.ttf
          weight: 700
    - family: CustomIcon
      fonts:
        - asset: assets/fonts/CustomIcon.ttf

  # Fragment shaders (if using)
  shaders:
    - shaders/gradient.frag
    - shaders/ripple.frag
```

### 3. flutter_gen Configuration

Create `build.yaml` in project root for customization (optional):

```yaml
# build.yaml
targets:
  $default:
    builders:
      flutter_gen:
        options:
          # Output directory for generated files
          output: lib/gen/

          # Line length for generated code
          line_length: 80

          # Null safety
          null_safety: true

          # Integrate with flutter_svg (if using SVG images)
          integrations:
            flutter_svg: true

          # Color generation from file names
          colors:
            enabled: true
```

**Configuration Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `output` | `lib/gen/` | Generated code directory |
| `line_length` | `80` | Code formatting line length |
| `null_safety` | `true` | Generate null-safe code |
| `integrations.flutter_svg` | `false` | Enable SVG support |
| `integrations.flare_flutter` | `false` | Enable Flare support |
| `colors.enabled` | `false` | Generate color classes |

### 4. Generate Code

Run build_runner to generate asset code:

```bash
# One-time generation
flutter pub run build_runner build

# Watch mode (auto-regenerate on changes)
flutter pub run build_runner watch

# Clean and rebuild
flutter pub run build_runner build --delete-conflicting-outputs
```

**Generated Output:**

```
lib/
  gen/
    assets.gen.dart       # Main generated file
    colors.gen.dart       # Generated colors (if enabled)
    fonts.gen.dart        # Generated font families
```

## Generated API Usage

### 1. Image Assets

**Before (String-Based):**

```dart
// ❌ String literals - prone to typos, no autocomplete
Image.asset('assets/images/logo.png')
Image.asset('assets/images/icons/home.png')
Image.asset('assts/images/backgrund.jpg')  // Typo! Runtime error!
```

**After (Type-Safe):**

```dart
import 'package:your_app/gen/assets.gen.dart';

// ✅ Type-safe, autocomplete, compile-time checked
Assets.images.logo.image()
Assets.images.icons.home.image()
Assets.images.background.image()  // Compiler error if missing!
```

**Generated Image API:**

```dart
// Direct Image widget
Assets.images.logo.image(
  width: 200,
  height: 100,
  fit: BoxFit.cover,
)

// AssetImage for ImageProvider context
Container(
  decoration: BoxDecoration(
    image: DecorationImage(
      image: Assets.images.background.provider(),
      fit: BoxFit.cover,
    ),
  ),
)

// Raw path string (when needed)
final path = Assets.images.logo.path;  // 'assets/images/logo.png'

// NetworkImage alternative not available - use regular Image.network
```

**Directory Structure Mapping:**

```
assets/
  images/
    logo.png              → Assets.images.logo
    icon.svg              → Assets.images.icon
    backgrounds/
      mountain.jpg        → Assets.images.backgrounds.mountain
      ocean.jpg           → Assets.images.backgrounds.ocean
    icons/
      home.png            → Assets.images.icons.home
      settings.png        → Assets.images.icons.settings
```

### 2. SVG Images (with flutter_svg)

**Setup:**

```yaml
# pubspec.yaml
dependencies:
  flutter_svg: ^2.0.0

dev_dependencies:
  flutter_gen_runner: ^5.3.1
```

```yaml
# build.yaml
targets:
  $default:
    builders:
      flutter_gen:
        options:
          integrations:
            flutter_svg: true  # Enable SVG support
```

**Usage:**

```dart
import 'package:your_app/gen/assets.gen.dart';

// SVG image with flutter_svg
Assets.images.icon.svg(
  width: 24,
  height: 24,
  color: Colors.blue,
)

// SVG as SvgPicture (more control)
SvgPicture(
  Assets.images.icon.provider(),
  width: 24,
  height: 24,
  colorFilter: ColorFilter.mode(Colors.blue, BlendMode.srcIn),
)
```

### 3. Fonts

**Before:**

```dart
// ❌ String literal font family
TextStyle(
  fontFamily: 'Roboto',        // Typo risk
  fontWeight: FontWeight.bold,
)
```

**After:**

```dart
import 'package:your_app/gen/fonts.gen.dart';

// ✅ Type-safe font family
TextStyle(
  fontFamily: FontFamily.roboto,
  fontWeight: FontWeight.bold,
)

TextStyle(
  fontFamily: FontFamily.customIcon,
)
```

**Generated Font Families:**

```dart
// gen/fonts.gen.dart
class FontFamily {
  static const String roboto = 'Roboto';
  static const String customIcon = 'CustomIcon';
}
```

### 4. JSON and Data Files

**Before:**

```dart
// ❌ String path
final data = await rootBundle.loadString('assets/json/config.json');
```

**After:**

```dart
import 'package:your_app/gen/assets.gen.dart';

// ✅ Type-safe path
final data = await rootBundle.loadString(Assets.json.config);
```

### 5. Shaders (Fragment Shaders)

Shader files declared in `pubspec.yaml` under `shaders:` are accessible via generated code:

```yaml
# pubspec.yaml
flutter:
  shaders:
    - shaders/gradient.frag
    - shaders/ripple.frag
```

**Generated Access:**

```dart
import 'dart:ui' as ui;
import 'package:your_app/gen/assets.gen.dart';

// ✅ Type-safe shader path
final program = await ui.FragmentProgram.fromAsset(
  Assets.shaders.gradient,  // 'shaders/gradient.frag'
);

final shader = program.fragmentShader();
// Configure and use shader...
```

**Note:** While shaders are listed separately in pubspec.yaml, flutter_gen treats them as regular assets, making them accessible through the generated code.

### 6. Colors from Asset File Names

**Enable Color Generation:**

```yaml
# build.yaml
targets:
  $default:
    builders:
      flutter_gen:
        options:
          colors:
            enabled: true
```

**Color File Naming Convention:**

```
assets/colors/
  primary_blue.png       → ColorName.primaryBlue
  accent_red.png         → ColorName.accentRed
  background_gray.png    → ColorName.backgroundGray
```

**Usage:**

```dart
import 'package:your_app/gen/colors.gen.dart';

Container(
  color: ColorName.primaryBlue,
)
```

**Note:** This extracts the dominant color from image files. For app-wide color schemes, prefer defining colors in Dart code or ThemeData.

## Advanced Patterns

### 1. Organizing Generated Code

**Recommended Import Pattern:**

```dart
// Create barrel file: lib/gen.dart
export 'gen/assets.gen.dart';
export 'gen/fonts.gen.dart';
export 'gen/colors.gen.dart';

// Import in files
import 'package:your_app/gen.dart';

// Access all generated code
Assets.images.logo.image()
FontFamily.roboto
ColorName.primaryBlue
```

### 2. Extension Methods for Convenience

```dart
// lib/extensions/asset_extensions.dart
import 'package:flutter/widgets.dart';
import 'package:your_app/gen/assets.gen.dart';

extension AssetImageExtension on AssetGenImage {
  // Quick image with common defaults
  Widget thumbnail({double size = 50}) {
    return image(
      width: size,
      height: size,
      fit: BoxFit.cover,
    );
  }

  // Circular avatar
  Widget avatar({double radius = 20}) {
    return CircleAvatar(
      radius: radius,
      backgroundImage: provider(),
    );
  }
}

// Usage
Assets.images.profile.thumbnail(size: 100)
Assets.images.profile.avatar(radius: 30)
```

### 3. Theming with Generated Assets

```dart
import 'package:flutter/material.dart';
import 'package:your_app/gen.dart';

final lightTheme = ThemeData(
  brightness: Brightness.light,
  fontFamily: FontFamily.roboto,
  // Use generated assets for theme
);

final darkTheme = ThemeData(
  brightness: Brightness.dark,
  fontFamily: FontFamily.roboto,
);
```

### 4. Asset Preloading

```dart
import 'package:flutter/material.dart';
import 'package:your_app/gen/assets.gen.dart';

class AssetPreloader {
  static Future<void> preloadImages(BuildContext context) async {
    // Preload critical images
    await Future.wait([
      precacheImage(Assets.images.logo.provider(), context),
      precacheImage(Assets.images.splash.provider(), context),
      precacheImage(Assets.images.backgrounds.main.provider(), context),
    ]);
  }
}

// In main app
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Preload in splash screen or initialization
    AssetPreloader.preloadImages(context);

    return MaterialApp(
      home: HomeScreen(),
    );
  }
}
```

## Integration with Other Tools

### 1. flutter_svg Integration

```yaml
# pubspec.yaml
dependencies:
  flutter_svg: ^2.0.0

# build.yaml
targets:
  $default:
    builders:
      flutter_gen:
        options:
          integrations:
            flutter_svg: true
```

**Generated SVG API:**

```dart
// Automatic SVG support
Assets.images.icon.svg(width: 24, height: 24)
```

### 2. Version Control (.gitignore)

**Add generated files to .gitignore:**

```gitignore
# Generated code
/lib/gen/
*.g.dart
```

**Regenerate in CI/CD:**

```yaml
# .github/workflows/build.yml
- name: Generate code
  run: flutter pub run build_runner build --delete-conflicting-outputs
```

**Note:** Some teams commit generated code to avoid build failures. Choose based on team preference.

## Best Practices

### 1. Asset Organization

```
assets/
  images/
    app/              # App-specific images
      logo.png
      splash.png
    icons/            # UI icons
      home.png
      settings.png
      profile.png
    backgrounds/      # Background images
      gradient.png
      pattern.png
    products/         # Feature-specific
      item_1.jpg
      item_2.jpg
  fonts/              # Custom fonts
    Roboto-Regular.ttf
    Roboto-Bold.ttf
  data/               # JSON, CSV, etc.
    config.json
    mock_data.json
  shaders/            # GLSL shaders
    gradient.frag
    ripple.frag
```

### 2. Naming Conventions

**File Naming:**
- Use snake_case for file names: `primary_button.png`, `user_profile.jpg`
- Generated code uses camelCase: `Assets.images.primaryButton`, `Assets.images.userProfile`
- Avoid special characters and spaces
- Use descriptive names: `icon_home_filled.png` not `icon1.png`

**Directory Naming:**
- Use lowercase: `assets/images/icons/` not `assets/Images/Icons/`
- Group by feature or type
- Keep nesting shallow (2-3 levels max)

### 3. Conditional Asset Loading

```dart
// Load different assets based on platform or condition
Widget _buildLogo(BuildContext context) {
  if (Theme.of(context).brightness == Brightness.dark) {
    return Assets.images.logoDark.image();
  } else {
    return Assets.images.logoLight.image();
  }
}

// Responsive images
Widget _buildBackground(BuildContext context) {
  final isDesktop = MediaQuery.of(context).size.width > 1024;

  return isDesktop
      ? Assets.images.backgrounds.desktop.image(fit: BoxFit.cover)
      : Assets.images.backgrounds.mobile.image(fit: BoxFit.cover);
}
```

### 4. Testing with Generated Assets

```dart
// test/widget_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:your_app/gen/assets.gen.dart';

void main() {
  test('Asset paths are correct', () {
    expect(Assets.images.logo.path, 'assets/images/logo.png');
    expect(Assets.images.icons.home.path, 'assets/images/icons/home.png');
  });

  testWidgets('Logo image loads', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Assets.images.logo.image(),
      ),
    );

    expect(find.byType(Image), findsOneWidget);
  });
}
```

## Workflow Integration

### 1. Development Workflow

```bash
# 1. Add new assets to pubspec.yaml
# 2. Place asset files in directories
# 3. Generate code
flutter pub run build_runner build

# OR: Watch mode for continuous generation
flutter pub run build_runner watch

# 4. Use generated code
import 'package:your_app/gen/assets.gen.dart';
Assets.images.newImage.image()
```

### 2. Team Workflow

**Option A: Commit Generated Code**
- Pros: No build step needed for team members
- Cons: More merge conflicts, larger repo size

**Option B: Ignore Generated Code**
- Pros: Smaller repo, cleaner diffs
- Cons: Every developer runs build_runner

**Recommendation:** Ignore generated code, document build step in README:

```markdown
# Setup

1. Clone repository
2. Run `flutter pub get`
3. Run `flutter pub run build_runner build`
4. Run `flutter run`
```

### 3. CI/CD Integration

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.38.0'

      - name: Install dependencies
        run: flutter pub get

      - name: Generate code
        run: flutter pub run build_runner build --delete-conflicting-outputs

      - name: Run tests
        run: flutter test

      - name: Build APK
        run: flutter build apk --release
```

## Troubleshooting

### Build Fails to Generate

**Check:**
1. pubspec.yaml syntax is correct
2. Assets exist in declared directories
3. flutter_gen_runner in dev_dependencies
4. Run `flutter pub get` before build_runner

### Generated Code Missing Assets

**Solutions:**
1. Verify assets declared in pubspec.yaml
2. Check asset files exist in filesystem
3. Run `flutter pub run build_runner build --delete-conflicting-outputs`
4. Restart IDE for IntelliSense update

### "No such file or directory" Runtime Error

**Causes:**
- Asset declared in pubspec.yaml but file doesn't exist
- Asset file moved/renamed without updating pubspec.yaml
- Typo in asset path in pubspec.yaml

**Solution:**
```bash
# Verify all assets exist
flutter pub run build_runner build

# If errors, check which assets are missing in output
```

### Autocomplete Not Working

**Solutions:**
1. Regenerate code: `flutter pub run build_runner build`
2. Restart IDE / Dart Analysis Server
3. Run `flutter clean` then `flutter pub get`
4. Check import statement: `import 'package:your_app/gen/assets.gen.dart';`

## Integration with Other Skills

This skill complements:

- **flutter-fragment-shaders** - Type-safe shader asset loading
- **flutter-widget-previewer** - Reliable asset references in widget previews
- **material-design-3-flutter** - Type-safe font and color management
- **flutter-performance-optimization** - Structured asset organization improves performance

## Additional Resources

- **flutter_gen Package:** https://pub.dev/packages/flutter_gen
- **flutter_gen GitHub:** https://github.com/FlutterGen/flutter_gen
- **build_runner Documentation:** https://pub.dev/packages/build_runner
- **FreeCodeCamp Tutorial:** https://www.freecodecamp.org/news/how-to-manage-assets-in-flutter-using-fluttergen/
- **Flutter Asset Management:** https://docs.flutter.dev/ui/assets/assets-and-images

Type-safe asset management with code generation eliminates entire categories of runtime errors and significantly improves developer experience and application reliability.
