# Material Design 3 Widget Catalog

This reference provides a comprehensive catalog of Material Design 3 widgets available in Flutter, organized by category.

## App Structure

### MaterialApp
The root widget that provides Material Design visual, behavioral, and motion-rich features.

```dart
MaterialApp(
  title: 'My App',
  theme: ThemeData(useMaterial3: true),
  darkTheme: ThemeData(useMaterial3: true, brightness: Brightness.dark),
  themeMode: ThemeMode.system,
  home: HomePage(),
  routes: {
    '/details': (context) => DetailsPage(),
  },
)
```

### Scaffold
Implements the basic Material Design visual layout structure.

```dart
Scaffold(
  appBar: AppBar(),
  body: Container(),
  floatingActionButton: FloatingActionButton(),
  bottomNavigationBar: NavigationBar(),
  drawer: NavigationDrawer(),
  endDrawer: Drawer(),
  bottomSheet: Container(),
)
```

**Properties:**
- `appBar`: Top app bar
- `body`: Primary content
- `floatingActionButton`: FAB (primary action)
- `floatingActionButtonLocation`: Position of FAB
- `bottomNavigationBar`: Bottom navigation
- `drawer`: Left side drawer
- `endDrawer`: Right side drawer
- `bottomSheet`: Persistent bottom sheet

## Top-Level Navigation

### AppBar
Material Design app bar (top bar).

```dart
AppBar(
  title: Text('Title'),
  leading: IconButton(icon: Icon(Icons.menu), onPressed: () {}),
  actions: [
    IconButton(icon: Icon(Icons.search), onPressed: () {}),
    IconButton(icon: Icon(Icons.more_vert), onPressed: () {}),
  ],
  backgroundColor: Colors.transparent, // M3 default
  elevation: 0, // M3 default
  centerTitle: true,
  bottom: TabBar(tabs: []),
)
```

**Material 3 Changes:**
- No elevation by default
- No background color by default (transparent)
- Inherits color from ColorScheme

### SliverAppBar
Scrollable app bar that can expand, collapse, or scroll with content.

```dart
CustomScrollView(
  slivers: [
    SliverAppBar(
      expandedHeight: 200,
      floating: false,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        title: Text('Title'),
        background: Image.network('url'),
      ),
    ),
    SliverList(delegate: SliverChildBuilderDelegate((context, index) {})),
  ],
)
```

### TabBar / TabBarView
Tab-based navigation for switching between content sections.

```dart
DefaultTabController(
  length: 3,
  child: Scaffold(
    appBar: AppBar(
      bottom: TabBar(
        tabs: [
          Tab(icon: Icon(Icons.home), text: 'Home'),
          Tab(icon: Icon(Icons.search), text: 'Search'),
          Tab(icon: Icon(Icons.person), text: 'Profile'),
        ],
      ),
    ),
    body: TabBarView(
      children: [
        HomeTab(),
        SearchTab(),
        ProfileTab(),
      ],
    ),
  ),
)
```

## Bottom Navigation

### NavigationBar
Material 3 bottom navigation bar (replaces BottomNavigationBar).

```dart
NavigationBar(
  selectedIndex: _currentIndex,
  onDestinationSelected: (index) => setState(() => _currentIndex = index),
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
  labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
)
```

**Properties:**
- `selectedIndex`: Current selected index
- `onDestinationSelected`: Callback when destination is tapped
- `destinations`: List of NavigationDestination
- `labelBehavior`: How labels are displayed
- `backgroundColor`: Background color
- `elevation`: Elevation (default varies in M3)

### BottomAppBar
Bottom app bar for actions and FAB integration.

```dart
BottomAppBar(
  shape: CircularNotchedRectangle(),
  notchMargin: 8.0,
  child: Row(
    mainAxisAlignment: MainAxisAlignment.spaceAround,
    children: [
      IconButton(icon: Icon(Icons.menu), onPressed: () {}),
      IconButton(icon: Icon(Icons.search), onPressed: () {}),
      SizedBox(width: 48), // Space for FAB
      IconButton(icon: Icon(Icons.favorite), onPressed: () {}),
      IconButton(icon: Icon(Icons.more_vert), onPressed: () {}),
    ],
  ),
)
```

## Side Navigation

### NavigationRail
Vertical navigation for tablet/desktop layouts.

```dart
NavigationRail(
  selectedIndex: _selectedIndex,
  onDestinationSelected: (index) => setState(() => _selectedIndex = index),
  labelType: NavigationRailLabelType.all,
  extended: false, // Set true for extended labels
  leading: FloatingActionButton(
    onPressed: () {},
    child: Icon(Icons.add),
  ),
  trailing: IconButton(
    icon: Icon(Icons.settings),
    onPressed: () {},
  ),
  destinations: [
    NavigationRailDestination(
      icon: Icon(Icons.home_outlined),
      selectedIcon: Icon(Icons.home),
      label: Text('Home'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.bookmark_outlined),
      selectedIcon: Icon(Icons.bookmark),
      label: Text('Saved'),
    ),
  ],
)
```

**Properties:**
- `extended`: Whether to show extended labels
- `labelType`: How labels are displayed (none, selected, all)
- `leading`: Widget shown at the top
- `trailing`: Widget shown at the bottom

### NavigationDrawer
Material 3 navigation drawer (side menu).

```dart
NavigationDrawer(
  selectedIndex: _selectedIndex,
  onDestinationSelected: (index) {
    setState(() => _selectedIndex = index);
    Navigator.pop(context);
  },
  children: [
    Padding(
      padding: EdgeInsets.fromLTRB(28, 16, 16, 10),
      child: Text('Menu', style: Theme.of(context).textTheme.titleSmall),
    ),
    NavigationDrawerDestination(
      icon: Icon(Icons.inbox_outlined),
      selectedIcon: Icon(Icons.inbox),
      label: Text('Inbox'),
    ),
    Divider(indent: 28, endIndent: 28),
    Padding(
      padding: EdgeInsets.fromLTRB(28, 16, 16, 10),
      child: Text('Labels', style: Theme.of(context).textTheme.titleSmall),
    ),
    NavigationDrawerDestination(
      icon: Icon(Icons.label_outlined),
      selectedIcon: Icon(Icons.label),
      label: Text('Family'),
    ),
  ],
)
```

### Drawer
Generic drawer (legacy, use NavigationDrawer for M3).

```dart
Drawer(
  child: ListView(
    children: [
      DrawerHeader(
        decoration: BoxDecoration(color: Colors.blue),
        child: Text('Header'),
      ),
      ListTile(
        leading: Icon(Icons.home),
        title: Text('Home'),
        onTap: () {},
      ),
    ],
  ),
)
```

## Buttons

### FilledButton
Primary action button (Material 3 main button).

```dart
FilledButton(
  onPressed: () {},
  onLongPress: () {},
  child: Text('Filled Button'),
  style: FilledButton.styleFrom(
    backgroundColor: Colors.blue,
    foregroundColor: Colors.white,
    disabledBackgroundColor: Colors.grey,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
  ),
)

// Tonal variant
FilledButton.tonal(
  onPressed: () {},
  child: Text('Tonal Button'),
)
```

### ElevatedButton
Secondary action button with elevation.

```dart
ElevatedButton(
  onPressed: () {},
  child: Text('Elevated Button'),
  style: ElevatedButton.styleFrom(
    backgroundColor: Colors.blue,
    foregroundColor: Colors.white,
    elevation: 2,
    shadowColor: Colors.black,
  ),
)
```

### OutlinedButton
Tertiary action button with border.

```dart
OutlinedButton(
  onPressed: () {},
  child: Text('Outlined Button'),
  style: OutlinedButton.styleFrom(
    foregroundColor: Colors.blue,
    side: BorderSide(color: Colors.blue, width: 1),
  ),
)
```

### TextButton
Low-emphasis button without background.

```dart
TextButton(
  onPressed: () {},
  child: Text('Text Button'),
  style: TextButton.styleFrom(
    foregroundColor: Colors.blue,
  ),
)
```

### IconButton
Button with only an icon.

```dart
IconButton(
  icon: Icon(Icons.favorite),
  onPressed: () {},
  color: Colors.red,
  iconSize: 24,
  tooltip: 'Favorite',
)

// Filled variant (Material 3)
IconButton.filled(
  icon: Icon(Icons.add),
  onPressed: () {},
)

// Outlined variant (Material 3)
IconButton.outlined(
  icon: Icon(Icons.edit),
  onPressed: () {},
)

// Tonal variant (Material 3)
IconButton.filledTonal(
  icon: Icon(Icons.settings),
  onPressed: () {},
)
```

### FloatingActionButton
Primary action button that floats above content.

```dart
FloatingActionButton(
  onPressed: () {},
  child: Icon(Icons.add),
  tooltip: 'Add',
  backgroundColor: Colors.blue,
)

// Extended FAB
FloatingActionButton.extended(
  onPressed: () {},
  icon: Icon(Icons.add),
  label: Text('Create'),
)

// Small FAB
FloatingActionButton.small(
  onPressed: () {},
  child: Icon(Icons.add),
)

// Large FAB (Material 3)
FloatingActionButton.large(
  onPressed: () {},
  child: Icon(Icons.add),
)
```

### SegmentedButton
Multiple choice button group (Material 3).

```dart
SegmentedButton<String>(
  segments: [
    ButtonSegment(
      value: 'day',
      label: Text('Day'),
      icon: Icon(Icons.calendar_today),
    ),
    ButtonSegment(value: 'week', label: Text('Week')),
    ButtonSegment(value: 'month', label: Text('Month')),
  ],
  selected: {'day'},
  onSelectionChanged: (Set<String> newSelection) {
    setState(() => _selection = newSelection);
  },
  multiSelectionEnabled: false,
  showSelectedIcon: true,
)
```

### DropdownButton
Button that displays a dropdown menu.

```dart
DropdownButton<String>(
  value: _selectedValue,
  items: [
    DropdownMenuItem(value: '1', child: Text('Option 1')),
    DropdownMenuItem(value: '2', child: Text('Option 2')),
  ],
  onChanged: (String? value) {
    setState(() => _selectedValue = value);
  },
  hint: Text('Select option'),
  underline: Container(),
)
```

## Selection Controls

### Checkbox
Binary selection control.

```dart
Checkbox(
  value: _isChecked,
  onChanged: (bool? value) {
    setState(() => _isChecked = value ?? false);
  },
  activeColor: Colors.blue,
  checkColor: Colors.white,
  tristate: false,
)

// CheckboxListTile for list integration
CheckboxListTile(
  title: Text('Option'),
  subtitle: Text('Description'),
  value: _isChecked,
  onChanged: (bool? value) {
    setState(() => _isChecked = value ?? false);
  },
  secondary: Icon(Icons.settings),
  controlAffinity: ListTileControlAffinity.trailing,
)
```

### Radio
Single selection from a set.

```dart
Radio<String>(
  value: 'option1',
  groupValue: _selectedOption,
  onChanged: (String? value) {
    setState(() => _selectedOption = value);
  },
  activeColor: Colors.blue,
)

// RadioListTile for list integration
RadioListTile<String>(
  title: Text('Option 1'),
  subtitle: Text('Description'),
  value: 'option1',
  groupValue: _selectedOption,
  onChanged: (String? value) {
    setState(() => _selectedOption = value);
  },
  secondary: Icon(Icons.radio),
)
```

### Switch
Toggle between on/off states.

```dart
Switch(
  value: _isSwitched,
  onChanged: (bool value) {
    setState(() => _isSwitched = value);
  },
  activeColor: Colors.blue,
  activeTrackColor: Colors.blue.shade200,
  inactiveThumbColor: Colors.grey,
  inactiveTrackColor: Colors.grey.shade300,
)

// SwitchListTile for list integration
SwitchListTile(
  title: Text('Enable notifications'),
  subtitle: Text('Receive alerts'),
  value: _isSwitched,
  onChanged: (bool value) {
    setState(() => _isSwitched = value);
  },
  secondary: Icon(Icons.notifications),
)
```

### Slider
Select from a range of values.

```dart
Slider(
  value: _sliderValue,
  min: 0,
  max: 100,
  divisions: 10,
  label: _sliderValue.round().toString(),
  onChanged: (double value) {
    setState(() => _sliderValue = value);
  },
  activeColor: Colors.blue,
  inactiveColor: Colors.grey,
)

// RangeSlider
RangeSlider(
  values: _rangeValues,
  min: 0,
  max: 100,
  divisions: 10,
  labels: RangeLabels(
    _rangeValues.start.round().toString(),
    _rangeValues.end.round().toString(),
  ),
  onChanged: (RangeValues values) {
    setState(() => _rangeValues = values);
  },
)
```

## Text Input

### TextField
Single-line or multi-line text input.

```dart
TextField(
  decoration: InputDecoration(
    labelText: 'Label',
    hintText: 'Hint text',
    helperText: 'Helper text',
    prefixIcon: Icon(Icons.email),
    suffixIcon: Icon(Icons.visibility),
    border: OutlineInputBorder(),
    filled: true,
    fillColor: Colors.grey.shade100,
  ),
  controller: _controller,
  keyboardType: TextInputType.emailAddress,
  textInputAction: TextInputAction.next,
  obscureText: false,
  maxLines: 1,
  maxLength: 50,
  onChanged: (String value) {},
  onSubmitted: (String value) {},
)
```

### TextFormField
TextField with built-in Form integration.

```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Email',
    border: OutlineInputBorder(),
  ),
  validator: (String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter email';
    }
    if (!value.contains('@')) {
      return 'Invalid email';
    }
    return null;
  },
  onSaved: (String? value) {
    _email = value ?? '';
  },
  autovalidateMode: AutovalidateMode.onUserInteraction,
)
```

### DropdownMenu
Material 3 dropdown menu for selection (new in M3).

```dart
DropdownMenu<String>(
  label: Text('Select option'),
  initialSelection: '1',
  dropdownMenuEntries: [
    DropdownMenuEntry(value: '1', label: 'Option 1', leadingIcon: Icon(Icons.star)),
    DropdownMenuEntry(value: '2', label: 'Option 2'),
    DropdownMenuEntry(value: '3', label: 'Option 3'),
  ],
  onSelected: (String? value) {
    setState(() => _selectedValue = value);
  },
  width: 200,
  menuHeight: 300,
)
```

## Information Display

### Text
Display text with styling.

```dart
Text(
  'Text content',
  style: TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.bold,
    color: Colors.black,
    letterSpacing: 1.0,
    height: 1.5,
  ),
  textAlign: TextAlign.center,
  maxLines: 2,
  overflow: TextOverflow.ellipsis,
)
```

### RichText / TextSpan
Display text with multiple styles.

```dart
RichText(
  text: TextSpan(
    text: 'Hello ',
    style: TextStyle(color: Colors.black),
    children: [
      TextSpan(
        text: 'bold',
        style: TextStyle(fontWeight: FontWeight.bold),
      ),
      TextSpan(text: ' and '),
      TextSpan(
        text: 'colored',
        style: TextStyle(color: Colors.blue),
      ),
    ],
  ),
)
```

### Icon
Display Material Design icons.

```dart
Icon(
  Icons.favorite,
  size: 24,
  color: Colors.red,
)
```

### Image
Display images from various sources.

```dart
// Network image
Image.network(
  'https://example.com/image.png',
  width: 200,
  height: 200,
  fit: BoxFit.cover,
  loadingBuilder: (context, child, loadingProgress) {
    if (loadingProgress == null) return child;
    return CircularProgressIndicator();
  },
  errorBuilder: (context, error, stackTrace) {
    return Icon(Icons.error);
  },
)

// Asset image
Image.asset('assets/image.png')

// File image
Image.file(File('path/to/file'))
```

### CircleAvatar
Display circular avatar images or initials.

```dart
CircleAvatar(
  radius: 30,
  backgroundImage: NetworkImage('url'),
  backgroundColor: Colors.blue,
  child: Text('AB'),
)
```

### Chip
Compact element representing an attribute, text, or action.

```dart
Chip(
  avatar: CircleAvatar(child: Icon(Icons.person)),
  label: Text('Chip'),
  onDeleted: () {},
  deleteIcon: Icon(Icons.close),
)

// InputChip
InputChip(
  label: Text('Input Chip'),
  selected: _isSelected,
  onSelected: (bool value) {
    setState(() => _isSelected = value);
  },
  avatar: Icon(Icons.tag),
)

// FilterChip
FilterChip(
  label: Text('Filter'),
  selected: _isSelected,
  onSelected: (bool value) {
    setState(() => _isSelected = value);
  },
  showCheckmark: true,
)

// ActionChip
ActionChip(
  label: Text('Action'),
  onPressed: () {},
  avatar: Icon(Icons.add),
)

// ChoiceChip
ChoiceChip(
  label: Text('Choice'),
  selected: _isSelected,
  onSelected: (bool value) {
    setState(() => _isSelected = value);
  },
)
```

### Badge
Display notification badge (Material 3).

```dart
Badge(
  label: Text('3'),
  child: Icon(Icons.notifications),
)

Badge.count(
  count: 10,
  child: Icon(Icons.email),
)

Badge(
  child: Icon(Icons.message), // Shows small dot
)
```

### Tooltip
Display informational tooltip on long press.

```dart
Tooltip(
  message: 'This is a tooltip',
  child: Icon(Icons.info),
  preferBelow: false,
  verticalOffset: 20,
)
```

## Layout

### Container
Box model widget with padding, margin, decoration.

```dart
Container(
  width: 200,
  height: 100,
  padding: EdgeInsets.all(16),
  margin: EdgeInsets.symmetric(vertical: 8),
  decoration: BoxDecoration(
    color: Colors.blue,
    borderRadius: BorderRadius.circular(8),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(0.1),
        blurRadius: 4,
        offset: Offset(0, 2),
      ),
    ],
  ),
  child: Text('Content'),
)
```

### Card
Material Design card.

```dart
Card(
  elevation: 2,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(12),
  ),
  child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Card content'),
  ),
)

// Material 3 variants
Card.elevated(elevation: 2, child: Content())
Card.filled(child: Content())
Card.outlined(child: Content())
```

### ListTile
Standard list item with leading/trailing widgets.

```dart
ListTile(
  leading: Icon(Icons.person),
  title: Text('Title'),
  subtitle: Text('Subtitle'),
  trailing: Icon(Icons.arrow_forward),
  onTap: () {},
  onLongPress: () {},
  enabled: true,
  selected: false,
  dense: false,
  isThreeLine: false,
)
```

### ExpansionTile
Collapsible list item.

```dart
ExpansionTile(
  title: Text('Title'),
  subtitle: Text('Subtitle'),
  leading: Icon(Icons.folder),
  children: [
    ListTile(title: Text('Item 1')),
    ListTile(title: Text('Item 2')),
  ],
  initiallyExpanded: false,
  onExpansionChanged: (bool expanded) {},
)
```

### Divider / VerticalDivider
Horizontal or vertical line separator.

```dart
Divider(
  height: 1,
  thickness: 1,
  indent: 16,
  endIndent: 16,
  color: Colors.grey,
)

VerticalDivider(
  width: 1,
  thickness: 1,
  indent: 16,
  endIndent: 16,
)
```

## Lists and Grids

### ListView
Scrollable list of widgets.

```dart
// Basic ListView
ListView(
  children: [
    ListTile(title: Text('Item 1')),
    ListTile(title: Text('Item 2')),
  ],
)

// ListView.builder (efficient for large lists)
ListView.builder(
  itemCount: 100,
  itemBuilder: (context, index) {
    return ListTile(title: Text('Item $index'));
  },
)

// ListView.separated
ListView.separated(
  itemCount: 100,
  separatorBuilder: (context, index) => Divider(),
  itemBuilder: (context, index) {
    return ListTile(title: Text('Item $index'));
  },
)
```

### GridView
Scrollable grid of widgets.

```dart
// Fixed cross-axis count
GridView.count(
  crossAxisCount: 2,
  crossAxisSpacing: 8,
  mainAxisSpacing: 8,
  children: [
    Card(child: Center(child: Text('1'))),
    Card(child: Center(child: Text('2'))),
  ],
)

// GridView.builder (efficient)
GridView.builder(
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 3,
    crossAxisSpacing: 8,
    mainAxisSpacing: 8,
    childAspectRatio: 1.0,
  ),
  itemCount: 100,
  itemBuilder: (context, index) {
    return Card(child: Center(child: Text('$index')));
  },
)

// GridView.extent (max cross-axis extent)
GridView.extent(
  maxCrossAxisExtent: 150,
  children: [
    Card(child: Center(child: Text('1'))),
    Card(child: Center(child: Text('2'))),
  ],
)
```

### ReorderableListView
List that allows drag-to-reorder.

```dart
ReorderableListView(
  onReorder: (int oldIndex, int newIndex) {
    setState(() {
      if (newIndex > oldIndex) newIndex--;
      final item = items.removeAt(oldIndex);
      items.insert(newIndex, item);
    });
  },
  children: items.map((item) => ListTile(
    key: ValueKey(item),
    title: Text(item),
  )).toList(),
)
```

## Dialogs

### AlertDialog
Simple dialog for alerts and confirmations.

```dart
showDialog(
  context: context,
  barrierDismissible: false,
  builder: (context) => AlertDialog(
    title: Text('Title'),
    content: Text('Dialog content'),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: Text('Cancel'),
      ),
      FilledButton(
        onPressed: () {
          Navigator.pop(context);
          // Perform action
        },
        child: Text('OK'),
      ),
    ],
  ),
)
```

### SimpleDialog
Dialog with list of options.

```dart
showDialog(
  context: context,
  builder: (context) => SimpleDialog(
    title: Text('Select option'),
    children: [
      SimpleDialogOption(
        onPressed: () => Navigator.pop(context, 'option1'),
        child: Text('Option 1'),
      ),
      SimpleDialogOption(
        onPressed: () => Navigator.pop(context, 'option2'),
        child: Text('Option 2'),
      ),
    ],
  ),
)
```

### Dialog
Custom dialog with full control.

```dart
showDialog(
  context: context,
  builder: (context) => Dialog(
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
    child: Container(
      padding: EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Custom Dialog'),
          SizedBox(height: 16),
          FilledButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
        ],
      ),
    ),
  ),
)
```

## Bottom Sheets

### showModalBottomSheet
Modal bottom sheet (overlays content).

```dart
showModalBottomSheet(
  context: context,
  isScrollControlled: true,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
  ),
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
        ListTile(
          leading: Icon(Icons.link),
          title: Text('Get link'),
          onTap: () {},
        ),
      ],
    ),
  ),
)
```

### showBottomSheet
Persistent bottom sheet (pushes content up).

```dart
showBottomSheet(
  context: context,
  builder: (context) => Container(
    height: 200,
    padding: EdgeInsets.all(16),
    child: Text('Persistent bottom sheet'),
  ),
)
```

## Snackbars and Banners

### SnackBar
Temporary message at bottom of screen.

```dart
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text('Message'),
    duration: Duration(seconds: 3),
    action: SnackBarAction(
      label: 'Undo',
      onPressed: () {},
    ),
    behavior: SnackBarBehavior.floating,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
  ),
)
```

### MaterialBanner
Persistent banner at top of screen.

```dart
ScaffoldMessenger.of(context).showMaterialBanner(
  MaterialBanner(
    content: Text('Material Banner message'),
    actions: [
      TextButton(
        onPressed: () {
          ScaffoldMessenger.of(context).hideCurrentMaterialBanner();
        },
        child: Text('Dismiss'),
      ),
    ],
    leading: Icon(Icons.info),
  ),
)
```

## Progress Indicators

### CircularProgressIndicator
Circular loading indicator.

```dart
// Indeterminate
CircularProgressIndicator()

// Determinate
CircularProgressIndicator(
  value: 0.7, // 0.0 to 1.0
  backgroundColor: Colors.grey.shade200,
  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
  strokeWidth: 4,
)
```

### LinearProgressIndicator
Linear loading bar.

```dart
// Indeterminate
LinearProgressIndicator()

// Determinate
LinearProgressIndicator(
  value: 0.5,
  backgroundColor: Colors.grey.shade200,
  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
  minHeight: 8,
)
```

### RefreshIndicator
Pull-to-refresh indicator.

```dart
RefreshIndicator(
  onRefresh: () async {
    await Future.delayed(Duration(seconds: 2));
    // Refresh data
  },
  child: ListView(
    children: items.map((item) => ListTile(title: Text(item))).toList(),
  ),
)
```

## Date and Time Pickers

### showDatePicker
Date selection dialog.

```dart
final DateTime? picked = await showDatePicker(
  context: context,
  initialDate: DateTime.now(),
  firstDate: DateTime(2020),
  lastDate: DateTime(2030),
  helpText: 'Select date',
  cancelText: 'Cancel',
  confirmText: 'OK',
)
```

### showTimePicker
Time selection dialog.

```dart
final TimeOfDay? picked = await showTimePicker(
  context: context,
  initialTime: TimeOfDay.now(),
  helpText: 'Select time',
  cancelText: 'Cancel',
  confirmText: 'OK',
)
```

### showDateRangePicker
Date range selection dialog.

```dart
final DateTimeRange? picked = await showDateRangePicker(
  context: context,
  firstDate: DateTime(2020),
  lastDate: DateTime(2030),
  initialDateRange: DateTimeRange(
    start: DateTime.now(),
    end: DateTime.now().add(Duration(days: 7)),
  ),
)
```

## Menus

### PopupMenuButton
Button that shows a popup menu.

```dart
PopupMenuButton<String>(
  onSelected: (String value) {
    // Handle selection
  },
  itemBuilder: (BuildContext context) => [
    PopupMenuItem(
      value: 'edit',
      child: Row(
        children: [
          Icon(Icons.edit),
          SizedBox(width: 8),
          Text('Edit'),
        ],
      ),
    ),
    PopupMenuItem(
      value: 'delete',
      child: Row(
        children: [
          Icon(Icons.delete),
          SizedBox(width: 8),
          Text('Delete'),
        ],
      ),
    ),
    PopupMenuDivider(),
    PopupMenuItem(
      value: 'share',
      child: Row(
        children: [
          Icon(Icons.share),
          SizedBox(width: 8),
          Text('Share'),
        ],
      ),
    ),
  ],
)
```

### MenuAnchor / MenuBar
Material 3 menu system (new in M3).

```dart
MenuAnchor(
  builder: (context, controller, child) {
    return FilledButton(
      onPressed: () {
        if (controller.isOpen) {
          controller.close();
        } else {
          controller.open();
        }
      },
      child: Text('Open Menu'),
    );
  },
  menuChildren: [
    MenuItemButton(
      leadingIcon: Icon(Icons.edit),
      child: Text('Edit'),
      onPressed: () {},
    ),
    MenuItemButton(
      leadingIcon: Icon(Icons.delete),
      child: Text('Delete'),
      onPressed: () {},
    ),
  ],
)
```

## Search

### SearchBar
Material 3 search bar (new in M3).

```dart
SearchBar(
  hintText: 'Search',
  leading: Icon(Icons.search),
  trailing: [
    IconButton(
      icon: Icon(Icons.close),
      onPressed: () {},
    ),
  ],
  onChanged: (String value) {
    // Handle search
  },
  onSubmitted: (String value) {
    // Handle search submit
  },
)
```

### SearchAnchor
Material 3 search with suggestions (new in M3).

```dart
SearchAnchor(
  builder: (BuildContext context, SearchController controller) {
    return SearchBar(
      controller: controller,
      hintText: 'Search',
      onTap: () {
        controller.openView();
      },
      onChanged: (_) {
        controller.openView();
      },
    );
  },
  suggestionsBuilder: (BuildContext context, SearchController controller) {
    return List<ListTile>.generate(5, (int index) {
      final String item = 'Suggestion ${index + 1}';
      return ListTile(
        title: Text(item),
        onTap: () {
          controller.closeView(item);
        },
      );
    });
  },
)
```

## Stepper

### Stepper
Multi-step process indicator.

```dart
Stepper(
  currentStep: _currentStep,
  onStepContinue: () {
    setState(() {
      if (_currentStep < 2) _currentStep++;
    });
  },
  onStepCancel: () {
    setState(() {
      if (_currentStep > 0) _currentStep--;
    });
  },
  onStepTapped: (int step) {
    setState(() => _currentStep = step);
  },
  steps: [
    Step(
      title: Text('Step 1'),
      content: Text('Content for step 1'),
      isActive: _currentStep >= 0,
      state: _currentStep > 0 ? StepState.complete : StepState.indexed,
    ),
    Step(
      title: Text('Step 2'),
      content: Text('Content for step 2'),
      isActive: _currentStep >= 1,
      state: _currentStep > 1 ? StepState.complete : StepState.indexed,
    ),
  ],
)
```

## Other Widgets

### Ink / InkWell
Material ink splash effect.

```dart
InkWell(
  onTap: () {},
  onLongPress: () {},
  splashColor: Colors.blue.withOpacity(0.3),
  highlightColor: Colors.blue.withOpacity(0.1),
  borderRadius: BorderRadius.circular(8),
  child: Container(
    padding: EdgeInsets.all(16),
    child: Text('Tap me'),
  ),
)
```

### Material
Provides Material Design visual.

```dart
Material(
  color: Colors.white,
  elevation: 4,
  shadowColor: Colors.black,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8),
  ),
  child: Container(
    padding: EdgeInsets.all(16),
    child: Text('Material widget'),
  ),
)
```

This catalog covers the primary Material Design 3 widgets available in Flutter. For complete API documentation, refer to https://api.flutter.dev/flutter/material/material-library.html
