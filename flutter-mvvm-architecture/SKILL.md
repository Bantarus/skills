---
name: flutter-mvvm-architecture
description: Comprehensive guide for implementing Model-View-ViewModel (MVVM) architecture in Flutter with ChangeNotifier and Provider for state management. This skill should be used when structuring Flutter applications for scalability, testability, and separation of concerns, or when managing complex application state. Covers MVVM pattern implementation, ChangeNotifier usage, Provider integration, dependency injection, and architectural best practices.
---

# Flutter MVVM Architecture and State Management

## Overview

Model-View-ViewModel (MVVM) is an architectural pattern that separates presentation logic from UI code, enabling testable, maintainable, and scalable Flutter applications. Combined with ChangeNotifier and Provider, MVVM provides a robust foundation for managing application state and business logic.

**Core Components:**
- **Model** - Data structures and business entities
- **View** - UI widgets (StatelessWidget or StatefulWidget)
- **ViewModel** - Presentation logic and state management (extends ChangeNotifier)
- **Provider** - Dependency injection and state propagation

**Architecture Principles:**
- Separation of concerns
- Unidirectional data flow
- Testability
- Reusability

**Official Resources:**
- Flutter App Architecture: https://docs.flutter.dev/app-architecture/guide
- State Management: https://docs.flutter.dev/get-started/fundamentals/state-management
- Provider Package: https://pub.dev/packages/provider
- Updated: November 14, 2025

**Use Cases:**
- Medium to large applications
- Apps requiring complex state management
- Team projects needing clear architecture
- Applications requiring extensive testing
- Component galleries and design systems

## MVVM Architecture Layers

### 1. Model Layer

Models represent data structures and business entities:

```dart
// models/user.dart
class User {
  final String id;
  final String name;
  final String email;
  final String avatarUrl;

  const User({
    required this.id,
    required this.name,
    required this.email,
    required this.avatarUrl,
  });

  // Immutable copy with modifications
  User copyWith({
    String? id,
    String? name,
    String? email,
    String? avatarUrl,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      avatarUrl: avatarUrl ?? this.avatarUrl,
    );
  }

  // JSON serialization
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      avatarUrl: json['avatarUrl'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'avatarUrl': avatarUrl,
    };
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
```

**Model Best Practices:**
- Immutable data classes
- Implement `copyWith()` for modifications
- Override `==` and `hashCode` for comparisons
- Include JSON serialization (if needed)
- No business logic (pure data)

### 2. ViewModel Layer

ViewModels manage state and presentation logic using ChangeNotifier:

```dart
// viewmodels/user_profile_viewmodel.dart
import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/user_service.dart';

class UserProfileViewModel extends ChangeNotifier {
  final UserService _userService;

  UserProfileViewModel(this._userService);

  // State
  User? _user;
  bool _isLoading = false;
  String? _errorMessage;

  // Getters (public interface)
  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasError => _errorMessage != null;

  // Computed properties
  String get displayName => _user?.name ?? 'Unknown User';
  String get initials {
    if (_user == null) return '?';
    final names = _user!.name.split(' ');
    if (names.length >= 2) {
      return '${names[0][0]}${names[1][0]}'.toUpperCase();
    }
    return names[0][0].toUpperCase();
  }

  // Actions
  Future<void> loadUser(String userId) async {
    _setLoading(true);
    _clearError();

    try {
      _user = await _userService.fetchUser(userId);
      notifyListeners();
    } catch (e) {
      _setError('Failed to load user: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> updateProfile({
    String? name,
    String? email,
  }) async {
    if (_user == null) return;

    _setLoading(true);
    _clearError();

    try {
      final updatedUser = _user!.copyWith(
        name: name,
        email: email,
      );

      await _userService.updateUser(updatedUser);
      _user = updatedUser;
      notifyListeners();
    } catch (e) {
      _setError('Failed to update profile: $e');
    } finally {
      _setLoading(false);
    }
  }

  void clearError() {
    _clearError();
  }

  // Private methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String message) {
    _errorMessage = message;
    notifyListeners();
  }

  void _clearError() {
    if (_errorMessage != null) {
      _errorMessage = null;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    // Clean up resources
    super.dispose();
  }
}
```

**ViewModel Best Practices:**
- Extend ChangeNotifier
- Private state (_variableName), public getters
- Call `notifyListeners()` after state changes
- Handle async operations properly
- Provide clear public API (methods and getters)
- No Flutter UI dependencies (no BuildContext)

### 3. View Layer

Views consume ViewModel state and render UI:

```dart
// views/user_profile_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/user_profile_viewmodel.dart';

class UserProfileScreen extends StatelessWidget {
  final String userId;

  const UserProfileScreen({required this.userId});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) {
        final userService = context.read<UserService>();
        final viewModel = UserProfileViewModel(userService);
        viewModel.loadUser(userId);
        return viewModel;
      },
      child: const _UserProfileContent(),
    );
  }
}

class _UserProfileContent extends StatelessWidget {
  const _UserProfileContent();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
      ),
      body: Consumer<UserProfileViewModel>(
        builder: (context, viewModel, child) {
          // Loading state
          if (viewModel.isLoading && viewModel.user == null) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          // Error state
          if (viewModel.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error, size: 64, color: Colors.red),
                  SizedBox(height: 16),
                  Text(viewModel.errorMessage!),
                  SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => viewModel.clearError(),
                    child: Text('Dismiss'),
                  ),
                ],
              ),
            );
          }

          // Success state
          final user = viewModel.user;
          if (user == null) {
            return const Center(child: Text('No user data'));
          }

          return RefreshIndicator(
            onRefresh: () => viewModel.loadUser(user.id),
            child: ListView(
              padding: EdgeInsets.all(16),
              children: [
                // Profile header
                Center(
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundImage: NetworkImage(user.avatarUrl),
                        child: Text(viewModel.initials),
                      ),
                      SizedBox(height: 16),
                      Text(
                        viewModel.displayName,
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                      SizedBox(height: 8),
                      Text(user.email),
                    ],
                  ),
                ),
                SizedBox(height: 32),

                // Action buttons
                ElevatedButton(
                  onPressed: () => _showEditDialog(context, viewModel),
                  child: Text('Edit Profile'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _showEditDialog(
    BuildContext context,
    UserProfileViewModel viewModel,
  ) async {
    final nameController = TextEditingController(text: viewModel.user?.name);
    final emailController = TextEditingController(text: viewModel.user?.email);

    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Edit Profile'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: InputDecoration(labelText: 'Name'),
            ),
            SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: InputDecoration(labelText: 'Email'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              viewModel.updateProfile(
                name: nameController.text,
                email: emailController.text,
              );
              Navigator.pop(context);
            },
            child: Text('Save'),
          ),
        ],
      ),
    );
  }
}
```

**View Best Practices:**
- Use Consumer for rebuilding on state changes
- Separate presentation widgets
- Handle all UI states (loading, error, success, empty)
- No business logic in views
- Extract complex UI into separate widgets

## ChangeNotifier Deep Dive

### 1. ChangeNotifier Basics

```dart
import 'package:flutter/foundation.dart';

class CounterViewModel extends ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void increment() {
    _count++;
    notifyListeners(); // Notify widgets to rebuild
  }

  void decrement() {
    _count--;
    notifyListeners();
  }

  void reset() {
    _count = 0;
    notifyListeners();
  }
}
```

**Key Methods:**
- `notifyListeners()` - Triggers rebuild of listening widgets
- `dispose()` - Clean up resources (always call super.dispose())
- `addListener(callback)` - Manually subscribe to changes (rarely needed)
- `removeListener(callback)` - Unsubscribe from changes

### 2. Optimizing notifyListeners Calls

```dart
// ❌ BAD: Unnecessary notifyListeners
class BadViewModel extends ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void increment() {
    notifyListeners(); // Before change!
    _count++;
    notifyListeners(); // After change (correct)
  }
}

// ✅ GOOD: Single notifyListeners after all changes
class GoodViewModel extends ChangeNotifier {
  int _count = 0;
  String _message = '';

  int get count => _count;
  String get message => _message;

  void incrementWithMessage() {
    _count++;
    _message = 'Count is now $_count';
    notifyListeners(); // Once, after all state updates
  }
}

// ✅ CONDITIONAL: Only notify if value changed
class OptimizedViewModel extends ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void setCount(int newCount) {
    if (_count != newCount) {
      _count = newCount;
      notifyListeners(); // Only if changed
    }
  }
}
```

### 3. Async Operations with ChangeNotifier

```dart
class DataViewModel extends ChangeNotifier {
  List<String> _items = [];
  bool _isLoading = false;
  String? _error;

  List<String> get items => List.unmodifiable(_items);
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await Future.delayed(Duration(seconds: 2)); // Simulate API call
      _items = ['Item 1', 'Item 2', 'Item 3'];
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
```

## Provider Integration

### 1. Providing ViewModels

**Single Provider:**

```dart
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => CounterViewModel(),
      child: MyApp(),
    ),
  );
}
```

**Multiple Providers:**

```dart
void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthViewModel()),
        ChangeNotifierProvider(create: (_) => ThemeViewModel()),
        ChangeNotifierProvider(create: (_) => SettingsViewModel()),

        // Services (non-ChangeNotifier)
        Provider(create: (_) => UserService()),
        Provider(create: (_) => ApiClient()),
      ],
      child: MyApp(),
    ),
  );
}
```

**Scoped Providers:**

```dart
class DetailScreen extends StatelessWidget {
  final String itemId;

  const DetailScreen({required this.itemId});

  @override
  Widget build(BuildContext context) {
    // Create ViewModel scoped to this screen
    return ChangeNotifierProvider(
      create: (context) {
        final apiService = context.read<ApiService>();
        final viewModel = ItemDetailViewModel(apiService);
        viewModel.loadItem(itemId);
        return viewModel;
      },
      child: _DetailScreenContent(),
    );
  }
}
```

### 2. Consuming State

**Consumer Widget:**

```dart
Consumer<CounterViewModel>(
  builder: (context, viewModel, child) {
    return Text('Count: ${viewModel.count}');
  },
)
```

**context.watch (inside build):**

```dart
@override
Widget build(BuildContext context) {
  final viewModel = context.watch<CounterViewModel>();
  return Text('Count: ${viewModel.count}');
}
```

**context.read (one-time access):**

```dart
// In event handlers, not build()
ElevatedButton(
  onPressed: () {
    context.read<CounterViewModel>().increment();
  },
  child: Text('Increment'),
)
```

**Selector (optimized partial rebuilds):**

```dart
// Only rebuilds when count changes, not other properties
Selector<CounterViewModel, int>(
  selector: (context, viewModel) => viewModel.count,
  builder: (context, count, child) {
    return Text('Count: $count');
  },
)
```

**Comparison:**

| Method | Use Case | Rebuilds |
|--------|----------|----------|
| `Consumer` | Small widget tree | On any state change |
| `context.watch()` | Entire widget | On any state change |
| `context.read()` | Event handlers | Never |
| `Selector` | Performance critical | On selected value change |

## Dependency Injection

### 1. Service Layer

```dart
// services/user_service.dart
class UserService {
  final ApiClient _apiClient;

  UserService(this._apiClient);

  Future<User> fetchUser(String id) async {
    final response = await _apiClient.get('/users/$id');
    return User.fromJson(response.data);
  }

  Future<void> updateUser(User user) async {
    await _apiClient.put('/users/${user.id}', data: user.toJson());
  }
}

// services/api_client.dart
class ApiClient {
  final String baseUrl;

  ApiClient(this.baseUrl);

  Future<Response> get(String path) async {
    // HTTP GET implementation
  }

  Future<Response> put(String path, {required Map<String, dynamic> data}) async {
    // HTTP PUT implementation
  }
}
```

### 2. Dependency Injection Setup

```dart
void main() {
  runApp(
    MultiProvider(
      providers: [
        // 1. Provide services (bottom of dependency tree)
        Provider(
          create: (_) => ApiClient('https://api.example.com'),
        ),

        // 2. Provide services that depend on other services
        ProxyProvider<ApiClient, UserService>(
          update: (context, apiClient, previous) => UserService(apiClient),
        ),

        // 3. Provide ViewModels that depend on services
        ChangeNotifierProxyProvider<UserService, UserListViewModel>(
          create: (context) => UserListViewModel(context.read<UserService>()),
          update: (context, userService, previous) {
            return previous ?? UserListViewModel(userService);
          },
        ),
      ],
      child: MyApp(),
    ),
  );
}
```

## Complete MVVM Example

### Project Structure

```
lib/
├── main.dart
├── models/
│   ├── user.dart
│   └── post.dart
├── services/
│   ├── api_client.dart
│   ├── user_service.dart
│   └── post_service.dart
├── viewmodels/
│   ├── user_list_viewmodel.dart
│   ├── user_detail_viewmodel.dart
│   └── post_viewmodel.dart
├── views/
│   ├── screens/
│   │   ├── user_list_screen.dart
│   │   └── user_detail_screen.dart
│   └── widgets/
│       ├── user_card.dart
│       └── loading_indicator.dart
└── app.dart
```

### Implementation

**main.dart:**

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_client.dart';
import 'services/user_service.dart';
import 'viewmodels/user_list_viewmodel.dart';
import 'app.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        Provider(create: (_) => ApiClient('https://api.example.com')),
        ProxyProvider<ApiClient, UserService>(
          update: (_, apiClient, __) => UserService(apiClient),
        ),
        ChangeNotifierProxyProvider<UserService, UserListViewModel>(
          create: (context) => UserListViewModel(context.read<UserService>()),
          update: (_, userService, previous) => previous ?? UserListViewModel(userService),
        ),
      ],
      child: MyApp(),
    ),
  );
}
```

**viewmodels/user_list_viewmodel.dart:**

```dart
import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/user_service.dart';

class UserListViewModel extends ChangeNotifier {
  final UserService _userService;

  UserListViewModel(this._userService) {
    loadUsers();
  }

  List<User> _users = [];
  bool _isLoading = false;
  String? _error;

  List<User> get users => _users;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasUsers => _users.isNotEmpty;

  Future<void> loadUsers() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _users = await _userService.fetchUsers();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load users: $e';
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deleteUser(String userId) async {
    try {
      await _userService.deleteUser(userId);
      _users.removeWhere((user) => user.id == userId);
      notifyListeners();
    } catch (e) {
      _error = 'Failed to delete user: $e';
      notifyListeners();
    }
  }
}
```

**views/screens/user_list_screen.dart:**

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../viewmodels/user_list_viewmodel.dart';
import '../widgets/user_card.dart';

class UserListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Users')),
      body: Consumer<UserListViewModel>(
        builder: (context, viewModel, child) {
          if (viewModel.isLoading && !viewModel.hasUsers) {
            return Center(child: CircularProgressIndicator());
          }

          if (viewModel.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(viewModel.error!),
                  ElevatedButton(
                    onPressed: viewModel.loadUsers,
                    child: Text('Retry'),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: viewModel.loadUsers,
            child: ListView.builder(
              itemCount: viewModel.users.length,
              itemBuilder: (context, index) {
                return UserCard(user: viewModel.users[index]);
              },
            ),
          );
        },
      ),
    );
  }
}
```

## Testing

### ViewModel Testing

```dart
// test/viewmodels/user_list_viewmodel_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:your_app/models/user.dart';
import 'package:your_app/services/user_service.dart';
import 'package:your_app/viewmodels/user_list_viewmodel.dart';

class MockUserService extends Mock implements UserService {}

void main() {
  late MockUserService mockUserService;
  late UserListViewModel viewModel;

  setUp(() {
    mockUserService = MockUserService();
    viewModel = UserListViewModel(mockUserService);
  });

  tearDown(() {
    viewModel.dispose();
  });

  test('Initial state is correct', () {
    expect(viewModel.users, isEmpty);
    expect(viewModel.isLoading, isFalse);
    expect(viewModel.error, isNull);
  });

  test('loadUsers sets loading state and fetches users', () async {
    final mockUsers = [
      User(id: '1', name: 'John', email: 'john@example.com', avatarUrl: ''),
      User(id: '2', name: 'Jane', email: 'jane@example.com', avatarUrl: ''),
    ];

    when(mockUserService.fetchUsers()).thenAnswer((_) async => mockUsers);

    final future = viewModel.loadUsers();

    expect(viewModel.isLoading, isTrue);

    await future;

    expect(viewModel.isLoading, isFalse);
    expect(viewModel.users, equals(mockUsers));
    expect(viewModel.error, isNull);
  });

  test('loadUsers handles errors', () async {
    when(mockUserService.fetchUsers()).thenThrow(Exception('Network error'));

    await viewModel.loadUsers();

    expect(viewModel.isLoading, isFalse);
    expect(viewModel.users, isEmpty);
    expect(viewModel.error, contains('Network error'));
  });
}
```

## Integration with Other Skills

This skill combines with:

- **flutter-widget-previewer** - Test ViewModels in isolation with mock data
- **material-design-3-flutter** - MVVM structure for Material 3 components
- **flutter-performance-optimization** - Optimize ChangeNotifier and Provider usage
- **flutter-asset-codegen** - Type-safe assets in ViewModels

## Additional Resources

- **Flutter App Architecture:** https://docs.flutter.dev/app-architecture/guide
- **State Management Guide:** https://docs.flutter.dev/get-started/fundamentals/state-management
- **Provider Package:** https://pub.dev/packages/provider
- **ChangeNotifier API:** https://api.flutter.dev/flutter/foundation/ChangeNotifier-class.html
- **MVVM Pattern:** https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel

MVVM with ChangeNotifier and Provider provides a proven, scalable architecture for Flutter applications of any size.
