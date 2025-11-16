---
name: flutter-widget-previewer
description: Comprehensive guide for using the Flutter Widget Previewer tool (Flutter 3.35+). This skill should be used when visualizing Flutter widgets in isolation, creating widget galleries, testing components across different themes and locales, or working with the @Preview annotation API. Covers setup, annotation usage, theme variants, localization testing, context injection, and IDE integration for real-time widget rendering.
---

# Flutter Widget Previewer

## Overview

The Flutter Widget Previewer is an experimental tool introduced in Flutter 3.35 that enables real-time visualization of Flutter widgets in isolation within a Chrome browser environment. This tool is essential for developing component galleries, testing widgets across multiple themes and locales, and ensuring components don't rely on implicit global state.

**Version Requirements:**
- Minimum Flutter version: 3.35
- Full IDE support: Flutter 3.38+
- Status: Experimental feature (stable channel)
- API: package:flutter/widget_previews.dart

**Key Resources:**
- Official documentation: https://docs.flutter.dev/tools/widget-previewer
- API reference: https://api.flutter.dev/flutter/widget_previews/
- Widget previews library: package:flutter/widget_previews.dart

**Important**: The Widget Previewer APIs are explicitly marked as unstable and subject to breaking changes in future releases. Design architecture to isolate preview configurations from core component implementations.

## Core Capabilities

### 1. Setup and Initialization

#### IDE Integration (Flutter 3.38+)

**Supported IDEs:**
- Android Studio
- IntelliJ IDEA
- Visual Studio Code

Starting with Flutter 3.38, the Widget Previewer automatically launches on IDE startup and appears in a dedicated sidebar tab. The IDE manages the previewer lifecycle automatically.

#### Command-Line Usage

For headless environments or manual control:

```bash
# Start the widget previewer from project root
flutter widget-preview start

# The previewer will:
# 1. Start a local server
# 2. Open Chrome browser
# 3. Watch for @Preview annotations
# 4. Hot reload on file changes
```

**Browser Requirements:**
- Chrome browser (required)
- Built with Flutter Web
- No support for dart:io or dart:ffi libraries
- No support for native plugins

### 2. The @Preview Annotation API

#### Basic Usage

Import the widget previews library and annotate target code:

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';

// Preview a top-level function
@Preview(name: 'Primary Button')
Widget primaryButton() {
  return FilledButton(
    onPressed: () {},
    child: Text('Click Me'),
  );
}

// Preview a static method
class ButtonPreviews {
  @Preview(name: 'Elevated Button')
  static Widget elevatedButton() {
    return ElevatedButton(
      onPressed: () {},
      child: Text('Submit'),
    );
  }
}

// Preview a widget constructor
class CustomCard extends StatelessWidget {
  final String title;
  final String subtitle;

  // Constructor with no required parameters can be previewed
  @Preview(name: 'Default Card')
  const CustomCard({
    this.title = 'Sample Title',
    this.subtitle = 'Sample Subtitle',
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }
}
```

#### Annotation Targets

The @Preview annotation can be applied to:

1. **Top-level functions** returning Widget or WidgetBuilder
2. **Static methods** within a class returning Widget or WidgetBuilder
3. **Public widget constructors or factories** with no required arguments

#### Required Parameters

```dart
@Preview(
  name: 'Button Preview', // Required: Display label in preview gallery
)
```

The `name` parameter is mandatory and appears as the label in the generated preview gallery interface.

### 3. Theme Variants with PreviewThemeData

Test components across multiple Material or Cupertino themes simultaneously:

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';

@Preview(
  name: 'Button Theme Variants',
  themes: [
    PreviewThemeData(
      name: 'Light Mode',
      themeData: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
      ),
    ),
    PreviewThemeData(
      name: 'Dark Mode',
      themeData: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
      ),
    ),
    PreviewThemeData(
      name: 'Custom Purple',
      themeData: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.purple,
          brightness: Brightness.light,
        ),
      ),
    ),
  ],
)
Widget themedButton() {
  return FilledButton(
    onPressed: () {},
    child: Text('Themed Button'),
  );
}
```

**PreviewThemeData Functionality:**
- Automatically generates side-by-side previews for each theme
- Supports both Material (ThemeData) and Cupertino (CupertinoThemeData)
- Enables visual theme consistency verification
- Useful for testing light/dark mode, brand color variations, and accessibility themes

### 4. Localization Variants with PreviewLocalizationsData

Test internationalization and Right-to-Left (RTL) layouts:

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';

@Preview(
  name: 'Localized Card',
  localizations: [
    PreviewLocalizationsData(
      name: 'English (LTR)',
      locale: Locale('en', 'US'),
      textDirection: TextDirection.ltr,
    ),
    PreviewLocalizationsData(
      name: 'Arabic (RTL)',
      locale: Locale('ar', 'SA'),
      textDirection: TextDirection.rtl,
    ),
    PreviewLocalizationsData(
      name: 'German',
      locale: Locale('de', 'DE'),
      textDirection: TextDirection.ltr,
    ),
  ],
)
Widget localizedCard() {
  // IMPORTANT: Wrap localized text access with Builder
  // to ensure correct context inheritance
  return Builder(
    builder: (context) {
      return Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Access MaterialLocalizations through context
              Text(
                MaterialLocalizations.of(context).okButtonLabel,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 8),
              Text(
                'Content text that flows with text direction',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      );
    },
  );
}
```

**Localization Best Practices:**
- Always use `Builder` widget to access localization context
- The Builder ensures the widget inherits the correct locale from the Previewer
- Test critical layouts with RTL to verify proper text direction handling
- Verify layout doesn't break with longer text (German) or different scripts (Arabic)

### 5. Context Injection with WidgetWrapper

#### The Problem: Missing Dependencies

Isolated widgets often depend on InheritedWidgets or state management providers that aren't available in the isolated preview environment:

```dart
// This widget depends on Provider
class ProfileWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // This will FAIL in isolation - no Provider ancestor
    final user = Provider.of<User>(context);
    return Text('Hello, ${user.name}');
  }
}
```

#### The Solution: WidgetWrapper

The `wrappers` parameter accepts a `WidgetWrapper` function that wraps the target widget with necessary context providers:

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';
import 'package:provider/provider.dart';

// Mock data for preview
class User {
  final String name;
  final String email;
  User(this.name, this.email);
}

@Preview(
  name: 'Profile with Provider',
  wrappers: [_providerWrapper],
)
Widget profilePreview() {
  return ProfileWidget();
}

// WidgetWrapper function signature: Widget Function(Widget)
Widget _providerWrapper(Widget child) {
  return Provider<User>(
    create: (_) => User('John Doe', 'john@example.com'),
    child: child,
  );
}

// Multiple wrappers for complex dependency trees
@Preview(
  name: 'Complex Dependencies',
  wrappers: [_providerWrapper, _themeWrapper, _navigationWrapper],
)
Widget complexWidget() {
  return ComplexDependentWidget();
}

Widget _themeWrapper(Widget child) {
  return MaterialApp(
    theme: ThemeData.light(),
    home: Scaffold(body: child),
  );
}

Widget _navigationWrapper(Widget child) {
  return Navigator(
    onGenerateRoute: (settings) => MaterialPageRoute(
      builder: (_) => child,
    ),
  );
}
```

**WidgetWrapper Signature:**
```dart
typedef WidgetWrapper = Widget Function(Widget child);
```

**Common Use Cases:**
- Injecting Provider, Riverpod, or Bloc state management
- Adding MaterialApp or CupertinoApp for navigation context
- Providing MediaQuery for responsive widgets
- Mocking service dependencies (repositories, API clients)
- Adding Scaffold for SnackBar or Dialog dependencies

### 6. Complete Example: Material 3 Component Gallery

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';

// ============================================
// Theme Definitions
// ============================================

final lightTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.blue,
    brightness: Brightness.light,
  ),
);

final darkTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.blue,
    brightness: Brightness.dark,
  ),
);

final customTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.deepPurple,
    brightness: Brightness.light,
  ),
);

// ============================================
// Preview Configurations
// ============================================

const standardThemes = [
  PreviewThemeData(name: 'Light', themeData: lightTheme),
  PreviewThemeData(name: 'Dark', themeData: darkTheme),
  PreviewThemeData(name: 'Purple', themeData: customTheme),
];

const localeVariants = [
  PreviewLocalizationsData(
    name: 'English',
    locale: Locale('en', 'US'),
    textDirection: TextDirection.ltr,
  ),
  PreviewLocalizationsData(
    name: 'Arabic',
    locale: Locale('ar'),
    textDirection: TextDirection.rtl,
  ),
];

// ============================================
// Button Previews
// ============================================

@Preview(
  name: 'Filled Button States',
  themes: standardThemes,
)
Widget filledButtonStates() {
  return Wrap(
    spacing: 8,
    runSpacing: 8,
    children: [
      FilledButton(
        onPressed: () {},
        child: Text('Enabled'),
      ),
      FilledButton(
        onPressed: null, // Disabled state
        child: Text('Disabled'),
      ),
      FilledButton.icon(
        onPressed: () {},
        icon: Icon(Icons.send),
        label: Text('With Icon'),
      ),
    ],
  );
}

@Preview(
  name: 'All Button Types',
  themes: standardThemes,
)
Widget allButtonTypes() {
  return Padding(
    padding: EdgeInsets.all(16),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        FilledButton(onPressed: () {}, child: Text('Filled')),
        SizedBox(height: 8),
        FilledButton.tonal(onPressed: () {}, child: Text('Filled Tonal')),
        SizedBox(height: 8),
        ElevatedButton(onPressed: () {}, child: Text('Elevated')),
        SizedBox(height: 8),
        OutlinedButton(onPressed: () {}, child: Text('Outlined')),
        SizedBox(height: 8),
        TextButton(onPressed: () {}, child: Text('Text')),
      ],
    ),
  );
}

// ============================================
// Card Previews with Localization
// ============================================

@Preview(
  name: 'Card Variants with RTL',
  themes: standardThemes,
  localizations: localeVariants,
)
Widget cardVariantsRTL() {
  return Builder(
    builder: (context) {
      return Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Card.elevated(
              child: ListTile(
                leading: Icon(Icons.person),
                title: Text('Elevated Card'),
                subtitle: Text('With elevation shadow'),
                trailing: Icon(Icons.arrow_forward),
              ),
            ),
            SizedBox(height: 8),
            Card.filled(
              child: ListTile(
                leading: Icon(Icons.favorite),
                title: Text('Filled Card'),
                subtitle: Text('With background fill'),
                trailing: Icon(Icons.arrow_forward),
              ),
            ),
            SizedBox(height: 8),
            Card.outlined(
              child: ListTile(
                leading: Icon(Icons.star),
                title: Text('Outlined Card'),
                subtitle: Text('With border outline'),
                trailing: Icon(Icons.arrow_forward),
              ),
            ),
          ],
        ),
      );
    },
  );
}

// ============================================
// Form Input Previews
// ============================================

@Preview(
  name: 'Text Input States',
  themes: standardThemes,
)
Widget textInputStates() {
  return Padding(
    padding: EdgeInsets.all(16),
    child: Column(
      children: [
        TextField(
          decoration: InputDecoration(
            labelText: 'Email',
            hintText: 'Enter your email',
            prefixIcon: Icon(Icons.email),
            border: OutlineInputBorder(),
          ),
        ),
        SizedBox(height: 16),
        TextField(
          decoration: InputDecoration(
            labelText: 'Disabled',
            enabled: false,
            border: OutlineInputBorder(),
          ),
        ),
        SizedBox(height: 16),
        TextField(
          decoration: InputDecoration(
            labelText: 'Error State',
            errorText: 'This field is required',
            border: OutlineInputBorder(),
          ),
        ),
      ],
    ),
  );
}

// ============================================
// Navigation Previews with Wrapper
// ============================================

Widget _scaffoldWrapper(Widget child) {
  return MaterialApp(
    home: Scaffold(
      body: child,
    ),
  );
}

@Preview(
  name: 'Navigation Bar',
  themes: standardThemes,
  wrappers: [_scaffoldWrapper],
)
Widget navigationBarPreview() {
  return Column(
    mainAxisAlignment: MainAxisAlignment.end,
    children: [
      NavigationBar(
        selectedIndex: 0,
        destinations: [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.search_outlined),
            selectedIcon: Icon(Icons.search),
            label: 'Search',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outlined),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    ],
  );
}
```

## Best Practices and Guidelines

### Architecture: Separation of Concerns

**Principle:** Isolate preview configurations from component implementations to minimize breaking change impact.

```dart
// ❌ BAD: Tightly coupled to experimental API
class MyButton extends StatelessWidget {
  @Preview(name: 'My Button') // Don't mix preview with component
  const MyButton();

  @override
  Widget build(BuildContext context) => FilledButton(...);
}

// ✅ GOOD: Separated preview configuration
// my_button.dart
class MyButton extends StatelessWidget {
  const MyButton({required this.label, required this.onPressed});
  final String label;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return FilledButton(onPressed: onPressed, child: Text(label));
  }
}

// my_button_preview.dart
@Preview(name: 'Enabled Button')
Widget enabledButton() => MyButton(label: 'Click Me', onPressed: () {});

@Preview(name: 'Disabled Button')
Widget disabledButton() => MyButton(label: 'Disabled', onPressed: null);
```

### Organizing Preview Files

**Recommended Structure:**

```
lib/
├── components/
│   ├── buttons/
│   │   ├── custom_button.dart          # Component implementation
│   │   └── custom_button_preview.dart  # All button previews
│   ├── cards/
│   │   ├── custom_card.dart
│   │   └── custom_card_preview.dart
│   └── forms/
│       ├── custom_input.dart
│       └── custom_input_preview.dart
```

**Benefits:**
- Clear separation of production and preview code
- Easy to locate all variants of a component
- Minimizes impact when APIs change
- Keeps component files clean

### Testing State Variants

Create dedicated preview functions for each meaningful state:

```dart
// Document component states through previews
@Preview(name: 'Button - Enabled')
Widget buttonEnabled() => CustomButton(enabled: true);

@Preview(name: 'Button - Disabled')
Widget buttonDisabled() => CustomButton(enabled: false);

@Preview(name: 'Button - Loading')
Widget buttonLoading() => CustomButton(loading: true);

@Preview(name: 'Button - Error')
Widget buttonError() => CustomButton(hasError: true);

@Preview(name: 'Button - Success')
Widget buttonSuccess() => CustomButton(success: true);
```

### Performance Considerations

**Heavy Computations:** Avoid expensive operations in preview functions, as they execute on every hot reload:

```dart
// ❌ BAD: Expensive operation on every render
@Preview(name: 'Chart')
Widget chartPreview() {
  final data = computeExpensiveChartData(); // Runs on every reload
  return Chart(data: data);
}

// ✅ GOOD: Use static/const mock data
const _mockChartData = [1, 2, 3, 4, 5];

@Preview(name: 'Chart')
Widget chartPreview() => Chart(data: _mockChartData);
```

## Limitations and Constraints

### Browser-Based Rendering Constraints

The Widget Previewer runs on Flutter Web, which imposes several limitations:

**Not Supported:**
- Native plugins (camera, sensors, location)
- dart:io APIs (file system, processes)
- dart:ffi APIs (native code integration)
- Platform-specific code (Android/iOS only features)

**Workaround:** Use conditional imports or abstract interfaces with mock implementations for previews.

### API Stability Warning

```dart
// This is an experimental API
import 'package:flutter/widget_previews.dart';

// ⚠️ WARNING: Breaking changes expected
// - @Preview annotation signature may change
// - PreviewThemeData structure may evolve
// - New parameters may be added
// - Existing parameters may be removed
```

**Mitigation Strategy:** Keep preview configurations in separate files (see Architecture section) so updates require minimal refactoring.

## Troubleshooting

### Preview Not Appearing

**Check:**
1. Flutter version ≥ 3.35 (`flutter --version`)
2. IDE supports Widget Previewer (Flutter 3.38+ for automatic support)
3. @Preview annotation imported: `import 'package:flutter/widget_previews.dart';`
4. Annotated function/constructor has correct signature (Widget or WidgetBuilder return type)
5. Constructors have no required parameters

### Context-Dependent Widget Errors

**Symptom:** Widget throws error about missing InheritedWidget or context dependencies.

**Solution:** Use `wrappers` parameter to inject required context:

```dart
// Error: MediaQuery.of() called with a context that does not contain a MediaQuery
@Preview(name: 'Responsive Widget', wrappers: [_mediaQueryWrapper])
Widget responsivePreview() => ResponsiveWidget();

Widget _mediaQueryWrapper(Widget child) {
  return MediaQuery(
    data: MediaQueryData(size: Size(375, 667)), // iPhone SE size
    child: child,
  );
}
```

### Localization Context Issues

**Symptom:** MaterialLocalizations.of(context) throws error.

**Solution:** Wrap localized text access with Builder widget:

```dart
@Preview(name: 'Localized', localizations: [/*...*/])
Widget localizedPreview() {
  return Builder( // Essential for context inheritance
    builder: (context) {
      final localizations = MaterialLocalizations.of(context);
      return Text(localizations.okButtonLabel);
    },
  );
}
```

## Additional Resources

- **Official Flutter Documentation:** https://docs.flutter.dev/tools/widget-previewer
- **Widget Previews API Reference:** https://api.flutter.dev/flutter/widget_previews/
- **Material 3 Components:** Use with material-design-3-flutter skill for complete gallery implementation
- **Flutter Release Notes:** https://docs.flutter.dev/release/whats-new

## Integration with Other Skills

This skill works best when combined with:

- **material-design-3-flutter** - For Material 3 theming and component implementation
- **flutter-mvvm-architecture** - For testing view models and state management in isolation
- **flutter-performance-optimization** - For profiling preview rendering performance
- **flutter-custom-painter** - For previewing custom-painted components

The Widget Previewer is a powerful tool for developing high-quality, well-tested component libraries and design systems in Flutter.
