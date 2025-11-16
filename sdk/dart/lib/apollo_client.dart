import 'package:dio/dio.dart';
import 'models.dart';

/// Apollo AI Client SDK for Dart/Flutter
/// 
/// Provides easy integration with the Apollo AI service from Delt and other Flutter apps
class ApolloClient {
  final Dio _dio;
  final String apiUrl;
  final String apiKey;
  
  ApolloClient({
    required this.apiUrl,
    required this.apiKey,
  }) : _dio = Dio() {
    _dio.options.baseUrl = apiUrl;
    _dio.options.headers['Authorization'] = 'Bearer $apiKey';
    _dio.options.connectTimeout = Duration(seconds: 30);
    _dio.options.receiveTimeout = Duration(seconds: 30);
  }
  
  /// Send a chat message to Apollo
  Future<ApolloResponse> chat({
    required String message,
    required String userId,
    required String service,  // 'delt', 'atlas', 'akashic'
    Map<String, dynamic>? context,
  }) async {
    try {
      final response = await _dio.post('/api/chat', data: {
        'message': message,
        'user_id': userId,
        'service': service,
        'context': context,
      });
      
      return ApolloResponse.fromJson(response.data);
    } catch (e) {
      throw ApolloException('Failed to send message: $e');
    }
  }
  
  /// Get conversation history
  Future<List<Message>> getConversationHistory({
    required String userId,
    required String service,
  }) async {
    try {
      final response = await _dio.get(
        '/api/conversations/$userId',
        queryParameters: {'service': service},
      );
      
      final messages = (response.data['messages'] as List)
          .map((m) => Message.fromJson(m))
          .toList();
      
      return messages;
    } catch (e) {
      throw ApolloException('Failed to get conversation: $e');
    }
  }
  
  /// Delete conversation
  Future<void> deleteConversation({
    required String conversationId,
  }) async {
    try {
      await _dio.delete('/api/conversations/$conversationId');
    } catch (e) {
      throw ApolloException('Failed to delete conversation: $e');
    }
  }
  
  /// Analyze data
  Future<AnalysisResponse> analyze({
    required String dataType,  // 'portfolio', 'code', 'document'
    required Map<String, dynamic> data,
    required String userId,
  }) async {
    try {
      final response = await _dio.post('/api/analyze', data: {
        'data_type': dataType,
        'data': data,
        'user_id': userId,
      });
      
      return AnalysisResponse.fromJson(response.data);
    } catch (e) {
      throw ApolloException('Failed to analyze: $e');
    }
  }
  
  /// Check if permission exists
  Future<bool> checkPermission({
    required String userId,
    required String fromService,
    required String toService,
    required List<String> scopes,
  }) async {
    try {
      final response = await _dio.get('/api/permissions/check', queryParameters: {
        'user_id': userId,
        'from_service': fromService,
        'to_service': toService,
        'scopes': scopes.join(','),
      });
      
      return response.data['allowed'] as bool;
    } catch (e) {
      return false;
    }
  }
  
  /// Grant permission
  Future<void> grantPermission({
    required String userId,
    required String fromService,
    required String toService,
    required List<String> scopes,
  }) async {
    try {
      await _dio.post('/api/permissions/grant', data: {
        'user_id': userId,
        'from_service': fromService,
        'to_service': toService,
        'scopes': scopes,
      });
    } catch (e) {
      throw ApolloException('Failed to grant permission: $e');
    }
  }
  
  /// Revoke permission
  Future<void> revokePermission({
    required String userId,
    required String fromService,
    required String toService,
  }) async {
    try {
      await _dio.post('/api/permissions/revoke', data: {
        'user_id': userId,
        'from_service': fromService,
        'to_service': toService,
      });
    } catch (e) {
      throw ApolloException('Failed to revoke permission: $e');
    }
  }
  
  /// Add context
  Future<void> addContext({
    required String userId,
    required String service,
    required Map<String, dynamic> context,
  }) async {
    try {
      await _dio.post('/api/context/add', queryParameters: {
        'user_id': userId,
        'service': service,
      }, data: context);
    } catch (e) {
      throw ApolloException('Failed to add context: $e');
    }
  }
  
  /// Get context
  Future<Map<String, dynamic>> getContext({
    required String userId,
    String? service,
  }) async {
    try {
      final response = await _dio.get('/api/context/$userId', queryParameters: {
        if (service != null) 'service': service,
      });
      
      return response.data['context'] as Map<String, dynamic>;
    } catch (e) {
      throw ApolloException('Failed to get context: $e');
    }
  }
}

class ApolloException implements Exception {
  final String message;
  ApolloException(this.message);
  
  @override
  String toString() => 'ApolloException: $message';
}

