# Responsive and Adaptive Design Patterns

This reference provides comprehensive guidance on creating responsive and adaptive Flutter applications that work across mobile, tablet, and desktop screen sizes using Material Design 3 principles.

## Core Concepts

### Responsive vs Adaptive Design

- **Responsive Design:** UI automatically adjusts layout and sizing based on available space (fluid layouts)
- **Adaptive Design:** UI selects different layouts or components based on device characteristics (breakpoint-based)

Flutter apps should typically combine both approaches for best user experience.

## Screen Size Detection

### MediaQuery

Use MediaQuery to access screen-wide properties:

```dart
Widget build(BuildContext context) {
  // Get screen size
  final screenSize = MediaQuery.sizeOf(context);
  final width = screenSize.width;
  final height = screenSize.height;

  // Get orientation
  final orientation = MediaQuery.orientationOf(context);

  // Get device pixel ratio
  final devicePixelRatio = MediaQuery.devicePixelRatioOf(context);

  // Get padding (safe area)
  final padding = MediaQuery.paddingOf(context);

  // Get view insets (keyboard)
  final viewInsets = MediaQuery.viewInsetsOf(context);

  return Container(
    width: width * 0.8, // 80% of screen width
    height: height * 0.5, // 50% of screen height
    child: Text('Content'),
  );
}
```

**Best Practices:**
- Use `MediaQuery.sizeOf(context)` instead of `MediaQuery.of(context).size` (more efficient)
- Access only needed properties (e.g., `orientationOf`, `paddingOf`) for better performance
- MediaQuery provides screen-wide information, not parent-constrained sizing

### LayoutBuilder

Use LayoutBuilder for parent-constrained responsive behavior:

```dart
LayoutBuilder(
  builder: (BuildContext context, BoxConstraints constraints) {
    // constraints.maxWidth = available width from parent
    // constraints.maxHeight = available height from parent
    // constraints.minWidth, constraints.minHeight = minimum constraints

    if (constraints.maxWidth > 600) {
      return WideLayout();
    } else {
      return NarrowLayout();
    }
  },
)
```

**When to Use:**
- Adapting layout based on parent widget size
- Building responsive widgets that work in different contexts
- Creating reusable components that adapt to available space

**MediaQuery vs LayoutBuilder:**
- MediaQuery: Full screen size, use for app-level decisions
- LayoutBuilder: Parent-constrained size, use for component-level decisions

## Breakpoints

### Standard Material Design Breakpoints

Material Design 3 recommends these breakpoints:

```dart
class Breakpoints {
  // Mobile devices (portrait)
  static const double mobile = 600;

  // Tablets (portrait) and large phones (landscape)
  static const double tablet = 1024;

  // Desktop and large tablets (landscape)
  static const double desktop = 1440;

  // Large desktop screens
  static const double largeDesktop = 1920;
}
```

### Implementing Breakpoint Logic

```dart
enum DeviceType { mobile, tablet, desktop }

class ResponsiveBreakpoints {
  static const double mobileBreakpoint = 600.0;
  static const double tabletBreakpoint = 1024.0;

  static DeviceType getDeviceType(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;

    if (width < mobileBreakpoint) {
      return DeviceType.mobile;
    } else if (width < tabletBreakpoint) {
      return DeviceType.tablet;
    } else {
      return DeviceType.desktop;
    }
  }

  static bool isMobile(BuildContext context) =>
      MediaQuery.sizeOf(context).width < mobileBreakpoint;

  static bool isTablet(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    return width >= mobileBreakpoint && width < tabletBreakpoint;
  }

  static bool isDesktop(BuildContext context) =>
      MediaQuery.sizeOf(context).width >= tabletBreakpoint;
}
```

### Responsive Value Selection

```dart
// Helper to select values based on breakpoint
T responsiveValue<T>(
  BuildContext context, {
  required T mobile,
  T? tablet,
  T? desktop,
}) {
  final width = MediaQuery.sizeOf(context).width;

  if (width >= 1024) {
    return desktop ?? tablet ?? mobile;
  } else if (width >= 600) {
    return tablet ?? mobile;
  } else {
    return mobile;
  }
}

// Usage
final padding = responsiveValue(
  context,
  mobile: 16.0,
  tablet: 24.0,
  desktop: 32.0,
);

final columns = responsiveValue(
  context,
  mobile: 1,
  tablet: 2,
  desktop: 3,
);
```

## Adaptive Navigation Patterns

### Adaptive Navigation Widget

```dart
class AdaptiveNavigation extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;
  final List<NavigationDestination> destinations;
  final Widget child;

  const AdaptiveNavigation({
    required this.selectedIndex,
    required this.onDestinationSelected,
    required this.destinations,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;

    // Desktop: Extended NavigationRail
    if (screenWidth >= 1024) {
      return Scaffold(
        body: Row(
          children: [
            NavigationRail(
              extended: true,
              selectedIndex: selectedIndex,
              onDestinationSelected: onDestinationSelected,
              labelType: NavigationRailLabelType.none,
              destinations: destinations.map((dest) {
                return NavigationRailDestination(
                  icon: dest.icon,
                  selectedIcon: dest.selectedIcon,
                  label: Text(dest.label),
                );
              }).toList(),
            ),
            VerticalDivider(thickness: 1, width: 1),
            Expanded(child: child),
          ],
        ),
      );
    }

    // Tablet: NavigationRail
    if (screenWidth >= 600) {
      return Scaffold(
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: selectedIndex,
              onDestinationSelected: onDestinationSelected,
              labelType: NavigationRailLabelType.all,
              destinations: destinations.map((dest) {
                return NavigationRailDestination(
                  icon: dest.icon,
                  selectedIcon: dest.selectedIcon,
                  label: Text(dest.label),
                );
              }).toList(),
            ),
            VerticalDivider(thickness: 1, width: 1),
            Expanded(child: child),
          ],
        ),
      );
    }

    // Mobile: NavigationBar + Drawer
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: onDestinationSelected,
        destinations: destinations,
      ),
    );
  }
}

// Usage
AdaptiveNavigation(
  selectedIndex: _selectedIndex,
  onDestinationSelected: (index) {
    setState(() => _selectedIndex = index);
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
  ],
  child: _buildContent(),
)
```

### Master-Detail Pattern

Adaptive pattern that shows list + detail on large screens, but separate pages on mobile:

```dart
class AdaptiveMasterDetail extends StatefulWidget {
  @override
  _AdaptiveMasterDetailState createState() => _AdaptiveMasterDetailState();
}

class _AdaptiveMasterDetailState extends State<AdaptiveMasterDetail> {
  int? _selectedItem;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Large screen: show both panels
        if (constraints.maxWidth >= 600) {
          return Row(
            children: [
              SizedBox(
                width: 300,
                child: _MasterPanel(
                  selectedItem: _selectedItem,
                  onItemSelected: (index) {
                    setState(() => _selectedItem = index);
                  },
                ),
              ),
              VerticalDivider(width: 1),
              Expanded(
                child: _selectedItem == null
                    ? Center(child: Text('Select an item'))
                    : _DetailPanel(itemIndex: _selectedItem!),
              ),
            ],
          );
        }

        // Small screen: show only master, navigate to detail
        return _MasterPanel(
          selectedItem: _selectedItem,
          onItemSelected: (index) {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => Scaffold(
                  appBar: AppBar(title: Text('Detail')),
                  body: _DetailPanel(itemIndex: index),
                ),
              ),
            );
          },
        );
      },
    );
  }
}

class _MasterPanel extends StatelessWidget {
  final int? selectedItem;
  final ValueChanged<int> onItemSelected;

  const _MasterPanel({
    required this.selectedItem,
    required this.onItemSelected,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: 20,
      itemBuilder: (context, index) {
        return ListTile(
          title: Text('Item $index'),
          selected: selectedItem == index,
          onTap: () => onItemSelected(index),
        );
      },
    );
  }
}

class _DetailPanel extends StatelessWidget {
  final int itemIndex;

  const _DetailPanel({required this.itemIndex});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Detail view for item $itemIndex'),
    );
  }
}
```

## Responsive Layout Widgets

### Flexible and Expanded

Use Flexible and Expanded in Row/Column for proportional sizing:

```dart
Row(
  children: [
    Flexible(
      flex: 1,
      child: Container(color: Colors.red, height: 50),
    ),
    Flexible(
      flex: 2,
      child: Container(color: Colors.blue, height: 50),
    ),
    Flexible(
      flex: 1,
      child: Container(color: Colors.green, height: 50),
    ),
  ],
)

// Expanded is Flexible with flex: 1 and fit: FlexFit.tight
Row(
  children: [
    Expanded(
      child: Container(color: Colors.red, height: 50),
    ),
    Expanded(
      flex: 2,
      child: Container(color: Colors.blue, height: 50),
    ),
  ],
)
```

### Wrap

Automatically wraps children to next line when space runs out:

```dart
Wrap(
  spacing: 8,
  runSpacing: 8,
  children: [
    Chip(label: Text('Tag 1')),
    Chip(label: Text('Tag 2')),
    Chip(label: Text('Tag 3')),
    Chip(label: Text('Tag 4')),
    Chip(label: Text('Tag 5')),
  ],
)
```

### FittedBox

Scales and positions child to fit parent:

```dart
FittedBox(
  fit: BoxFit.contain, // contain, cover, fill, fitWidth, fitHeight, none, scaleDown
  child: Text('This text will scale to fit'),
)
```

### AspectRatio

Maintains aspect ratio of child:

```dart
AspectRatio(
  aspectRatio: 16 / 9,
  child: Container(
    color: Colors.blue,
    child: Center(child: Text('16:9')),
  ),
)
```

### FractionallySizedBox

Sizes child as fraction of available space:

```dart
FractionallySizedBox(
  widthFactor: 0.8, // 80% of available width
  heightFactor: 0.5, // 50% of available height
  child: Container(color: Colors.blue),
)
```

## Grid Layouts

### Responsive GridView

```dart
class ResponsiveGrid extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Calculate columns based on width
        int columns = 1;
        if (constraints.maxWidth >= 1200) {
          columns = 4;
        } else if (constraints.maxWidth >= 800) {
          columns = 3;
        } else if (constraints.maxWidth >= 600) {
          columns = 2;
        }

        return GridView.builder(
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columns,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            childAspectRatio: 1.0,
          ),
          itemCount: 20,
          itemBuilder: (context, index) {
            return Card(
              child: Center(child: Text('Item $index')),
            );
          },
        );
      },
    );
  }
}
```

### GridView with Max Cross-Axis Extent

```dart
// Automatically determines column count based on max tile width
GridView.builder(
  gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
    maxCrossAxisExtent: 200, // Max width of each tile
    crossAxisSpacing: 16,
    mainAxisSpacing: 16,
    childAspectRatio: 1.0,
  ),
  itemCount: 20,
  itemBuilder: (context, index) {
    return Card(child: Center(child: Text('Item $index')));
  },
)
```

## Responsive Padding and Spacing

### Adaptive Padding

```dart
class AdaptivePadding extends StatelessWidget {
  final Widget child;

  const AdaptivePadding({required this.child});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;

    double padding;
    if (screenWidth >= 1024) {
      padding = 32.0;
    } else if (screenWidth >= 600) {
      padding = 24.0;
    } else {
      padding = 16.0;
    }

    return Padding(
      padding: EdgeInsets.all(padding),
      child: child,
    );
  }
}
```

### Content Width Constraints

Limit content width on large screens:

```dart
class ResponsiveContainer extends StatelessWidget {
  final Widget child;
  final double maxWidth;

  const ResponsiveContainer({
    required this.child,
    this.maxWidth = 1200,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: maxWidth),
        child: child,
      ),
    );
  }
}

// Usage in large screens
Scaffold(
  body: ResponsiveContainer(
    maxWidth: 1200,
    child: ListView(
      padding: EdgeInsets.all(16),
      children: [
        // Content centered with max width on large screens
      ],
    ),
  ),
)
```

## Orientation Handling

### OrientationBuilder

```dart
OrientationBuilder(
  builder: (context, orientation) {
    if (orientation == Orientation.portrait) {
      return Column(
        children: [
          Image.network('url'),
          Text('Portrait layout'),
        ],
      );
    } else {
      return Row(
        children: [
          Expanded(child: Image.network('url')),
          Expanded(child: Text('Landscape layout')),
        ],
      );
    }
  },
)
```

### Lock Orientation

```dart
import 'package:flutter/services.dart';

// Lock to portrait
SystemChrome.setPreferredOrientations([
  DeviceOrientation.portraitUp,
  DeviceOrientation.portraitDown,
]);

// Lock to landscape
SystemChrome.setPreferredOrientations([
  DeviceOrientation.landscapeLeft,
  DeviceOrientation.landscapeRight,
]);

// Allow all orientations
SystemChrome.setPreferredOrientations([
  DeviceOrientation.portraitUp,
  DeviceOrientation.portraitDown,
  DeviceOrientation.landscapeLeft,
  DeviceOrientation.landscapeRight,
]);
```

## Responsive Typography

### Text Scaling

```dart
class ResponsiveText extends StatelessWidget {
  final String text;

  const ResponsiveText(this.text);

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.sizeOf(context).width;

    double fontSize;
    if (screenWidth >= 1024) {
      fontSize = 24;
    } else if (screenWidth >= 600) {
      fontSize = 20;
    } else {
      fontSize = 16;
    }

    return Text(
      text,
      style: TextStyle(fontSize: fontSize),
    );
  }
}
```

### Using Theme Text Styles

Material Design 3 provides responsive text styles through ThemeData:

```dart
// Use theme text styles (automatically responsive)
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

// Material 3 text scale hierarchy:
// displayLarge, displayMedium, displaySmall
// headlineLarge, headlineMedium, headlineSmall
// titleLarge, titleMedium, titleSmall
// bodyLarge, bodyMedium, bodySmall
// labelLarge, labelMedium, labelSmall
```

## Complete Responsive App Example

```dart
class ResponsiveApp extends StatefulWidget {
  @override
  _ResponsiveAppState createState() => _ResponsiveAppState();
}

class _ResponsiveAppState extends State<ResponsiveApp> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth >= 1024;
        final isTablet = constraints.maxWidth >= 600 && !isDesktop;
        final isMobile = constraints.maxWidth < 600;

        return Scaffold(
          appBar: isMobile
              ? AppBar(
                  title: Text('Responsive App'),
                  actions: [
                    IconButton(
                      icon: Icon(Icons.search),
                      onPressed: () {},
                    ),
                  ],
                )
              : null,
          body: Row(
            children: [
              // Navigation Rail for tablet/desktop
              if (isTablet || isDesktop)
                NavigationRail(
                  extended: isDesktop,
                  selectedIndex: _selectedIndex,
                  onDestinationSelected: (index) {
                    setState(() => _selectedIndex = index);
                  },
                  labelType: isDesktop
                      ? NavigationRailLabelType.none
                      : NavigationRailLabelType.all,
                  leading: isDesktop
                      ? Padding(
                          padding: EdgeInsets.all(8),
                          child: FloatingActionButton(
                            onPressed: () {},
                            child: Icon(Icons.add),
                          ),
                        )
                      : null,
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
                    NavigationRailDestination(
                      icon: Icon(Icons.person_outlined),
                      selectedIcon: Icon(Icons.person),
                      label: Text('Profile'),
                    ),
                  ],
                ),

              if (isTablet || isDesktop)
                VerticalDivider(thickness: 1, width: 1),

              // Main content
              Expanded(
                child: ResponsiveContainer(
                  maxWidth: isDesktop ? 1200 : double.infinity,
                  child: _buildContent(isDesktop, isTablet, isMobile),
                ),
              ),
            ],
          ),

          // Bottom navigation for mobile
          bottomNavigationBar: isMobile
              ? NavigationBar(
                  selectedIndex: _selectedIndex,
                  onDestinationSelected: (index) {
                    setState(() => _selectedIndex = index);
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
              : null,

          floatingActionButton: isMobile
              ? FloatingActionButton(
                  onPressed: () {},
                  child: Icon(Icons.add),
                )
              : null,
        );
      },
    );
  }

  Widget _buildContent(bool isDesktop, bool isTablet, bool isMobile) {
    final padding = isDesktop ? 32.0 : (isTablet ? 24.0 : 16.0);
    final columns = isDesktop ? 3 : (isTablet ? 2 : 1);

    return GridView.builder(
      padding: EdgeInsets.all(padding),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columns,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1.0,
      ),
      itemCount: 20,
      itemBuilder: (context, index) {
        return Card(
          child: InkWell(
            onTap: () {},
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.image, size: isDesktop ? 64 : 48),
                  SizedBox(height: 8),
                  Text(
                    'Item $index',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
```

## Best Practices Summary

1. **Use MediaQuery for screen-wide decisions** (app-level layout)
2. **Use LayoutBuilder for parent-constrained decisions** (component-level)
3. **Define clear breakpoints** (mobile: <600, tablet: 600-1024, desktop: >1024)
4. **Combine responsive and adaptive techniques**
5. **NavigationBar for mobile, NavigationRail for tablet/desktop**
6. **Constrain content width on large screens** (max 1200-1440px)
7. **Scale padding and spacing** based on screen size
8. **Use theme text styles** for consistent typography
9. **Test on multiple screen sizes** and orientations
10. **Consider safe areas** (MediaQuery.paddingOf for notches, etc.)

## Additional Resources

- Flutter Adaptive Design Docs: https://docs.flutter.dev/ui/adaptive-responsive
- Material Design Layout Guidelines: https://m3.material.io/foundations/layout/understanding-layout
- Google Codelabs: https://codelabs.developers.google.com/codelabs/flutter-animated-responsive-layout
