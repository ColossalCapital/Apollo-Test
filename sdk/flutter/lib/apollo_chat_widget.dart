import 'package:flutter/material.dart';
import 'apollo_service.dart';

/// Apollo AI Chat Widget - Reusable across Delt, Atlas, Akashic
/// 
/// Usage:
/// ```dart
/// ApolloChatWidget(
///   apiKey: 'your_api_key',
///   userId: 'user_id',
///   context: 'trading', // or 'knowledge', 'coding'
/// )
/// ```
class ApolloChatWidget extends StatefulWidget {
  final String apiKey;
  final String userId;
  final String context; // trading, knowledge, coding
  final Color? primaryColor;
  final Color? backgroundColor;
  final bool showFloatingBubble;
  final Function(String)? onMessageSent;
  final Function(String)? onResponseReceived;

  const ApolloChatWidget({
    Key? key,
    required this.apiKey,
    required this.userId,
    required this.context,
    this.primaryColor,
    this.backgroundColor,
    this.showFloatingBubble = false,
    this.onMessageSent,
    this.onResponseReceived,
  }) : super(key: key);

  @override
  State<ApolloChatWidget> createState() => _ApolloChatWidgetState();
}

class _ApolloChatWidgetState extends State<ApolloChatWidget> {
  late final ApolloService _apolloService;
  final TextEditingController _chatController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _apolloService = ApolloService(
      apiKey: widget.apiKey,
      userId: widget.userId,
    );
    _addWelcomeMessage();
  }

  @override
  void dispose() {
    _chatController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _addWelcomeMessage() {
    final welcomeMessages = {
      'trading': "👋 Hi! I'm Apollo, your AI trading assistant. I can help you analyze markets, create strategies, and optimize your portfolio.",
      'knowledge': "👋 Hi! I'm Apollo, your AI knowledge assistant. I can help you organize information, find insights, and answer questions.",
      'coding': "👋 Hi! I'm Apollo, your AI coding assistant. I can help you write code, debug issues, and optimize algorithms.",
    };

    setState(() {
      _messages.add(ChatMessage(
        text: welcomeMessages[widget.context] ?? "👋 Hi! I'm Apollo, your AI assistant.",
        isUser: false,
        timestamp: DateTime.now(),
      ));
    });
  }

  Future<void> _sendMessage() async {
    final text = _chatController.text.trim();
    if (text.isEmpty) return;

    // Add user message
    setState(() {
      _messages.add(ChatMessage(
        text: text,
        isUser: true,
        timestamp: DateTime.now(),
      ));
      _isLoading = true;
    });

    _chatController.clear();
    _scrollToBottom();

    // Callback
    widget.onMessageSent?.call(text);

    try {
      // Get Apollo response
      final response = await _apolloService.chat(
        message: text,
        context: widget.context,
        conversationHistory: _messages.map((m) => {
          'role': m.isUser ? 'user' : 'assistant',
          'content': m.text,
        }).toList(),
      );

      // Add Apollo response
      setState(() {
        _messages.add(ChatMessage(
          text: response,
          isUser: false,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });

      // Callback
      widget.onResponseReceived?.call(response);

      _scrollToBottom();
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: "Sorry, I encountered an error. Please try again.",
          isUser: false,
          timestamp: DateTime.now(),
          isError: true,
        ));
        _isLoading = false;
      });
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final primaryColor = widget.primaryColor ?? const Color(0xFF6366F1);
    final backgroundColor = widget.backgroundColor ?? const Color(0xFF0F172A);

    return Container(
      color: backgroundColor,
      child: Column(
        children: [
          // Chat messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length && _isLoading) {
                  return _buildLoadingIndicator(primaryColor);
                }
                return _buildMessageBubble(_messages[index], primaryColor);
              },
            ),
          ),

          // Input bar
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: backgroundColor,
              border: Border(
                top: BorderSide(
                  color: Colors.white.withOpacity(0.1),
                  width: 1,
                ),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _chatController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Ask Apollo anything...',
                      hintStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.05),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [primaryColor, primaryColor.withOpacity(0.8)],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: IconButton(
                    icon: const Icon(Icons.send, color: Colors.white),
                    onPressed: _sendMessage,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message, Color primaryColor) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: message.isUser
              ? primaryColor
              : message.isError
                  ? Colors.red.withOpacity(0.2)
                  : Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.text,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              _formatTime(message.timestamp),
              style: TextStyle(
                color: Colors.white.withOpacity(0.5),
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingIndicator(Color primaryColor) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(primaryColor),
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'Apollo is thinking...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final bool isError;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.isError = false,
  });
}
