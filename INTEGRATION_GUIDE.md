# 🚀 Apollo SDK Integration Guide

**Quick reference for integrating Apollo into Delt, Atlas, and Akashic**

---

## 📦 Step 1: Add Dependency

Add to your app's `pubspec.yaml`:

```yaml
dependencies:
  apollo_sdk:
    path: ../Apollo/sdk/flutter
```

Then run:
```bash
flutter pub get
```

---

## 📱 Step 2: Import

```dart
import 'package:apollo_sdk/apollo_sdk.dart';
```

---

## 🎯 Step 3: Choose Integration Method

### **Option A: Floating Bubble** (Recommended)

Perfect for adding Apollo to existing screens without major changes.

```dart
class YourScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Your existing content
          YourMainContent(),
          
          // Add Apollo bubble
          ApolloFloatingBubble(
            apiKey: 'your_api_key',
            userId: 'user_id',
            context: 'trading', // or 'knowledge', 'coding'
          ),
        ],
      ),
    );
  }
}
```

### **Option B: Full Screen Chat**

Perfect for dedicated Apollo screens.

```dart
class ApolloScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Apollo AI')),
      body: ApolloChatWidget(
        apiKey: 'your_api_key',
        userId: 'user_id',
        context: 'trading', // or 'knowledge', 'coding'
      ),
    );
  }
}
```

### **Option C: Direct API Calls**

Perfect for custom integrations.

```dart
final apollo = ApolloService(
  apiKey: 'your_api_key',
  userId: 'user_id',
);

// Chat
final response = await apollo.chat(
  message: 'What should I trade?',
  context: 'trading',
);

// Get recommendations
final recs = await apollo.getTradingRecommendations();

// Analyze sentiment
final sentiment = await apollo.analyzeSentiment(symbol: 'BTC/USD');
```

---

## 🎨 Step 4: Customize (Optional)

### **Custom Colors**

```dart
ApolloFloatingBubble(
  apiKey: apiKey,
  userId: userId,
  context: 'trading',
  primaryColor: Color(0xFF6366F1), // Your brand color
)
```

### **Custom Position**

```dart
ApolloFloatingBubble(
  apiKey: apiKey,
  userId: userId,
  context: 'trading',
  alignment: Alignment.topLeft, // Top left corner
  padding: EdgeInsets.all(24), // More padding
)
```

### **Event Callbacks**

```dart
ApolloChatWidget(
  apiKey: apiKey,
  userId: userId,
  context: 'trading',
  onMessageSent: (message) {
    print('User sent: $message');
    // Track analytics
  },
  onResponseReceived: (response) {
    print('Apollo responded: $response');
    // Track analytics
  },
)
```

---

## 📋 Step 5: Add Quick Actions (Optional)

```dart
Column(
  children: [
    ApolloQuickActions(
      actions: ApolloQuickActionsPresets.trading,
      onActionTap: (action) {
        // Open Apollo with pre-filled prompt
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ApolloScreen(
              initialMessage: action.prompt,
            ),
          ),
        );
      },
    ),
    YourMainContent(),
  ],
)
```

---

## 🔧 Context-Specific Examples

### **Delt (Trading)**

```dart
// In trading screen
Stack(
  children: [
    TradingChart(),
    OrderPanel(),
    ApolloFloatingBubble(
      apiKey: apiKey,
      userId: userId,
      context: 'trading', // Trading context
      primaryColor: DeltColors.primary,
    ),
  ],
)

// Quick actions in order panel
ApolloQuickActions(
  actions: ApolloQuickActionsPresets.trading,
  primaryColor: DeltColors.primary,
  onActionTap: (action) {
    // Handle action
  },
)
```

### **Atlas (Knowledge)**

```dart
// In document viewer
Stack(
  children: [
    DocumentViewer(),
    ApolloFloatingBubble(
      apiKey: apiKey,
      userId: userId,
      context: 'knowledge', // Knowledge context
      primaryColor: AtlasColors.primary,
    ),
  ],
)

// Quick actions for document
ApolloQuickActions(
  actions: ApolloQuickActionsPresets.knowledge,
  primaryColor: AtlasColors.primary,
  onActionTap: (action) {
    // Handle action
  },
)
```

### **Akashic (Coding)**

```dart
// In code editor
Stack(
  children: [
    CodeEditor(),
    ApolloFloatingBubble(
      apiKey: apiKey,
      userId: userId,
      context: 'coding', // Coding context
      primaryColor: AkashicColors.primary,
    ),
  ],
)

// Quick actions for code
ApolloQuickActions(
  actions: ApolloQuickActionsPresets.coding,
  primaryColor: AkashicColors.primary,
  onActionTap: (action) {
    // Handle action
  },
)
```

---

## 🔐 API Key Management

### **Development**

```dart
const apolloApiKey = 'apollo_dev_xxxxxxxxxxxxx';
```

### **Production**

```dart
// Load from environment or secure storage
final apolloApiKey = await SecureStorage.read('apollo_api_key');
```

### **Per-User Keys**

```dart
// Get user-specific key from backend
final apolloApiKey = await api.getApolloKey(userId);
```

---

## 📊 Analytics Integration

```dart
ApolloChatWidget(
  apiKey: apiKey,
  userId: userId,
  context: 'trading',
  onMessageSent: (message) {
    // Track with your analytics
    Analytics.track('apollo_message_sent', {
      'context': 'trading',
      'message_length': message.length,
    });
  },
  onResponseReceived: (response) {
    Analytics.track('apollo_response_received', {
      'context': 'trading',
      'response_length': response.length,
    });
  },
)
```

---

## 🧪 Testing

### **Mock Apollo Service**

```dart
class MockApolloService extends ApolloService {
  @override
  Future<String> chat({
    required String message,
    required String context,
    List<Map<String, String>>? conversationHistory,
  }) async {
    // Return mock response
    return 'Mock response for: $message';
  }
}

// Use in tests
final mockApollo = MockApolloService(
  apiKey: 'test_key',
  userId: 'test_user',
);
```

---

## 🚨 Error Handling

```dart
try {
  final response = await apollo.chat(
    message: 'What should I trade?',
    context: 'trading',
  );
  print(response);
} catch (e) {
  // Handle error
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: Text('Apollo Error'),
      content: Text('Failed to get response: $e'),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text('OK'),
        ),
      ],
    ),
  );
}
```

---

## 🎯 Best Practices

### **1. Context Selection**
- Use `'trading'` for Delt (market analysis, recommendations)
- Use `'knowledge'` for Atlas (document analysis, insights)
- Use `'coding'` for Akashic (code generation, debugging)

### **2. User Experience**
- Show loading indicators during API calls
- Handle errors gracefully
- Provide quick actions for common tasks
- Use floating bubble for non-intrusive access

### **3. Performance**
- Debounce rapid messages
- Cache responses when appropriate
- Lazy load Apollo components
- Use const constructors where possible

### **4. Security**
- Never hardcode API keys
- Use secure storage for keys
- Validate user input
- Implement rate limiting

---

## 📈 Monitoring

Track these metrics:
- Messages sent per user
- Response times
- Error rates
- Most common queries
- User satisfaction (thumbs up/down)

---

## 🔄 Updates

To update Apollo SDK:

```bash
cd Apollo/sdk/flutter
git pull origin main
cd ../../../YourApp
flutter pub get
```

---

## 📞 Support

- **Docs:** `Apollo/sdk/flutter/README.md`
- **Examples:** `Apollo/INTEGRATION_GUIDE.md`
- **Issues:** GitHub Issues
- **Email:** support@colossalcapital.io

---

## ✅ Integration Checklist

- [ ] Add dependency to pubspec.yaml
- [ ] Run `flutter pub get`
- [ ] Import Apollo SDK
- [ ] Choose integration method
- [ ] Add API key
- [ ] Set correct context
- [ ] Customize colors (optional)
- [ ] Add quick actions (optional)
- [ ] Test in development
- [ ] Add analytics
- [ ] Handle errors
- [ ] Deploy to production

---

**That's it! Apollo is ready to use in your app.** 🚀

Total integration time: **~15 minutes**
