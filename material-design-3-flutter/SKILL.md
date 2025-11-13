---
name: material-design-3-flutter
description: Comprehensive guide for building Flutter applications with Material Design 3 (Material You). This skill should be used when developing Flutter apps with Material 3 components, implementing adaptive and responsive layouts, applying Material Design theming and color schemes, or building Android applications using the complete Material widget catalog. Covers layout patterns, interactive widgets, forms, navigation, and best practices for Material 3 implementation.
---

# Material Design 3 Flutter

## Overview

Material Design 3 (also known as Material You) is Flutter's default design system, providing a comprehensive widget catalog for building beautiful, adaptive, and expressive applications. This skill provides guidance for implementing Material 3 components, creating responsive layouts, applying dynamic theming, and following best practices for Android platform development.

**Flutter Version:** Material 3 is stable and default in Flutter 3.16+. Latest stable versions include Flutter 3.32 and 3.35.5 (as of 2025).

**Key Resources:**
- Official Material 3 docs: https://m3.material.io/develop/flutter
- Flutter Material widgets: https://docs.flutter.dev/ui/widgets/material
- Flutter API reference: https://api.flutter.dev/flutter/material/

## Core Capabilities

### 1. Material Design 3 Setup

#### Enable Material 3

Material 3 is enabled by default in Flutter 3.16+, but can be explicitly configured:

```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
  ),
  darkTheme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.dark,
    ),
  ),
  themeMode: ThemeMode.system,
  home: MyHomePage(),
)
```

### 2. Layout Structure with Scaffold

Scaffold provides the basic Material Design visual layout structure:

```dart
Scaffold(
  appBar: AppBar(
    title: Text('Material 3 App'),
  ),
  body: // Main content,
  floatingActionButton: FloatingActionButton(
    onPressed: () {},
    child: Icon(Icons.add),
  ),
  bottomNavigationBar: NavigationBar(
    destinations: [
      NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
      NavigationDestination(icon: Icon(Icons.search), label: 'Search'),
    ],
    selectedIndex: 0,
    onDestinationSelected: (index) {},
  ),
  drawer: NavigationDrawer(
    children: [
      NavigationDrawerDestination(
        icon: Icon(Icons.inbox),
        label: Text('Inbox'),
      ),
    ],
  ),
)
```

**Key Points:**
- AppBar has no elevation or background color by default in Material 3
- Use NavigationBar (not BottomNavigationBar) for Material 3 apps
- NavigationBar uses NavigationDestination (not BottomNavigationBarItem)
- Use onDestinationSelected instead of onTap
- Use selectedIndex instead of currentIndex

### 3. Interactive Widgets

#### Buttons

Material 3 provides five button types with distinct visual hierarchies:

```dart
// Primary action - filled button
FilledButton(
  onPressed: () {},
  child: Text('Filled Button'),
)

// Secondary action - elevated button
ElevatedButton(
  onPressed: () {},
  child: Text('Elevated Button'),
)

// Tertiary action - outlined button
OutlinedButton(
  onPressed: () {},
  child: Text('Outlined Button'),
)

// Low emphasis - text button
TextButton(
  onPressed: () {},
  child: Text('Text Button'),
)

// Icon button variants
IconButton(
  onPressed: () {},
  icon: Icon(Icons.favorite),
)

// Segmented button (new in M3)
SegmentedButton<String>(
  segments: [
    ButtonSegment(value: 'day', label: Text('Day')),
    ButtonSegment(value: 'week', label: Text('Week')),
    ButtonSegment(value: 'month', label: Text('Month')),
  ],
  selected: {'day'},
  onSelectionChanged: (Set<String> newSelection) {},
)
```

#### Dialogs and Snackbars

```dart
// Alert Dialog
showDialog(
  context: context,
  builder: (context) => AlertDialog(
    title: Text('Dialog Title'),
    content: Text('Dialog content goes here'),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: Text('Cancel'),
      ),
      FilledButton(
        onPressed: () => Navigator.pop(context),
        child: Text('OK'),
      ),
    ],
  ),
)

// Snackbar
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text('Action completed'),
    action: SnackBarAction(
      label: 'Undo',
      onPressed: () {},
    ),
  ),
)

// Bottom Sheet
showModalBottomSheet(
  context: context,
  builder: (context) => Container(
    padding: EdgeInsets.all(16),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        ListTile(
          leading: Icon(Icons.share),
          title: Text('Share'),
          onTap: () {},
        ),
      ],
    ),
  ),
)
```

### 4. Form Input Widgets

#### TextField and TextFormField

```dart
// Basic TextField
TextField(
  decoration: InputDecoration(
    labelText: 'Email',
    hintText: 'Enter your email',
    prefixIcon: Icon(Icons.email),
    border: OutlineInputBorder(),
  ),
  keyboardType: TextInputType.emailAddress,
)

// Form with validation
Form(
  key: _formKey,
  child: Column(
    children: [
      TextFormField(
        decoration: InputDecoration(
          labelText: 'Username',
          border: OutlineInputBorder(),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please enter username';
          }
          return null;
        },
      ),
      ElevatedButton(
        onPressed: () {
          if (_formKey.currentState!.validate()) {
            // Process data
          }
        },
        child: Text('Submit'),
      ),
    ],
  ),
)
```

#### Selection Controls

```dart
// Checkbox
Checkbox(
  value: _isChecked,
  onChanged: (bool? value) {
    setState(() {
      _isChecked = value ?? false;
    });
  },
)

// Radio buttons
Radio<String>(
  value: 'option1',
  groupValue: _selectedOption,
  onChanged: (String? value) {
    setState(() {
      _selectedOption = value;
    });
  },
)

// Switch
Switch(
  value: _isSwitched,
  onChanged: (bool value) {
    setState(() {
      _isSwitched = value;
    });
  },
)

// Slider (Material 3 updated design)
Slider(
  value: _sliderValue,
  min: 0,
  max: 100,
  divisions: 10,
  label: _sliderValue.round().toString(),
  onChanged: (double value) {
    setState(() {
      _sliderValue = value;
    });
  },
)

// DropdownMenu (new in Material 3)
DropdownMenu<String>(
  label: Text('Select option'),
  dropdownMenuEntries: [
    DropdownMenuEntry(value: '1', label: 'Option 1'),
    DropdownMenuEntry(value: '2', label: 'Option 2'),
  ],
  onSelected: (String? value) {},
)
```

**Form Best Practices:**
- Wrap form fields in a Form widget with FormField for validation
- Use TextFormField (not TextField) for automatic FormField integration
- FormState provides save(), reset(), and validate() methods
- Checkbox, Radio, and Switch do not maintain state—handle via onChanged callback

### 5. Layout Widgets

#### Card and ListTile

```dart
// Card with ListTile (recommended pattern)
Card(
  child: ListTile(
    leading: Icon(Icons.person),
    title: Text('John Doe'),
    subtitle: Text('Software Engineer'),
    trailing: Icon(Icons.more_vert),
    onTap: () {},
  ),
)

// Card types in Material 3
Card.elevated(
  elevation: 2,
  child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Elevated Card'),
  ),
)

Card.filled(
  child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Filled Card'),
  ),
)

Card.outlined(
  child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Outlined Card'),
  ),
)
```

**Card Best Practices:**
- Card provides built-in elevation and rounded corners (following Material Design)
- Card is more efficient than Container with manual BoxDecoration for Material styling
- ListTile requires a Material widget ancestor to paint properly
- Avoid wrapping individual ListTiles with Material—use common ancestor instead
- Combine Card + ListTile for lists, or use in DrawerHeader and ExpansionTile

**ListTile Benefits:**
- Predefined sections (leading, title, subtitle, trailing) with automatic spacing
- Easier to read and maintain than Row with manual layout
- Up to 3 lines of text with proper typography

#### Lists and Grids

```dart
// ListView with separated items
ListView.separated(
  itemCount: items.length,
  separatorBuilder: (context, index) => Divider(),
  itemBuilder: (context, index) {
    return ListTile(
      title: Text(items[index]),
    );
  },
)

// GridView
GridView.builder(
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 2,
    crossAxisSpacing: 8,
    mainAxisSpacing: 8,
  ),
  itemCount: items.length,
  itemBuilder: (context, index) {
    return Card(
      child: Center(child: Text(items[index])),
    );
  },
)
```

### 6. Navigation Patterns

#### NavigationBar (Bottom Navigation)

```dart
NavigationBar(
  selectedIndex: _currentIndex,
  onDestinationSelected: (int index) {
    setState(() {
      _currentIndex = index;
    });
  },
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
)
```

#### NavigationRail (Side Navigation)

```dart
NavigationRail(
  selectedIndex: _selectedIndex,
  onDestinationSelected: (int index) {
    setState(() {
      _selectedIndex = index;
    });
  },
  labelType: NavigationRailLabelType.all,
  destinations: [
    NavigationRailDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: Text('Home'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.search_outlined),
      selectedIcon: Icon(Icons.search),
      label: Text('Search'),
    ),
  ],
)
```

#### NavigationDrawer

```dart
NavigationDrawer(
  selectedIndex: _selectedIndex,
  onDestinationSelected: (int index) {
    setState(() {
      _selectedIndex = index;
    });
    Navigator.pop(context); // Close drawer
  },
  children: [
    Padding(
      padding: EdgeInsets.fromLTRB(28, 16, 16, 10),
      child: Text('Header', style: Theme.of(context).textTheme.titleSmall),
    ),
    NavigationDrawerDestination(
      icon: Icon(Icons.inbox_outlined),
      selectedIcon: Icon(Icons.inbox),
      label: Text('Inbox'),
    ),
    NavigationDrawerDestination(
      icon: Icon(Icons.send_outlined),
      selectedIcon: Icon(Icons.send),
      label: Text('Outbox'),
    ),
    Divider(indent: 28, endIndent: 28),
    NavigationDrawerDestination(
      icon: Icon(Icons.settings_outlined),
      selectedIcon: Icon(Icons.settings),
      label: Text('Settings'),
    ),
  ],
)
```

### 7. Theming and Color Schemes

#### Creating Theme with ColorScheme

```dart
// From seed color (recommended)
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.blue,
    brightness: Brightness.light,
  ),
)

// Custom ColorScheme
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme(
    brightness: Brightness.light,
    primary: Color(0xFF6200EE),
    onPrimary: Colors.white,
    secondary: Color(0xFF03DAC6),
    onSecondary: Colors.black,
    error: Color(0xFFB00020),
    onError: Colors.white,
    surface: Color(0xFFFFFFFF),
    onSurface: Color(0xFF000000),
  ),
)
```

#### Dynamic Color (Android 12+)

Install the `dynamic_color` package and implement:

```dart
import 'package:dynamic_color/dynamic_color.dart';

DynamicColorBuilder(
  builder: (ColorScheme? lightDynamic, ColorScheme? darkDynamic) {
    return MaterialApp(
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: lightDynamic ?? ColorScheme.fromSeed(
          seedColor: Colors.blue,
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: darkDynamic ?? ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
      ),
      themeMode: ThemeMode.system,
    );
  },
)
```

#### Updated ColorScheme Roles

Material 3 introduces new color roles:
- **Surface colors:** surface, surfaceDim, surfaceBright, surfaceContainerLowest, surfaceContainerLow, surfaceContainer, surfaceContainerHigh, surfaceContainerHighest
- **Accent colors:** primary, onPrimary, primaryContainer, onPrimaryContainer (same pattern for secondary and tertiary)
- **Deprecated:** background, onBackground, surfaceVariant (use surface variants instead)

#### Custom Component Themes

```dart
ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
  appBarTheme: AppBarTheme(
    centerTitle: true,
    backgroundColor: Colors.transparent,
    elevation: 0,
  ),
  cardTheme: CardTheme(
    elevation: 2,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
  filledButtonTheme: FilledButtonThemeData(
    style: FilledButton.styleFrom(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    ),
  ),
)
```

### 8. Adaptive and Responsive Design

#### Using MediaQuery and LayoutBuilder

```dart
// MediaQuery for screen-wide properties
Widget build(BuildContext context) {
  final screenSize = MediaQuery.sizeOf(context);
  final orientation = MediaQuery.orientationOf(context);

  return Container(
    width: screenSize.width * 0.8,
    child: Text('Responsive content'),
  );
}

// LayoutBuilder for parent-constrained sizing
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth > 600) {
      return TabletLayout();
    } else {
      return MobileLayout();
    }
  },
)
```

#### Breakpoint-Based Layout

```dart
class ResponsiveLayout extends StatelessWidget {
  static const mobileBreakpoint = 600.0;
  static const tabletBreakpoint = 1024.0;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < mobileBreakpoint) {
          return _buildMobileLayout();
        } else if (constraints.maxWidth < tabletBreakpoint) {
          return _buildTabletLayout();
        } else {
          return _buildDesktopLayout();
        }
      },
    );
  }

  Widget _buildMobileLayout() {
    return Scaffold(
      appBar: AppBar(title: Text('Mobile')),
      body: ListView(children: _items),
      drawer: Drawer(child: _navigationItems),
    );
  }

  Widget _buildTabletLayout() {
    return Scaffold(
      appBar: AppBar(title: Text('Tablet')),
      body: Row(
        children: [
          NavigationRail(
            destinations: _railDestinations,
            selectedIndex: 0,
          ),
          Expanded(child: GridView(children: _items)),
        ],
      ),
    );
  }

  Widget _buildDesktopLayout() {
    return Scaffold(
      appBar: AppBar(title: Text('Desktop')),
      body: Row(
        children: [
          NavigationRail(
            extended: true,
            destinations: _railDestinations,
            selectedIndex: 0,
          ),
          VerticalDivider(width: 1),
          Expanded(
            child: GridView(
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
              ),
              children: _items,
            ),
          ),
        ],
      ),
    );
  }
}
```

**Best Practices:**
- Use MediaQuery.sizeOf() for screen-wide measurements
- Use LayoutBuilder for parent-constrained responsive behavior
- Common breakpoints: mobile (<600px), tablet (600-1024px), desktop (>1024px)
- Combine with Flexible, Expanded, and FittedBox for fine control
- Prefer NavigationBar for mobile, NavigationRail for tablet/desktop
- Use GridView with adaptive crossAxisCount for different screen sizes

#### Adaptive Navigation Example

```dart
class AdaptiveScaffold extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.sizeOf(context).width >= 1024;
    final isTablet = MediaQuery.sizeOf(context).width >= 600 && !isDesktop;

    return Scaffold(
      appBar: isDesktop ? null : AppBar(title: Text('App Title')),
      body: Row(
        children: [
          if (isDesktop || isTablet)
            NavigationRail(
              extended: isDesktop,
              destinations: _destinations,
              selectedIndex: _selectedIndex,
              onDestinationSelected: _onNavigate,
            ),
          Expanded(child: _buildContent()),
        ],
      ),
      bottomNavigationBar: (!isDesktop && !isTablet)
          ? NavigationBar(
              destinations: _navBarDestinations,
              selectedIndex: _selectedIndex,
              onDestinationSelected: _onNavigate,
            )
          : null,
      drawer: (!isDesktop && !isTablet) ? Drawer(child: _menu) : null,
    );
  }
}
```

### 9. Progress Indicators

Material 3 updated CircularProgressIndicator and LinearProgressIndicator in Flutter 3.29:

```dart
// Circular progress
CircularProgressIndicator(
  value: 0.7, // 0.0 to 1.0, or null for indeterminate
)

// Linear progress
LinearProgressIndicator(
  value: 0.5, // 0.0 to 1.0, or null for indeterminate
)
```

### 10. Common Patterns and Best Practices

#### Material Ancestor Requirement

Many Material widgets require a Material ancestor:
- Wrap root with MaterialApp (provides Material ancestor and theme)
- ListTile requires Material ancestor for painting
- Use Scaffold which provides Material surface
- Avoid excessive Material wrapping for performance

#### State Management with Forms

```dart
class MyForm extends StatefulWidget {
  @override
  _MyFormState createState() => _MyFormState();
}

class _MyFormState extends State<MyForm> {
  final _formKey = GlobalKey<FormState>();
  String _email = '';
  bool _acceptTerms = false;

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            decoration: InputDecoration(labelText: 'Email'),
            validator: (value) => value?.contains('@') == true
                ? null
                : 'Invalid email',
            onSaved: (value) => _email = value ?? '',
          ),
          CheckboxListTile(
            title: Text('Accept terms'),
            value: _acceptTerms,
            onChanged: (value) => setState(() => _acceptTerms = value ?? false),
          ),
          FilledButton(
            onPressed: _submit,
            child: Text('Submit'),
          ),
        ],
      ),
    );
  }

  void _submit() {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      // Process form data
    }
  }
}
```

#### Efficient List Rendering

```dart
// Use builder constructors for large lists
ListView.builder(
  itemCount: largeList.length,
  itemBuilder: (context, index) {
    return ListTile(title: Text(largeList[index]));
  },
)

// Separate items with Divider
ListView.separated(
  itemCount: items.length,
  separatorBuilder: (context, index) => Divider(),
  itemBuilder: (context, index) => ListTile(title: Text(items[index])),
)
```

#### Async Operations with Dialogs

```dart
Future<void> _showLoadingAndProcess() async {
  // Show loading dialog
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => Center(
      child: CircularProgressIndicator(),
    ),
  );

  try {
    await _processData();
    Navigator.pop(context); // Close loading dialog

    // Show success snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Success!')),
    );
  } catch (e) {
    Navigator.pop(context); // Close loading dialog

    // Show error dialog
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Error'),
        content: Text(e.toString()),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }
}
```

## Resources

This skill includes reference documentation for detailed Material 3 implementation:

### references/

- **widget_catalog.md** - Comprehensive list of all Material 3 widgets organized by category
- **theming_guide.md** - Detailed theming, ColorScheme, and dynamic color implementation
- **responsive_patterns.md** - Adaptive layout patterns, breakpoints, and responsive design techniques
- **best_practices.md** - Material 3 best practices, performance tips, and common patterns

These reference files contain detailed information to supplement the core guidance above. Load them when deeper knowledge is needed for specific implementations.

## Migration from Material 2

For existing apps, Material 3 is enabled by default in Flutter 3.16+. Key differences:
- NavigationBar replaces BottomNavigationBar
- New color roles (surface variants, accent colors)
- Updated component designs (buttons, AppBar, progress indicators)
- No elevation on AppBar by default
- FilledButton for primary actions (instead of ElevatedButton)

Refer to official migration guides at https://docs.flutter.dev/release/breaking-changes/material-3-default

## Additional Resources

- **Official Documentation:** https://docs.flutter.dev/ui/design/material
- **Material 3 Guidelines:** https://m3.material.io/develop/flutter
- **Flutter API Reference:** https://api.flutter.dev/flutter/material/
- **Adaptive Design Guide:** https://docs.flutter.dev/ui/adaptive-responsive
- **Material 3 Codelabs:** https://codelabs.developers.google.com/codelabs/flutter-animated-responsive-layout
