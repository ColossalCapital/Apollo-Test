/// Apollo SDK for Dart/Flutter
/// 
/// Simplified SDK for Delt mobile app
/// Only chat functionality - no complex IDE features

library apollo_sdk;

import 'dart:convert';
import 'package:http/http.dart' as http;

export 'src/apollo_client.dart';
export 'src/models.dart';

/// Simple Apollo client for mobile apps
class ApolloClient {
  final String apiUrl;
  final String authToken;
  
  ApolloClient({
    required this.apiUrl,
    required this.authToken,
  });
  
  /// Send a chat message to Apollo
  /// Conductor will select optimal model automatically
  Future<ChatResponse> chat(String message, {String? context}) async {
    final response = await http.post(
      Uri.parse('$apiUrl/api/v1/inference/chat'),
      headers: {
        'Authorization': 'Bearer $authToken',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'message': message,
        'context': context ?? 'delt',
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return ChatResponse.fromJson(data);
    } else {
      throw Exception('Apollo chat failed: ${response.body}');
    }
  }
  
  /// Get recommended data subscriptions based on user's needs
  /// Conductor analyzes usage patterns
  Future<List<DataStream>> getRecommendedDataStreams() async {
    final response = await http.get(
      Uri.parse('$apiUrl/api/v1/conductor/recommend-data'),
      headers: {'Authorization': 'Bearer $authToken'},
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['recommendations'] as List)
          .map((d) => DataStream.fromJson(d))
          .toList();
    }
    
    return [];
  }
  
  /// Get Conductor status (what's running)
  Future<ConductorStatus> getStatus() async {
    final response = await http.get(
      Uri.parse('$apiUrl/api/v1/conductor/status'),
      headers: {'Authorization': 'Bearer $authToken'},
    );
    
    if (response.statusCode == 200) {
      return ConductorStatus.fromJson(jsonDecode(response.body));
    }
    
    throw Exception('Failed to get conductor status');
  }
}

/// Chat response from Apollo
class ChatResponse {
  final String message;
  final String modelUsed;
  final double costWTF;
  final int responseTimeMs;
  final String? reasoning;
  
  ChatResponse({
    required this.message,
    required this.modelUsed,
    required this.costWTF,
    required this.responseTimeMs,
    this.reasoning,
  });
  
  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      message: json['message'],
      modelUsed: json['model_used'],
      costWTF: json['cost_wtf'].toDouble(),
      responseTimeMs: json['response_time_ms'],
      reasoning: json['reasoning'],
    );
  }
}

/// Data stream recommendation
class DataStream {
  final String symbol;
  final String provider;
  final int costWTF;
  final String reason;
  
  DataStream({
    required this.symbol,
    required this.provider,
    required this.costWTF,
    required this.reason,
  });
  
  factory DataStream.fromJson(Map<String, dynamic> json) {
    return DataStream(
      symbol: json['symbol'],
      provider: json['provider'],
      costWTF: json['cost_wtf'],
      reason: json['reason'],
    );
  }
}

/// Conductor status
class ConductorStatus {
  final int activeJobs;
  final int queuedJobs;
  final Map<String, int> gpuAvailability;
  final double totalCostToday;
  
  ConductorStatus({
    required this.activeJobs,
    required this.queuedJobs,
    required this.gpuAvailability,
    required this.totalCostToday,
  });
  
  factory ConductorStatus.fromJson(Map<String, dynamic> json) {
    return ConductorStatus(
      activeJobs: json['active_jobs'],
      queuedJobs: json['queued_jobs'],
      gpuAvailability: Map<String, int>.from(json['gpu_availability']),
      totalCostToday: json['total_cost_today'].toDouble(),
    );
  }
}

