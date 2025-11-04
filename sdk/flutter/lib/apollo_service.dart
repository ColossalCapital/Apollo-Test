import 'dart:convert';
import 'package:http/http.dart' as http;

/// Apollo AI Service - Core API client
/// Handles all communication with Apollo backend
class ApolloService {
  final String apiKey;
  final String userId;
  final String baseUrl;

  ApolloService({
    required this.apiKey,
    required this.userId,
    this.baseUrl = 'https://apollo.colossalcapital.io/api',
  });

  /// Send chat message to Apollo
  Future<String> chat({
    required String message,
    required String context,
    List<Map<String, String>>? conversationHistory,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'message': message,
          'context': context,
          'conversation_history': conversationHistory ?? [],
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['response'] as String;
      } else {
        throw Exception('Apollo API error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to communicate with Apollo: $e');
    }
  }

  /// Get trading recommendations
  Future<List<TradingRecommendation>> getTradingRecommendations({
    String? symbol,
    String? timeframe,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (symbol != null) queryParams['symbol'] = symbol;
      if (timeframe != null) queryParams['timeframe'] = timeframe;

      final uri = Uri.parse('$baseUrl/recommendations').replace(
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List;
        return data.map((item) => TradingRecommendation.fromJson(item)).toList();
      } else {
        throw Exception('Failed to get recommendations');
      }
    } catch (e) {
      throw Exception('Failed to get recommendations: $e');
    }
  }

  /// Analyze market sentiment
  Future<MarketSentiment> analyzeSentiment({
    required String symbol,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/sentiment'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({'symbol': symbol}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return MarketSentiment.fromJson(data);
      } else {
        throw Exception('Failed to analyze sentiment');
      }
    } catch (e) {
      throw Exception('Failed to analyze sentiment: $e');
    }
  }

  /// Generate trading strategy
  Future<TradingStrategy> generateStrategy({
    required String description,
    String? riskLevel,
    double? capitalAllocation,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/strategy/generate'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'description': description,
          'risk_level': riskLevel ?? 'medium',
          'capital_allocation': capitalAllocation ?? 10000.0,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return TradingStrategy.fromJson(data);
      } else {
        throw Exception('Failed to generate strategy');
      }
    } catch (e) {
      throw Exception('Failed to generate strategy: $e');
    }
  }

  /// Optimize portfolio
  Future<PortfolioOptimization> optimizePortfolio({
    required List<Map<String, dynamic>> holdings,
    String? objective,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/portfolio/optimize'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'holdings': holdings,
          'objective': objective ?? 'maximize_sharpe',
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return PortfolioOptimization.fromJson(data);
      } else {
        throw Exception('Failed to optimize portfolio');
      }
    } catch (e) {
      throw Exception('Failed to optimize portfolio: $e');
    }
  }

  /// Execute auto-trading
  Future<AutoTradeResult> executeAutoTrade({
    required String strategyId,
    required double amount,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auto-trade/execute'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'strategy_id': strategyId,
          'amount': amount,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return AutoTradeResult.fromJson(data);
      } else {
        throw Exception('Failed to execute auto-trade');
      }
    } catch (e) {
      throw Exception('Failed to execute auto-trade: $e');
    }
  }
}

// Data models

class TradingRecommendation {
  final String symbol;
  final String action; // buy, sell, hold
  final double confidence;
  final String reasoning;
  final double? targetPrice;
  final double? stopLoss;

  TradingRecommendation({
    required this.symbol,
    required this.action,
    required this.confidence,
    required this.reasoning,
    this.targetPrice,
    this.stopLoss,
  });

  factory TradingRecommendation.fromJson(Map<String, dynamic> json) {
    return TradingRecommendation(
      symbol: json['symbol'],
      action: json['action'],
      confidence: json['confidence'].toDouble(),
      reasoning: json['reasoning'],
      targetPrice: json['target_price']?.toDouble(),
      stopLoss: json['stop_loss']?.toDouble(),
    );
  }
}

class MarketSentiment {
  final String symbol;
  final String sentiment; // bullish, bearish, neutral
  final double score; // -1 to 1
  final Map<String, double> indicators;

  MarketSentiment({
    required this.symbol,
    required this.sentiment,
    required this.score,
    required this.indicators,
  });

  factory MarketSentiment.fromJson(Map<String, dynamic> json) {
    return MarketSentiment(
      symbol: json['symbol'],
      sentiment: json['sentiment'],
      score: json['score'].toDouble(),
      indicators: Map<String, double>.from(json['indicators']),
    );
  }
}

class TradingStrategy {
  final String id;
  final String name;
  final String description;
  final String code;
  final Map<String, dynamic> parameters;
  final double expectedReturn;
  final double riskScore;

  TradingStrategy({
    required this.id,
    required this.name,
    required this.description,
    required this.code,
    required this.parameters,
    required this.expectedReturn,
    required this.riskScore,
  });

  factory TradingStrategy.fromJson(Map<String, dynamic> json) {
    return TradingStrategy(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      code: json['code'],
      parameters: json['parameters'],
      expectedReturn: json['expected_return'].toDouble(),
      riskScore: json['risk_score'].toDouble(),
    );
  }
}

class PortfolioOptimization {
  final Map<String, double> suggestedAllocations;
  final double expectedReturn;
  final double expectedRisk;
  final double sharpeRatio;
  final List<String> recommendations;

  PortfolioOptimization({
    required this.suggestedAllocations,
    required this.expectedReturn,
    required this.expectedRisk,
    required this.sharpeRatio,
    required this.recommendations,
  });

  factory PortfolioOptimization.fromJson(Map<String, dynamic> json) {
    return PortfolioOptimization(
      suggestedAllocations: Map<String, double>.from(json['suggested_allocations']),
      expectedReturn: json['expected_return'].toDouble(),
      expectedRisk: json['expected_risk'].toDouble(),
      sharpeRatio: json['sharpe_ratio'].toDouble(),
      recommendations: List<String>.from(json['recommendations']),
    );
  }
}

class AutoTradeResult {
  final String tradeId;
  final String status;
  final String symbol;
  final double amount;
  final double executionPrice;
  final DateTime timestamp;

  AutoTradeResult({
    required this.tradeId,
    required this.status,
    required this.symbol,
    required this.amount,
    required this.executionPrice,
    required this.timestamp,
  });

  factory AutoTradeResult.fromJson(Map<String, dynamic> json) {
    return AutoTradeResult(
      tradeId: json['trade_id'],
      status: json['status'],
      symbol: json['symbol'],
      amount: json['amount'].toDouble(),
      executionPrice: json['execution_price'].toDouble(),
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}
