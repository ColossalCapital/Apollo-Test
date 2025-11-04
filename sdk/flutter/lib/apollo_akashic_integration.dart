import 'dart:convert';
import 'package:http/http.dart' as http;

/// Apollo-Akashic Integration Service
/// 
/// Allows Apollo to query Akashic's data infrastructure:
/// - Materialize streaming SQL
/// - QuestDB historical data
/// - Ray/Smelt ML models
/// - Filecoin storage
/// 
/// Example:
/// ```dart
/// User: "Apollo, how much BTC/USD data is flowing from Coinbase?"
/// Apollo → Ollama → Materialize SQL → Response
/// ```
class ApolloAkashicIntegration {
  final String apiKey;
  final String userId;
  final String baseUrl;

  ApolloAkashicIntegration({
    required this.apiKey,
    required this.userId,
    this.baseUrl = 'https://apollo.colossalcapital.io/api',
  });

  /// Query Akashic data using natural language
  /// Apollo converts NL → SQL using Ollama, then queries Materialize
  Future<AkashicQueryResult> queryData({
    required String naturalLanguageQuery,
    String? context, // 'streaming', 'historical', 'ml'
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/akashic/query'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'query': naturalLanguageQuery,
          'context': context,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return AkashicQueryResult.fromJson(data);
      } else {
        throw Exception('Failed to query Akashic data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to query Akashic data: $e');
    }
  }

  /// Get streaming metrics for a specific market
  Future<StreamingDataMetrics> getStreamingMetrics({
    required String market, // e.g., 'BTC/USD', 'ETH/USD'
    String? exchange, // e.g., 'coinbase', 'binance'
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/akashic/streaming/metrics'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'market': market,
          'exchange': exchange,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return StreamingDataMetrics.fromJson(data);
      } else {
        throw Exception('Failed to get streaming metrics: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get streaming metrics: $e');
    }
  }

  /// Get aggregate metrics across all streaming sources
  Future<AggregateMetrics> getAggregateMetrics() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/akashic/streaming/aggregate'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return AggregateMetrics.fromJson(data);
      } else {
        throw Exception('Failed to get aggregate metrics: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get aggregate metrics: $e');
    }
  }

  /// Query historical data using natural language
  Future<HistoricalQueryResult> queryHistoricalData({
    required String naturalLanguageQuery,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/akashic/historical/query'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'query': naturalLanguageQuery,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return HistoricalQueryResult.fromJson(data);
      } else {
        throw Exception('Failed to query historical data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to query historical data: $e');
    }
  }

  /// Get ML model insights
  Future<MLInsights> getMLInsights({
    required String deploymentId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/akashic/ml/insights/$deploymentId'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return MLInsights.fromJson(data);
      } else {
        throw Exception('Failed to get ML insights: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get ML insights: $e');
    }
  }

  /// Search strategies on Filecoin/IPFS
  Future<List<StrategySearchResult>> searchStrategies({
    required String query,
    List<String>? tags,
    String? language,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/akashic/storage/search'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
        body: jsonEncode({
          'query': query,
          'tags': tags,
          'language': language,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return (data['results'] as List)
            .map((r) => StrategySearchResult.fromJson(r))
            .toList();
      } else {
        throw Exception('Failed to search strategies: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to search strategies: $e');
    }
  }

  /// Get data pipeline status
  Future<DataPipelineStatus> getDataPipelineStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/akashic/pipeline/status'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'X-User-ID': userId,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return DataPipelineStatus.fromJson(data);
      } else {
        throw Exception('Failed to get pipeline status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get pipeline status: $e');
    }
  }
}

// ============================================================================
// DATA MODELS
// ============================================================================

class AkashicQueryResult {
  final String naturalLanguageQuery;
  final String generatedSQL;
  final List<Map<String, dynamic>> results;
  final String summary; // Natural language summary of results
  final Map<String, dynamic> metadata;

  AkashicQueryResult({
    required this.naturalLanguageQuery,
    required this.generatedSQL,
    required this.results,
    required this.summary,
    required this.metadata,
  });

  factory AkashicQueryResult.fromJson(Map<String, dynamic> json) {
    return AkashicQueryResult(
      naturalLanguageQuery: json['natural_language_query'],
      generatedSQL: json['generated_sql'],
      results: List<Map<String, dynamic>>.from(json['results']),
      summary: json['summary'],
      metadata: Map<String, dynamic>.from(json['metadata']),
    );
  }
}

class StreamingDataMetrics {
  final String market;
  final String? exchange;
  final int messageRate; // messages per second
  final double currentPrice;
  final double volatility1m; // 1-minute volatility
  final double volatility5m; // 5-minute volatility
  final double volume1m; // 1-minute volume
  final int totalMessages;
  final DateTime timestamp;
  final String summary; // Natural language summary

  StreamingDataMetrics({
    required this.market,
    this.exchange,
    required this.messageRate,
    required this.currentPrice,
    required this.volatility1m,
    required this.volatility5m,
    required this.volume1m,
    required this.totalMessages,
    required this.timestamp,
    required this.summary,
  });

  factory StreamingDataMetrics.fromJson(Map<String, dynamic> json) {
    return StreamingDataMetrics(
      market: json['market'],
      exchange: json['exchange'],
      messageRate: json['message_rate'],
      currentPrice: json['current_price'].toDouble(),
      volatility1m: json['volatility_1m'].toDouble(),
      volatility5m: json['volatility_5m'].toDouble(),
      volume1m: json['volume_1m'].toDouble(),
      totalMessages: json['total_messages'],
      timestamp: DateTime.parse(json['timestamp']),
      summary: json['summary'],
    );
  }
}

class AggregateMetrics {
  final int totalStreams;
  final int totalMessageRate; // total messages/sec across all streams
  final Map<String, int> streamsByExchange;
  final Map<String, int> streamsByMarket;
  final double totalDataThroughputMBps;
  final DateTime timestamp;

  AggregateMetrics({
    required this.totalStreams,
    required this.totalMessageRate,
    required this.streamsByExchange,
    required this.streamsByMarket,
    required this.totalDataThroughputMBps,
    required this.timestamp,
  });

  factory AggregateMetrics.fromJson(Map<String, dynamic> json) {
    return AggregateMetrics(
      totalStreams: json['total_streams'],
      totalMessageRate: json['total_message_rate'],
      streamsByExchange: Map<String, int>.from(json['streams_by_exchange']),
      streamsByMarket: Map<String, int>.from(json['streams_by_market']),
      totalDataThroughputMBps: json['total_data_throughput_mbps'].toDouble(),
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}

class HistoricalQueryResult {
  final String naturalLanguageQuery;
  final String generatedSQL;
  final List<Map<String, dynamic>> data;
  final String summary;
  final Map<String, dynamic> statistics;

  HistoricalQueryResult({
    required this.naturalLanguageQuery,
    required this.generatedSQL,
    required this.data,
    required this.summary,
    required this.statistics,
  });

  factory HistoricalQueryResult.fromJson(Map<String, dynamic> json) {
    return HistoricalQueryResult(
      naturalLanguageQuery: json['natural_language_query'],
      generatedSQL: json['generated_sql'],
      data: List<Map<String, dynamic>>.from(json['data']),
      summary: json['summary'],
      statistics: Map<String, dynamic>.from(json['statistics']),
    );
  }
}

class MLInsights {
  final String deploymentId;
  final String modelType;
  final double accuracy;
  final Map<String, double> featureImportance;
  final List<String> recentPredictions;
  final String performanceSummary;
  final Map<String, dynamic> metrics;

  MLInsights({
    required this.deploymentId,
    required this.modelType,
    required this.accuracy,
    required this.featureImportance,
    required this.recentPredictions,
    required this.performanceSummary,
    required this.metrics,
  });

  factory MLInsights.fromJson(Map<String, dynamic> json) {
    return MLInsights(
      deploymentId: json['deployment_id'],
      modelType: json['model_type'],
      accuracy: json['accuracy'].toDouble(),
      featureImportance: Map<String, double>.from(json['feature_importance']),
      recentPredictions: List<String>.from(json['recent_predictions']),
      performanceSummary: json['performance_summary'],
      metrics: Map<String, dynamic>.from(json['metrics']),
    );
  }
}

class StrategySearchResult {
  final String cid;
  final String name;
  final String description;
  final String language;
  final List<String> tags;
  final String author;
  final double rating;
  final int downloads;
  final DateTime createdAt;

  StrategySearchResult({
    required this.cid,
    required this.name,
    required this.description,
    required this.language,
    required this.tags,
    required this.author,
    required this.rating,
    required this.downloads,
    required this.createdAt,
  });

  factory StrategySearchResult.fromJson(Map<String, dynamic> json) {
    return StrategySearchResult(
      cid: json['cid'],
      name: json['name'],
      description: json['description'],
      language: json['language'],
      tags: List<String>.from(json['tags']),
      author: json['author'],
      rating: json['rating'].toDouble(),
      downloads: json['downloads'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class DataPipelineStatus {
  final String status; // 'healthy', 'degraded', 'down'
  final Map<String, SourceStatus> sources;
  final int totalEventsProcessed;
  final double avgLatencyMs;
  final DateTime lastUpdated;

  DataPipelineStatus({
    required this.status,
    required this.sources,
    required this.totalEventsProcessed,
    required this.avgLatencyMs,
    required this.lastUpdated,
  });

  factory DataPipelineStatus.fromJson(Map<String, dynamic> json) {
    return DataPipelineStatus(
      status: json['status'],
      sources: (json['sources'] as Map<String, dynamic>)
          .map((k, v) => MapEntry(k, SourceStatus.fromJson(v))),
      totalEventsProcessed: json['total_events_processed'],
      avgLatencyMs: json['avg_latency_ms'].toDouble(),
      lastUpdated: DateTime.parse(json['last_updated']),
    );
  }
}

class SourceStatus {
  final String name;
  final String status;
  final int eventsPerSecond;
  final double latencyMs;
  final DateTime lastEvent;

  SourceStatus({
    required this.name,
    required this.status,
    required this.eventsPerSecond,
    required this.latencyMs,
    required this.lastEvent,
  });

  factory SourceStatus.fromJson(Map<String, dynamic> json) {
    return SourceStatus(
      name: json['name'],
      status: json['status'],
      eventsPerSecond: json['events_per_second'],
      latencyMs: json['latency_ms'].toDouble(),
      lastEvent: DateTime.parse(json['last_event']),
    );
  }
}
