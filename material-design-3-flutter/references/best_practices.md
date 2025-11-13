# Material Design 3 Best Practices

This reference provides best practices, performance tips, common patterns, and anti-patterns for building high-quality Material Design 3 Flutter applications.

## General Principles

### 1. Follow Material Design Guidelines

Material Design 3 provides comprehensive guidelines for:
- Component usage and behavior
- Layout and spacing
- Motion and animation
- Accessibility

Always reference the official Material Design 3 documentation: https://m3.material.io

### 2. Use Material 3 Defaults

Material 3 provides sensible defaults for all components. Override only when necessary:

```dart
// Good: Use defaults
AppBar(
  title: Text('Title'),
)

// Less ideal: Unnecessary overrides
AppBar(
  title: Text('Title'),
  elevation: 0, // Already default in M3
  backgroundColor: Colors.transparent, // Already default in M3
)
```

### 3. Prefer Material Widgets Over Custom Implementations

Material widgets are optimized, accessible, and follow design guidelines:

```dart
// Good: Use ListTile
ListTile(
  leading: Icon(Icons.person),
  title: Text('Name'),
  subtitle: Text('Email'),
  trailing: Icon(Icons.arrow_forward),
)

// Less ideal: Custom Row
Padding(
  padding: EdgeInsets.all(16),
  child: Row(
    children: [
      Icon(Icons.person),
      SizedBox(width: 16),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Name'),
            Text('Email'),
          ],
        ),
      ),
      Icon(Icons.arrow_forward),
    ],
  ),
)
```

## Widget Selection

### Navigation Components

**Mobile (< 600dp):**
- Use `NavigationBar` for primary navigation (3-5 destinations)
- Use `NavigationDrawer` for additional or secondary navigation
- Use `BottomSheet` for contextual actions

**Tablet (600-1024dp):**
- Use `NavigationRail` for primary navigation
- Consider `NavigationBar` for specific use cases

**Desktop (> 1024dp):**
- Use `NavigationRail` (extended) for primary navigation
- Use `NavigationDrawer` for supplementary navigation

### Button Hierarchy

```dart
// Primary action - use FilledButton
FilledButton(
  onPressed: () {},
  child: Text('Save'),
)

// Secondary action - use ElevatedButton or FilledButton.tonal
FilledButton.tonal(
  onPressed: () {},
  child: Text('Edit'),
)

// Tertiary action - use OutlinedButton
OutlinedButton(
  onPressed: () {},
  child: Text('Cancel'),
)

// Low emphasis - use TextButton
TextButton(
  onPressed: () {},
  child: Text('Learn More'),
)
```

**Best Practices:**
- One primary action per screen
- Limit buttons to 1-3 per screen
- Place primary action on the right (for LTR languages)
- Use consistent button placement across app

### Card vs Container

```dart
// Good: Use Card for Material Design elevation and styling
Card(
  child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Content'),
  ),
)

// Less ideal: Manual Container styling
Container(
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(12),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(0.1),
        blurRadius: 4,
      ),
    ],
  ),
  child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Content'),
  ),
)
```

**When to use:**
- **Card**: Material Design cards with elevation, content grouping
- **Container**: Layout, positioning, non-Material styling

## Performance Optimization

### 1. Use Builder Constructors for Lists

```dart
// Good: Efficient for large lists
ListView.builder(
  itemCount: 1000,
  itemBuilder: (context, index) {
    return ListTile(title: Text('Item $index'));
  },
)

// Bad: Loads all items at once
ListView(
  children: List.generate(
    1000,
    (index) => ListTile(title: Text('Item $index')),
  ),
)
```

### 2. Use const Constructors

```dart
// Good: Compile-time constant, reused
const Text('Static text')
const Icon(Icons.home)
const SizedBox(height: 16)

// Less optimal: Created at runtime
Text('Static text')
Icon(Icons.home)
SizedBox(height: 16)
```

### 3. Avoid Rebuilding Expensive Widgets

```dart
// Good: Extract to const widget
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const ExpensiveWidget(), // Won't rebuild
        Text('Dynamic: ${_value}'),
      ],
    );
  }
}

class ExpensiveWidget extends StatelessWidget {
  const ExpensiveWidget();

  @override
  Widget build(BuildContext context) {
    return Container(/* complex layout */);
  }
}
```

### 4. Use Keys Appropriately

```dart
// Good: Keys for stateful widgets in lists
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(
      key: ValueKey(items[index].id),
      title: Text(items[index].name),
    );
  },
)
```

### 5. Optimize Images

```dart
// Good: Specify dimensions to avoid unnecessary scaling
Image.network(
  'url',
  width: 200,
  height: 200,
  cacheWidth: 200, // Scales on load
  cacheHeight: 200,
  fit: BoxFit.cover,
)

// Good: Use CachedNetworkImage for network images
CachedNetworkImage(
  imageUrl: 'url',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
)
```

### 6. Minimize Widget Rebuilds

```dart
// Good: Separate stateful logic
class ParentWidget extends StatefulWidget {
  @override
  _ParentWidgetState createState() => _ParentWidgetState();
}

class _ParentWidgetState extends State<ParentWidget> {
  int _counter = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const StaticHeader(), // Won't rebuild
        DynamicCounter(counter: _counter), // Only this rebuilds
        FilledButton(
          onPressed: () => setState(() => _counter++),
          child: Text('Increment'),
        ),
      ],
    );
  }
}
```

## Layout Best Practices

### 1. Use Scaffold Structure

```dart
Scaffold(
  appBar: AppBar(title: Text('Title')),
  body: SafeArea(
    child: Padding(
      padding: EdgeInsets.all(16),
      child: content,
    ),
  ),
  floatingActionButton: FloatingActionButton(
    onPressed: () {},
    child: Icon(Icons.add),
  ),
)
```

### 2. Respect Safe Areas

```dart
// Good: Respects system UI (notches, status bar)
SafeArea(
  child: ListView(...),
)

// Good: Using MediaQuery padding
Padding(
  padding: MediaQuery.paddingOf(context),
  child: content,
)
```

### 3. Proper Spacing

Use consistent spacing throughout your app:

```dart
class Spacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
}

// Usage
Padding(
  padding: EdgeInsets.all(Spacing.md),
  child: content,
)

SizedBox(height: Spacing.lg)
```

### 4. Constrain Content Width on Large Screens

```dart
// Good: Constrain content width on desktop
Center(
  child: ConstrainedBox(
    constraints: BoxConstraints(maxWidth: 1200),
    child: content,
  ),
)
```

## Form Best Practices

### 1. Use Form Widget with Validation

```dart
class MyForm extends StatefulWidget {
  @override
  _MyFormState createState() => _MyFormState();
}

class _MyFormState extends State<MyForm> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: 'Email',
              hintText: 'Enter your email',
            ),
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.next,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter email';
              }
              if (!value.contains('@')) {
                return 'Please enter valid email';
              }
              return null;
            },
          ),
          SizedBox(height: 16),
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
      // Process form
    }
  }
}
```

### 2. Always Dispose Controllers

```dart
class MyWidget extends StatefulWidget {
  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final _focusNode = FocusNode();

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: _controller,
      focusNode: _focusNode,
    );
  }
}
```

## State Management

### 1. Keep State Local When Possible

```dart
// Good: Local state for simple UI state
class Counter extends StatefulWidget {
  @override
  _CounterState createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_count'),
        FilledButton(
          onPressed: () => setState(() => _count++),
          child: Text('Increment'),
        ),
      ],
    );
  }
}
```

### 2. Lift State When Needed

```dart
// Good: Lift state to parent when shared
class ParentWidget extends StatefulWidget {
  @override
  _ParentWidgetState createState() => _ParentWidgetState();
}

class _ParentWidgetState extends State<ParentWidget> {
  int _sharedValue = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ChildA(value: _sharedValue),
        ChildB(
          value: _sharedValue,
          onChanged: (value) => setState(() => _sharedValue = value),
        ),
      ],
    );
  }
}
```

### 3. Use InheritedWidget or Provider for App-Wide State

```dart
// Good: Use Provider for global state
class AppState extends ChangeNotifier {
  int _count = 0;
  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }
}

// In main.dart
ChangeNotifierProvider(
  create: (_) => AppState(),
  child: MyApp(),
)

// In widget
final appState = Provider.of<AppState>(context);
Text('Count: ${appState.count}')
```

## Navigation Best Practices

### 1. Use Named Routes for Complex Apps

```dart
MaterialApp(
  initialRoute: '/',
  routes: {
    '/': (context) => HomePage(),
    '/details': (context) => DetailsPage(),
    '/settings': (context) => SettingsPage(),
  },
)

// Navigate
Navigator.pushNamed(context, '/details');
```

### 2. Handle Back Button Properly

```dart
WillPopScope(
  onWillPop: () async {
    // Show confirmation dialog
    final shouldPop = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Discard changes?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Discard'),
          ),
        ],
      ),
    );
    return shouldPop ?? false;
  },
  child: Scaffold(
    appBar: AppBar(title: Text('Edit')),
    body: form,
  ),
)
```

### 3. Pass Data Between Routes

```dart
// Pass data
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => DetailsPage(item: item),
  ),
);

// Receive data
class DetailsPage extends StatelessWidget {
  final Item item;

  const DetailsPage({required this.item});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(item.name)),
      body: Text(item.description),
    );
  }
}

// Return data
final result = await Navigator.push<String>(
  context,
  MaterialPageRoute(builder: (context) => SelectionPage()),
);
if (result != null) {
  print('Selected: $result');
}
```

## Async Operations

### 1. Use FutureBuilder for Async Data

```dart
FutureBuilder<List<Item>>(
  future: fetchItems(),
  builder: (context, snapshot) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return Center(child: CircularProgressIndicator());
    }

    if (snapshot.hasError) {
      return Center(child: Text('Error: ${snapshot.error}'));
    }

    if (!snapshot.hasData || snapshot.data!.isEmpty) {
      return Center(child: Text('No items found'));
    }

    return ListView.builder(
      itemCount: snapshot.data!.length,
      itemBuilder: (context, index) {
        return ListTile(title: Text(snapshot.data![index].name));
      },
    );
  },
)
```

### 2. Use StreamBuilder for Real-Time Data

```dart
StreamBuilder<int>(
  stream: counterStream,
  initialData: 0,
  builder: (context, snapshot) {
    if (snapshot.hasError) {
      return Text('Error: ${snapshot.error}');
    }

    return Text('Count: ${snapshot.data}');
  },
)
```

### 3. Handle Loading States Properly

```dart
class DataPage extends StatefulWidget {
  @override
  _DataPageState createState() => _DataPageState();
}

class _DataPageState extends State<DataPage> {
  bool _isLoading = false;
  String? _error;
  List<Item>? _items;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final items = await fetchItems();
      setState(() {
        _items = items;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Error: $_error'),
            SizedBox(height: 16),
            FilledButton(
              onPressed: _loadData,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_items == null || _items!.isEmpty) {
      return Center(child: Text('No items'));
    }

    return ListView.builder(
      itemCount: _items!.length,
      itemBuilder: (context, index) {
        return ListTile(title: Text(_items![index].name));
      },
    );
  }
}
```

## Accessibility

### 1. Provide Semantic Labels

```dart
// Good: Semantic labels for screen readers
IconButton(
  icon: Icon(Icons.favorite),
  tooltip: 'Add to favorites',
  onPressed: () {},
)

Semantics(
  label: 'Profile picture',
  child: CircleAvatar(
    backgroundImage: NetworkImage('url'),
  ),
)
```

### 2. Ensure Sufficient Contrast

```dart
// Good: Use ColorScheme for proper contrast
Container(
  color: Theme.of(context).colorScheme.primary,
  child: Text(
    'Text',
    style: TextStyle(
      color: Theme.of(context).colorScheme.onPrimary,
    ),
  ),
)
```

### 3. Support Large Text Sizes

```dart
// Good: Use theme text styles (scale with user settings)
Text(
  'Content',
  style: Theme.of(context).textTheme.bodyLarge,
)

// Test with large text
MediaQuery(
  data: MediaQuery.of(context).copyWith(textScaleFactor: 2.0),
  child: MyWidget(),
)
```

### 4. Provide Tap Targets

Minimum tap target size: 48x48 dp

```dart
// Good: Sufficient tap area
IconButton(
  icon: Icon(Icons.delete),
  iconSize: 24,
  onPressed: () {},
  // IconButton is 48x48 by default
)

// Good: Add padding for small widgets
InkWell(
  onTap: () {},
  child: Padding(
    padding: EdgeInsets.all(12), // Makes 24x24 icon into 48x48 target
    child: Icon(Icons.edit, size: 24),
  ),
)
```

## Error Handling

### 1. Show User-Friendly Error Messages

```dart
// Good: User-friendly error messages
try {
  await saveData();
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Saved successfully')),
  );
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('Failed to save. Please try again.'),
      action: SnackBarAction(
        label: 'Retry',
        onPressed: () => saveData(),
      ),
    ),
  );
}
```

### 2. Provide Recovery Options

```dart
showDialog(
  context: context,
  builder: (context) => AlertDialog(
    title: Text('Error'),
    content: Text('Failed to load data. Check your internet connection.'),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: Text('Cancel'),
      ),
      FilledButton(
        onPressed: () {
          Navigator.pop(context);
          _retryLoad();
        },
        child: Text('Retry'),
      ),
    ],
  ),
)
```

## Testing

### 1. Write Widget Tests

```dart
testWidgets('Counter increments', (WidgetTester tester) async {
  await tester.pumpWidget(MyApp());

  expect(find.text('0'), findsOneWidget);
  expect(find.text('1'), findsNothing);

  await tester.tap(find.byIcon(Icons.add));
  await tester.pump();

  expect(find.text('0'), findsNothing);
  expect(find.text('1'), findsOneWidget);
});
```

### 2. Test Accessibility

```dart
testWidgets('Has semantic labels', (WidgetTester tester) async {
  await tester.pumpWidget(MyApp());

  expect(
    tester.getSemantics(find.byType(IconButton)),
    matchesSemantics(label: 'Add to favorites'),
  );
});
```

## Common Anti-Patterns to Avoid

### 1. Don't Use BuildContext After Async Gaps

```dart
// Bad: context might be invalid
Future<void> loadData() async {
  await Future.delayed(Duration(seconds: 2));
  Navigator.pop(context); // ❌ Context might be invalid
}

// Good: Check if mounted
Future<void> loadData() async {
  await Future.delayed(Duration(seconds: 2));
  if (mounted) {
    Navigator.pop(context); // ✓ Safe
  }
}
```

### 2. Don't Call setState in Build

```dart
// Bad: Infinite loop
Widget build(BuildContext context) {
  setState(() {}); // ❌ Never call setState in build
  return Container();
}
```

### 3. Don't Forget to Dispose Resources

```dart
// Bad: Memory leak
class MyWidget extends StatefulWidget {
  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  final _controller = TextEditingController();

  // ❌ No dispose method

  @override
  Widget build(BuildContext context) {
    return TextField(controller: _controller);
  }
}

// Good: Properly dispose
class _MyWidgetState extends State<MyWidget> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose(); // ✓ Clean up
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(controller: _controller);
  }
}
```

### 4. Don't Nest Too Deeply

```dart
// Bad: Deeply nested widgets
Widget build(BuildContext context) {
  return Container(
    child: Padding(
      child: Center(
        child: Column(
          children: [
            Container(
              child: Padding(
                child: Row(
                  children: [
                    // Too deep!
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

// Good: Extract to methods or separate widgets
Widget build(BuildContext context) {
  return Container(
    padding: EdgeInsets.all(16),
    child: Center(
      child: Column(
        children: [
          _buildHeader(),
          _buildContent(),
        ],
      ),
    ),
  );
}

Widget _buildHeader() {
  return Container(
    padding: EdgeInsets.all(8),
    child: _buildHeaderContent(),
  );
}
```

## Summary Checklist

- ✓ Use Material 3 with `useMaterial3: true`
- ✓ Follow Material Design guidelines
- ✓ Use appropriate navigation patterns for screen sizes
- ✓ Implement proper form validation
- ✓ Dispose controllers and resources
- ✓ Use const constructors where possible
- ✓ Optimize lists with builder constructors
- ✓ Handle loading and error states
- ✓ Provide accessibility labels and sufficient contrast
- ✓ Test on multiple screen sizes
- ✓ Write widget tests
- ✓ Extract complex widgets to separate classes
- ✓ Use theme colors instead of hardcoded values
- ✓ Respect safe areas
- ✓ Check `mounted` before using context after async operations

## Additional Resources

- Material Design 3: https://m3.material.io
- Flutter Best Practices: https://docs.flutter.dev/perf/best-practices
- Flutter Performance: https://docs.flutter.dev/perf
- Flutter Accessibility: https://docs.flutter.dev/accessibility-and-internationalization/accessibility
