# Material Design 3 Theming Guide

This reference provides comprehensive guidance on implementing Material Design 3 theming, color schemes, dynamic colors, and custom styling in Flutter applications.

## Overview

Material 3 theming in Flutter is built around the ColorScheme, which provides a cohesive color system that automatically applies across all Material widgets. This ensures visual consistency and accessibility throughout your app.

## Enabling Material 3

Material 3 is enabled by default in Flutter 3.16+. Explicit configuration:

```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,
  ),
)
```

## ColorScheme

### ColorScheme Structure

Material 3 ColorScheme includes:

**Primary Colors:**
- `primary`: Main brand color
- `onPrimary`: Text/icons on primary
- `primaryContainer`: Containers using primary
- `onPrimaryContainer`: Content on primaryContainer

**Secondary Colors:**
- `secondary`: Secondary brand color
- `onSecondary`: Text/icons on secondary
- `secondaryContainer`: Containers using secondary
- `onSecondaryContainer`: Content on secondaryContainer

**Tertiary Colors:**
- `tertiary`: Third accent color
- `onTertiary`: Text/icons on tertiary
- `tertiaryContainer`: Containers using tertiary
- `onTertiaryContainer`: Content on tertiaryContainer

**Error Colors:**
- `error`: Error state color
- `onError`: Text/icons on error
- `errorContainer`: Error containers
- `onErrorContainer`: Content on errorContainer

**Surface Colors (Material 3 new):**
- `surface`: Default surface color
- `onSurface`: Content on surface
- `surfaceDim`: Dimmed surface
- `surfaceBright`: Bright surface
- `surfaceContainerLowest`: Lowest elevation container
- `surfaceContainerLow`: Low elevation container
- `surfaceContainer`: Standard container
- `surfaceContainerHigh`: High elevation container
- `surfaceContainerHighest`: Highest elevation container

**Other Colors:**
- `outline`: Border and divider color
- `outlineVariant`: Subtle borders
- `shadow`: Drop shadow color
- `scrim`: Modal scrim overlay
- `inverseSurface`: Inverse surface color
- `onInverseSurface`: Content on inverse surface
- `inversePrimary`: Primary color on inverse surface
- `surfaceTint`: Tint for elevated surfaces

**Deprecated (Material 2):**
- `background` → Use `surface`
- `onBackground` → Use `onSurface`
- `surfaceVariant` → Use surface container variants

### Creating ColorScheme from Seed

The recommended approach is generating a ColorScheme from a seed color:

```dart
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.blue,
    brightness: Brightness.light,
  ),
)
```

This automatically generates a harmonious color palette including:
- Primary, secondary, tertiary colors
- All container variants
- Surface colors
- Proper contrast ratios for accessibility

**Custom Seed Colors:**

```dart
// Using Material color
ColorScheme.fromSeed(seedColor: Colors.deepPurple)

// Using custom color
ColorScheme.fromSeed(seedColor: Color(0xFF6750A4))

// Overriding specific colors
ColorScheme.fromSeed(
  seedColor: Colors.blue,
  error: Colors.red, // Custom error color
  secondary: Colors.teal, // Custom secondary
)
```

### Manual ColorScheme Definition

For complete control, define all colors manually:

```dart
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme(
    brightness: Brightness.light,

    // Primary
    primary: Color(0xFF6200EE),
    onPrimary: Colors.white,
    primaryContainer: Color(0xFFBB86FC),
    onPrimaryContainer: Color(0xFF3700B3),

    // Secondary
    secondary: Color(0xFF03DAC6),
    onSecondary: Colors.black,
    secondaryContainer: Color(0xFF018786),
    onSecondaryContainer: Colors.white,

    // Tertiary
    tertiary: Color(0xFF03A9F4),
    onTertiary: Colors.white,
    tertiaryContainer: Color(0xFF81D4FA),
    onTertiaryContainer: Color(0xFF01579B),

    // Error
    error: Color(0xFFB00020),
    onError: Colors.white,
    errorContainer: Color(0xFFF9DEDC),
    onErrorContainer: Color(0xFF8C0009),

    // Surface
    surface: Color(0xFFFFFFFF),
    onSurface: Color(0xFF000000),
    surfaceContainerLowest: Color(0xFFFFFFFF),
    surfaceContainerLow: Color(0xFFF5F5F5),
    surfaceContainer: Color(0xFFEEEEEE),
    surfaceContainerHigh: Color(0xFFE0E0E0),
    surfaceContainerHighest: Color(0xFFBDBDBD),

    // Other
    outline: Color(0xFF79747E),
    outlineVariant: Color(0xFFCAC4D0),
    shadow: Colors.black,
    scrim: Colors.black,
    inverseSurface: Color(0xFF313033),
    onInverseSurface: Color(0xFFF4EFF4),
    inversePrimary: Color(0xFFD0BCFF),
    surfaceTint: Color(0xFF6200EE),
  ),
)
```

### Dark Theme

Create a dark theme using the same approaches:

```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.light,
    ),
  ),
  darkTheme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.dark,
    ),
  ),
  themeMode: ThemeMode.system, // system, light, or dark
)
```

**ThemeMode Options:**
- `ThemeMode.system`: Follow system theme (default)
- `ThemeMode.light`: Always use light theme
- `ThemeMode.dark`: Always use dark theme

### Runtime Theme Switching

```dart
class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  ThemeMode _themeMode = ThemeMode.system;

  void _toggleTheme() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.light
          ? ThemeMode.dark
          : ThemeMode.light;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      themeMode: _themeMode,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
      ),
      home: HomePage(onToggleTheme: _toggleTheme),
    );
  }
}
```

## Dynamic Color (Android 12+)

Dynamic color allows your app to match the user's wallpaper color scheme on Android 12+.

### Setup

Add the `dynamic_color` package:

```yaml
dependencies:
  dynamic_color: ^1.7.0
```

### Implementation

```dart
import 'package:dynamic_color/dynamic_color.dart';

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DynamicColorBuilder(
      builder: (ColorScheme? lightDynamic, ColorScheme? darkDynamic) {
        // lightDynamic: System light color scheme (Android 12+)
        // darkDynamic: System dark color scheme (Android 12+)
        // Both null on older Android or non-Android platforms

        ColorScheme lightColorScheme;
        ColorScheme darkColorScheme;

        if (lightDynamic != null && darkDynamic != null) {
          // Use dynamic colors
          lightColorScheme = lightDynamic.harmonized();
          darkColorScheme = darkDynamic.harmonized();
        } else {
          // Fallback to default colors
          lightColorScheme = ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.light,
          );
          darkColorScheme = ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.dark,
          );
        }

        return MaterialApp(
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: lightColorScheme,
          ),
          darkTheme: ThemeData(
            useMaterial3: true,
            colorScheme: darkColorScheme,
          ),
          themeMode: ThemeMode.system,
          home: HomePage(),
        );
      },
    );
  }
}
```

### Dynamic Color with Custom Overrides

```dart
DynamicColorBuilder(
  builder: (ColorScheme? lightDynamic, ColorScheme? darkDynamic) {
    ColorScheme lightColorScheme;
    ColorScheme darkColorScheme;

    if (lightDynamic != null && darkDynamic != null) {
      // Use dynamic colors with custom overrides
      lightColorScheme = lightDynamic.copyWith(
        error: const Color(0xFFBA1A1A), // Custom error color
      );
      darkColorScheme = darkDynamic.copyWith(
        error: const Color(0xFFFFB4AB),
      );
    } else {
      lightColorScheme = ColorScheme.fromSeed(
        seedColor: Colors.blue,
      );
      darkColorScheme = ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.dark,
      );
    }

    return MaterialApp(
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: lightColorScheme,
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: darkColorScheme,
      ),
    );
  },
)
```

## Component Theming

### ThemeData Component Themes

Customize individual component styles through ThemeData:

```dart
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),

  // AppBar
  appBarTheme: AppBarTheme(
    centerTitle: true,
    elevation: 0,
    backgroundColor: Colors.transparent,
    foregroundColor: Colors.black,
    titleTextStyle: TextStyle(
      fontSize: 20,
      fontWeight: FontWeight.bold,
      color: Colors.black,
    ),
  ),

  // Buttons
  filledButtonTheme: FilledButtonThemeData(
    style: FilledButton.styleFrom(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      textStyle: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
    ),
  ),

  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    ),
  ),

  outlinedButtonTheme: OutlinedButtonThemeData(
    style: OutlinedButton.styleFrom(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      side: BorderSide(color: Colors.blue, width: 1.5),
    ),
  ),

  textButtonTheme: TextButtonThemeData(
    style: TextButton.styleFrom(
      foregroundColor: Colors.blue,
    ),
  ),

  // Card
  cardTheme: CardTheme(
    elevation: 2,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
    margin: EdgeInsets.all(8),
  ),

  // Chip
  chipTheme: ChipThemeData(
    backgroundColor: Colors.grey.shade200,
    selectedColor: Colors.blue.shade100,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
  ),

  // Dialog
  dialogTheme: DialogTheme(
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
    titleTextStyle: TextStyle(
      fontSize: 20,
      fontWeight: FontWeight.bold,
    ),
  ),

  // ListTile
  listTileTheme: ListTileThemeData(
    contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
  ),

  // NavigationBar
  navigationBarTheme: NavigationBarThemeData(
    height: 80,
    elevation: 3,
    indicatorColor: Colors.blue.shade100,
    labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
  ),

  // NavigationRail
  navigationRailTheme: NavigationRailThemeData(
    backgroundColor: Colors.grey.shade50,
    selectedIconTheme: IconThemeData(color: Colors.blue),
    unselectedIconTheme: IconThemeData(color: Colors.grey),
    selectedLabelTextStyle: TextStyle(color: Colors.blue),
    unselectedLabelTextStyle: TextStyle(color: Colors.grey),
  ),

  // TextField
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: Colors.grey.shade100,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide(color: Colors.grey.shade300),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide(color: Colors.blue, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide(color: Colors.red),
    ),
    contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
  ),

  // FloatingActionButton
  floatingActionButtonTheme: FloatingActionButtonThemeData(
    backgroundColor: Colors.blue,
    foregroundColor: Colors.white,
    elevation: 4,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
  ),

  // SnackBar
  snackBarTheme: SnackBarThemeData(
    backgroundColor: Colors.grey.shade800,
    contentTextStyle: TextStyle(color: Colors.white),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
    behavior: SnackBarBehavior.floating,
  ),

  // Checkbox
  checkboxTheme: CheckboxThemeData(
    fillColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return Colors.blue;
      }
      return null;
    }),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(4),
    ),
  ),

  // Radio
  radioTheme: RadioThemeData(
    fillColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return Colors.blue;
      }
      return null;
    }),
  ),

  // Switch
  switchTheme: SwitchThemeData(
    thumbColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return Colors.blue;
      }
      return Colors.grey;
    }),
    trackColor: MaterialStateProperty.resolveWith((states) {
      if (states.contains(MaterialState.selected)) {
        return Colors.blue.shade200;
      }
      return Colors.grey.shade300;
    }),
  ),

  // Slider
  sliderTheme: SliderThemeData(
    activeTrackColor: Colors.blue,
    inactiveTrackColor: Colors.grey.shade300,
    thumbColor: Colors.blue,
    overlayColor: Colors.blue.withOpacity(0.2),
  ),

  // Progress Indicators
  progressIndicatorTheme: ProgressIndicatorThemeData(
    color: Colors.blue,
    linearTrackColor: Colors.grey.shade300,
    circularTrackColor: Colors.grey.shade300,
  ),

  // Divider
  dividerTheme: DividerThemeData(
    color: Colors.grey.shade300,
    thickness: 1,
    space: 1,
  ),
)
```

## Typography

### TextTheme

Material 3 defines a comprehensive text hierarchy:

```dart
ThemeData(
  useMaterial3: true,
  textTheme: TextTheme(
    // Display styles (largest)
    displayLarge: TextStyle(fontSize: 57, fontWeight: FontWeight.w400),
    displayMedium: TextStyle(fontSize: 45, fontWeight: FontWeight.w400),
    displaySmall: TextStyle(fontSize: 36, fontWeight: FontWeight.w400),

    // Headline styles
    headlineLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.w400),
    headlineMedium: TextStyle(fontSize: 28, fontWeight: FontWeight.w400),
    headlineSmall: TextStyle(fontSize: 24, fontWeight: FontWeight.w400),

    // Title styles
    titleLarge: TextStyle(fontSize: 22, fontWeight: FontWeight.w400),
    titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
    titleSmall: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),

    // Body styles
    bodyLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.w400),
    bodyMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w400),
    bodySmall: TextStyle(fontSize: 12, fontWeight: FontWeight.w400),

    // Label styles (smallest)
    labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
    labelMedium: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
    labelSmall: TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
  ),
)
```

### Using Text Styles

```dart
Text(
  'Display Large',
  style: Theme.of(context).textTheme.displayLarge,
)

Text(
  'Headline Medium',
  style: Theme.of(context).textTheme.headlineMedium,
)

Text(
  'Body Large',
  style: Theme.of(context).textTheme.bodyLarge,
)

// Custom modifications
Text(
  'Custom Text',
  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
    color: Colors.blue,
    fontWeight: FontWeight.bold,
  ),
)
```

### Custom Fonts

```dart
ThemeData(
  useMaterial3: true,
  fontFamily: 'Roboto',
  textTheme: TextTheme(
    bodyLarge: TextStyle(fontFamily: 'OpenSans'),
    headlineMedium: TextStyle(fontFamily: 'Montserrat'),
  ),
)
```

## Accessing Theme Values

### Using Theme.of()

```dart
// Access ColorScheme
final colorScheme = Theme.of(context).colorScheme;
Container(
  color: colorScheme.primary,
  child: Text(
    'Text',
    style: TextStyle(color: colorScheme.onPrimary),
  ),
)

// Access TextTheme
final textTheme = Theme.of(context).textTheme;
Text('Text', style: textTheme.bodyLarge)

// Access specific theme properties
final cardTheme = Theme.of(context).cardTheme;
final buttonStyle = Theme.of(context).filledButtonTheme.style;
```

## Custom Theme Extensions

Create custom theme properties using ThemeExtension:

```dart
@immutable
class CustomColors extends ThemeExtension<CustomColors> {
  final Color? success;
  final Color? warning;
  final Color? info;

  const CustomColors({
    this.success,
    this.warning,
    this.info,
  });

  @override
  CustomColors copyWith({
    Color? success,
    Color? warning,
    Color? info,
  }) {
    return CustomColors(
      success: success ?? this.success,
      warning: warning ?? this.warning,
      info: info ?? this.info,
    );
  }

  @override
  CustomColors lerp(ThemeExtension<CustomColors>? other, double t) {
    if (other is! CustomColors) {
      return this;
    }
    return CustomColors(
      success: Color.lerp(success, other.success, t),
      warning: Color.lerp(warning, other.warning, t),
      info: Color.lerp(info, other.info, t),
    );
  }
}

// Add to ThemeData
ThemeData(
  useMaterial3: true,
  extensions: [
    CustomColors(
      success: Colors.green,
      warning: Colors.orange,
      info: Colors.lightBlue,
    ),
  ],
)

// Access custom theme
final customColors = Theme.of(context).extension<CustomColors>();
Container(
  color: customColors?.success,
  child: Text('Success!'),
)
```

## Material Color Utilities

Material 3 uses the Material Color Utilities for generating color schemes:

```yaml
dependencies:
  material_color_utilities: ^0.11.1
```

```dart
import 'package:material_color_utilities/material_color_utilities.dart';

// Generate scheme from image
Future<ColorScheme> colorSchemeFromImage(ImageProvider image) async {
  final ByteData data = await image.getBytes();
  final bytes = data.buffer.asUint8List();

  // Extract prominent color
  final argb = await ColorScheme.fromImageProvider(
    provider: image,
  );

  return argb;
}
```

## Best Practices

1. **Use ColorScheme.fromSeed()** for automatic harmonic color generation
2. **Enable Material 3** with `useMaterial3: true`
3. **Provide both light and dark themes** for best user experience
4. **Use theme colors** instead of hardcoded colors
5. **Test color contrast** for accessibility (WCAG AA minimum)
6. **Implement dynamic color** on Android 12+ for personalization
7. **Use TextTheme styles** for consistent typography
8. **Override only necessary** component themes, rely on defaults
9. **Test themes** in both light and dark modes
10. **Use ColorScheme container colors** for elevated surfaces

## Accessibility Considerations

Material 3 ColorScheme ensures proper contrast ratios:
- **Primary/onPrimary**: Minimum 4.5:1 contrast
- **Surface/onSurface**: Minimum 4.5:1 contrast
- **Error colors**: High contrast for visibility

Always test with:
- Screen readers
- Large text sizes
- High contrast mode
- Color blindness simulators

## Additional Resources

- Material Color System: https://m3.material.io/styles/color/system
- Flutter Theming Guide: https://docs.flutter.dev/cookbook/design/themes
- Dynamic Color Package: https://pub.dev/packages/dynamic_color
- Material Color Utilities: https://pub.dev/packages/material_color_utilities
