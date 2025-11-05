# Apollo SDK for Flutter

**Reusable AI chat widget and service for Delt, Atlas, and Akashic**

Apollo is your personal AI assistant that adapts to different contexts:
- **Trading** (Delt) - Market analysis, recommendations, auto-trading
- **Knowledge** (Atlas) - Document analysis, insights, Q&A
- **Coding** (Akashic) - Code generation, debugging, optimization

---

## 🚀 Quick Start

### Installation

Add to your `pubspec.yaml`:

```yaml
dependencies:
  apollo_sdk:
    path: ../Apollo/sdk/flutter
```

Or from pub.dev (when published):

```yaml
dependencies:
  apollo_sdk: ^1.0.0
```

### Basic Usage

```dart
import 'package:apollo_sdk/apollo_chat_widget.dart';

// Full-screen chat
ApolloChatWidget(
  apiKey: 'your_api_key',
  userId: 'user_id',
  context: 'trading', // or 'knowledge', 'coding'
)

// Floating bubble
ApolloFloatingBubble(
  apiKey: 'your_api_key',
  userId: 'user_id',
  context: 'trading',
  alignment: Alignment.bottomRight,
)
```

---

## 📦 Components

### 1. ApolloChatWidget

Full-featured chat interface with message history, typing indicators, and error handling.

```dart
ApolloChatWidget(
  apiKey: 'your_api_key',
  userId: 'user_id',
  context: 'trading',
  primaryColor: Colors.blue,
  backgroundColor: Color(0xFF0F172A),
  onMessageSent: (message) {
    print('User sent: $message');
  },
  onResponseReceived: (response) {
    print('Apollo responded: $response');
  },
)
```

**Parameters:**
- `apiKey` (required) - Your Apollo API key
- `userId` (required) - Current user ID
- `context` (required) - 'trading', 'knowledge', or 'coding'
- `primaryColor` (optional) - Theme color
- `backgroundColor` (optional) - Background color
- `onMessageSent` (optional) - Callback when user sends message
- `onResponseReceived` (optional) - Callback when Apollo responds

---

### 2. ApolloFloatingBubble

Floating bubble that expands into chat when tapped.

```dart
Stack(
  children: [
    YourMainContent(),
    ApolloFloatingBubble(
      apiKey: 'your_api_key',
      userId: 'user_id',
      context: 'trading',
      alignment: Alignment.bottomRight,
      padding: EdgeInsets.all(16),
    ),
  ],
)
```

**Parameters:**
- `apiKey` (required) - Your Apollo API key
- `userId` (required) - Current user ID
- `context` (required) - 'trading', 'knowledge', or 'coding'
- `primaryColor` (optional) - Theme color
- `alignment` (optional) - Bubble position (default: bottomRight)
- `padding` (optional) - Padding around bubble

---

### 3. ApolloService

Direct API client for custom integrations.

```dart
import 'package:apollo_sdk/apollo_service.dart';

final apollo = ApolloService(
  apiKey: 'your_api_key',
  userId: 'user_id',
);

// Chat
final response = await apollo.chat(
  message: 'What should I trade today?',
  context: 'trading',
);

// Get trading recommendations
final recommendations = await apollo.getTradingRecommendations(
  symbol: 'BTC/USD',
  timeframe: '1h',
);

// Analyze sentiment
final sentiment = await apollo.analyzeSentiment(
  symbol: 'BTC/USD',
);

// Generate strategy
final strategy = await apollo.generateStrategy(
  description: 'Momentum trading with RSI',
  riskLevel: 'medium',
  capitalAllocation: 10000.0,
);

// Optimize portfolio
final optimization = await apollo.optimizePortfolio(
  holdings: [
    {'symbol': 'BTC', 'amount': 0.5},
    {'symbol': 'ETH', 'amount': 2.0},
  ],
  objective: 'maximize_sharpe',
);

// Execute auto-trade
final result = await apollo.executeAutoTrade(
  strategyId: 'strategy_123',
  amount: 1000.0,
);
```

---

### 4. ApolloQuickActions

Pre-defined quick action buttons for common tasks.

```dart
import 'package:apollo_sdk/apollo_floating_bubble.dart';

ApolloQuickActions(
  actions: ApolloQuickActionsPresets.trading,
  onActionTap: (action) {
    // Send action.prompt to Apollo
    print('Quick action: ${action.prompt}');
  },
)
```

**Presets:**
- `ApolloQuickActionsPresets.trading` - Trading actions
- `ApolloQuickActionsPresets.knowledge` - Knowledge actions
- `ApolloQuickActionsPresets.coding` - Coding actions

---

## 🎨 Customization

### Custom Colors

```dart
ApolloChatWidget(
  apiKey: 'your_api_key',
  userId: 'user_id',
  context: 'trading',
  primaryColor: Color(0xFF6366F1), // Indigo
  backgroundColor: Color(0xFF0F172A), // Dark blue
)
```

### Custom Quick Actions

```dart
final customActions = [
  QuickAction(
    label: 'My Action',
    icon: Icons.star,
    prompt: 'Custom prompt for Apollo',
  ),
];

ApolloQuickActions(
  actions: customActions,
  onActionTap: (action) {
    // Handle action
  },
)
```

---

## 🔧 API Reference

### ApolloService Methods

#### `chat()`
Send chat message to Apollo.

**Parameters:**
- `message` (String) - User message
- `context` (String) - Context ('trading', 'knowledge', 'coding')
- `conversationHistory` (List<Map<String, String>>?) - Previous messages

**Returns:** `Future<String>` - Apollo's response

---

#### `getTradingRecommendations()`
Get AI-powered trading recommendations.

**Parameters:**
- `symbol` (String?) - Asset symbol (optional)
- `timeframe` (String?) - Timeframe (optional)

**Returns:** `Future<List<TradingRecommendation>>`

---

#### `analyzeSentiment()`
Analyze market sentiment for a symbol.

**Parameters:**
- `symbol` (String) - Asset symbol

**Returns:** `Future<MarketSentiment>`

---

#### `generateStrategy()`
Generate trading strategy from description.

**Parameters:**
- `description` (String) - Strategy description
- `riskLevel` (String?) - 'low', 'medium', 'high'
- `capitalAllocation` (double?) - Capital to allocate

**Returns:** `Future<TradingStrategy>`

---

#### `optimizePortfolio()`
Optimize portfolio allocation.

**Parameters:**
- `holdings` (List<Map<String, dynamic>>) - Current holdings
- `objective` (String?) - Optimization objective

**Returns:** `Future<PortfolioOptimization>`

---

#### `executeAutoTrade()`
Execute auto-trading strategy.

**Parameters:**
- `strategyId` (String) - Strategy ID
- `amount` (double) - Trade amount

**Returns:** `Future<AutoTradeResult>`

---

## 📱 Integration Examples

### Delt (Trading App)

```dart
// In your trading screen
Stack(
  children: [
    TradingChart(),
    ApolloFloatingBubble(
      apiKey: apiKey,
      userId: userId,
      context: 'trading',
    ),
  ],
)

// Quick actions in order panel
ApolloQuickActions(
  actions: ApolloQuickActionsPresets.trading,
  onActionTap: (action) {
    // Open chat with pre-filled prompt
  },
)
```

### Atlas (Knowledge Management)

```dart
// In your document viewer
Stack(
  children: [
    DocumentViewer(),
    ApolloFloatingBubble(
      apiKey: apiKey,
      userId: userId,
      context: 'knowledge',
    ),
  ],
)

// Quick actions for document analysis
ApolloQuickActions(
  actions: ApolloQuickActionsPresets.knowledge,
  onActionTap: (action) {
    // Analyze document with Apollo
  },
)
```

### Akashic (Code Editor)

```dart
// In your code editor
Stack(
  children: [
    CodeEditor(),
    ApolloFloatingBubble(
      apiKey: apiKey,
      userId: userId,
      context: 'coding',
    ),
  ],
)

// Quick actions for code assistance
ApolloQuickActions(
  actions: ApolloQuickActionsPresets.coding,
  onActionTap: (action) {
    // Get coding help from Apollo
  },
)
```

---

## 🔐 Authentication

Apollo uses API keys for authentication. Get your API key from the Apollo dashboard:

```dart
final apollo = ApolloService(
  apiKey: 'apollo_key_xxxxxxxxxxxxx',
  userId: 'user_123',
);
```

---

## 🌐 API Endpoints

Default base URL: `https://apollo.colossalcapital.io/api`

Custom base URL:

```dart
final apollo = ApolloService(
  apiKey: 'your_api_key',
  userId: 'user_id',
  baseUrl: 'https://your-custom-domain.com/api',
);
```

---

## 📊 Data Models

### TradingRecommendation
```dart
class TradingRecommendation {
  final String symbol;
  final String action; // buy, sell, hold
  final double confidence;
  final String reasoning;
  final double? targetPrice;
  final double? stopLoss;
}
```

### MarketSentiment
```dart
class MarketSentiment {
  final String symbol;
  final String sentiment; // bullish, bearish, neutral
  final double score; // -1 to 1
  final Map<String, double> indicators;
}
```

### TradingStrategy
```dart
class TradingStrategy {
  final String id;
  final String name;
  final String description;
  final String code;
  final Map<String, dynamic> parameters;
  final double expectedReturn;
  final double riskScore;
}
```

---

## 🎯 Best Practices

1. **Context-Specific Prompts** - Use appropriate context for each app
2. **Error Handling** - Always wrap API calls in try-catch
3. **User Feedback** - Show loading states during API calls
4. **Rate Limiting** - Implement debouncing for rapid messages
5. **Conversation History** - Pass history for better context

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

---

## 📞 Support

- **Email:** support@colossalcapital.io
- **Discord:** https://discord.gg/colossalcapital
- **Docs:** https://docs.apollo.colossalcapital.io

---

**Built with ❤️ by Colossal Capital**
