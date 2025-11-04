/// Apollo AI SDK for Flutter
/// 
/// Intelligent AI assistant with Akashic data integration.
/// 
/// Apollo is your personal AI assistant that adapts to different contexts:
/// - Trading (Delt) - Market analysis, recommendations, auto-trading
/// - Knowledge (Atlas) - Document analysis, insights, Q&A
/// - Coding (Akashic) - Code generation, debugging, optimization
/// 
/// **NEW: Akashic Integration**
/// Apollo can now query Akashic's data infrastructure:
/// - Materialize streaming SQL
/// - QuestDB historical data
/// - Ray/Smelt ML models
/// - Filecoin storage
/// 
/// ## Quick Start
/// 
/// ```dart
/// import 'package:apollo_sdk/apollo_sdk.dart';
/// 
/// // Chat widget
/// ApolloChatWidget(
///   apiKey: 'your_api_key',
///   userId: 'user_id',
///   context: 'trading',
/// )
/// 
/// // Query Akashic data
/// final akashicIntegration = ApolloAkashicIntegration(
///   apiKey: 'your_api_key',
///   userId: 'user_id',
/// );
/// 
/// // Natural language query
/// final result = await akashicIntegration.queryData(
///   naturalLanguageQuery: 'How much BTC/USD data is flowing from Coinbase?',
/// );
/// print(result.summary);
/// 
/// // Get streaming metrics
/// final metrics = await akashicIntegration.getStreamingMetrics(
///   market: 'BTC/USD',
///   exchange: 'coinbase',
/// );
/// print('Message rate: ${metrics.messageRate}/sec');
/// print('Current price: \$${metrics.currentPrice}');
/// ```
library apollo_sdk;

// Core components
export 'apollo_chat_widget.dart';
export 'apollo_service.dart';
export 'apollo_floating_bubble.dart';
export 'apollo_akashic_integration.dart';
