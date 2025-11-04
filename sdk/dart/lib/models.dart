/// Apollo AI SDK Models

class Message {
  final String role;  // 'user' or 'assistant'
  final String content;
  final String? timestamp;
  
  Message({
    required this.role,
    required this.content,
    this.timestamp,
  });
  
  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      role: json['role'],
      content: json['content'],
      timestamp: json['timestamp'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'role': role,
      'content': content,
      'timestamp': timestamp,
    };
  }
}

class ApolloResponse {
  final String response;
  final List<ActionButton>? actions;
  final List<String>? suggestions;
  final String conversationId;
  
  ApolloResponse({
    required this.response,
    this.actions,
    this.suggestions,
    required this.conversationId,
  });
  
  factory ApolloResponse.fromJson(Map<String, dynamic> json) {
    return ApolloResponse(
      response: json['response'],
      actions: json['actions'] != null
          ? (json['actions'] as List).map((a) => ActionButton.fromJson(a)).toList()
          : null,
      suggestions: json['suggestions'] != null
          ? List<String>.from(json['suggestions'])
          : null,
      conversationId: json['conversation_id'],
    );
  }
}

class ActionButton {
  final String label;
  final String action;
  final String? route;
  
  ActionButton({
    required this.label,
    required this.action,
    this.route,
  });
  
  factory ActionButton.fromJson(Map<String, dynamic> json) {
    return ActionButton(
      label: json['label'],
      action: json['action'],
      route: json['route'],
    );
  }
}

class AnalysisResponse {
  final String analysis;
  final List<Insight> insights;
  final List<Recommendation> recommendations;
  
  AnalysisResponse({
    required this.analysis,
    required this.insights,
    required this.recommendations,
  });
  
  factory AnalysisResponse.fromJson(Map<String, dynamic> json) {
    return AnalysisResponse(
      analysis: json['analysis'],
      insights: (json['insights'] as List)
          .map((i) => Insight.fromJson(i))
          .toList(),
      recommendations: (json['recommendations'] as List)
          .map((r) => Recommendation.fromJson(r))
          .toList(),
    );
  }
}

class Insight {
  final String type;
  final String text;
  
  Insight({
    required this.type,
    required this.text,
  });
  
  factory Insight.fromJson(Map<String, dynamic> json) {
    return Insight(
      type: json['type'],
      text: json['text'],
    );
  }
}

class Recommendation {
  final String action;
  final String reason;
  
  Recommendation({
    required this.action,
    required this.reason,
  });
  
  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      action: json['action'],
      reason: json['reason'],
    );
  }
}

class Permission {
  final String userId;
  final String fromService;
  final String toService;
  final List<String> scopes;
  final bool granted;
  final String? grantedAt;
  
  Permission({
    required this.userId,
    required this.fromService,
    required this.toService,
    required this.scopes,
    required this.granted,
    this.grantedAt,
  });
  
  factory Permission.fromJson(Map<String, dynamic> json) {
    return Permission(
      userId: json['user_id'],
      fromService: json['from_service'],
      toService: json['to_service'],
      scopes: List<String>.from(json['scopes']),
      granted: json['granted'],
      grantedAt: json['granted_at'],
    );
  }
}

