import 'package:flutter/material.dart';
import 'apollo_chat_widget.dart';

/// Floating Apollo Bubble - Can be added to any screen
/// Shows a floating bubble that expands into chat when tapped
class ApolloFloatingBubble extends StatefulWidget {
  final String apiKey;
  final String userId;
  final String context;
  final Color? primaryColor;
  final Alignment alignment;
  final EdgeInsets padding;

  const ApolloFloatingBubble({
    Key? key,
    required this.apiKey,
    required this.userId,
    required this.context,
    this.primaryColor,
    this.alignment = Alignment.bottomRight,
    this.padding = const EdgeInsets.all(16),
  }) : super(key: key);

  @override
  State<ApolloFloatingBubble> createState() => _ApolloFloatingBubbleState();
}

class _ApolloFloatingBubbleState extends State<ApolloFloatingBubble>
    with SingleTickerProviderStateMixin {
  bool _isExpanded = false;
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _scaleAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _toggleChat() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final primaryColor = widget.primaryColor ?? const Color(0xFF6366F1);

    return Stack(
      children: [
        // Expanded chat
        if (_isExpanded)
          Positioned.fill(
            child: GestureDetector(
              onTap: _toggleChat,
              child: Container(
                color: Colors.black.withOpacity(0.5),
              ),
            ),
          ),

        // Chat container
        if (_isExpanded)
          Align(
            alignment: widget.alignment,
            child: ScaleTransition(
              scale: _scaleAnimation,
              child: Container(
                width: MediaQuery.of(context).size.width * 0.9,
                height: MediaQuery.of(context).size.height * 0.7,
                margin: widget.padding,
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: primaryColor.withOpacity(0.3),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    // Header
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [primaryColor, primaryColor.withOpacity(0.8)],
                        ),
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(20),
                          topRight: Radius.circular(20),
                        ),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.auto_awesome, color: Colors.white),
                          const SizedBox(width: 12),
                          const Text(
                            'Apollo AI',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const Spacer(),
                          IconButton(
                            icon: const Icon(Icons.close, color: Colors.white),
                            onPressed: _toggleChat,
                          ),
                        ],
                      ),
                    ),

                    // Chat widget
                    Expanded(
                      child: ApolloChatWidget(
                        apiKey: widget.apiKey,
                        userId: widget.userId,
                        context: widget.context,
                        primaryColor: primaryColor,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        // Floating bubble
        if (!_isExpanded)
          Align(
            alignment: widget.alignment,
            child: Padding(
              padding: widget.padding,
              child: GestureDetector(
                onTap: _toggleChat,
                child: Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [primaryColor, primaryColor.withOpacity(0.8)],
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: primaryColor.withOpacity(0.5),
                        blurRadius: 15,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.auto_awesome,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Quick Action Bubble - Shows suggested actions
class ApolloQuickActions extends StatelessWidget {
  final List<QuickAction> actions;
  final Function(QuickAction) onActionTap;
  final Color? primaryColor;

  const ApolloQuickActions({
    Key? key,
    required this.actions,
    required this.onActionTap,
    this.primaryColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final primaryColor = this.primaryColor ?? const Color(0xFF6366F1);

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_awesome, color: primaryColor, size: 20),
              const SizedBox(width: 8),
              const Text(
                'Quick Actions',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: actions.map((action) {
              return GestureDetector(
                onTap: () => onActionTap(action),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: primaryColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: primaryColor.withOpacity(0.5),
                      width: 1,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(action.icon, color: primaryColor, size: 16),
                      const SizedBox(width: 6),
                      Text(
                        action.label,
                        style: TextStyle(
                          color: primaryColor,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class QuickAction {
  final String label;
  final IconData icon;
  final String prompt;

  QuickAction({
    required this.label,
    required this.icon,
    required this.prompt,
  });
}

/// Pre-defined quick actions for different contexts
class ApolloQuickActionsPresets {
  static List<QuickAction> trading = [
    QuickAction(
      label: 'Analyze Market',
      icon: Icons.analytics,
      prompt: 'Analyze current market conditions',
    ),
    QuickAction(
      label: 'Get Recommendations',
      icon: Icons.recommend,
      prompt: 'What should I trade today?',
    ),
    QuickAction(
      label: 'Optimize Portfolio',
      icon: Icons.pie_chart,
      prompt: 'Optimize my portfolio allocation',
    ),
    QuickAction(
      label: 'Risk Analysis',
      icon: Icons.warning,
      prompt: 'Analyze my portfolio risk',
    ),
  ];

  static List<QuickAction> knowledge = [
    QuickAction(
      label: 'Summarize',
      icon: Icons.summarize,
      prompt: 'Summarize this document',
    ),
    QuickAction(
      label: 'Find Insights',
      icon: Icons.lightbulb,
      prompt: 'What are the key insights?',
    ),
    QuickAction(
      label: 'Ask Question',
      icon: Icons.question_answer,
      prompt: 'I have a question about...',
    ),
    QuickAction(
      label: 'Connect Ideas',
      icon: Icons.hub,
      prompt: 'How does this relate to...?',
    ),
  ];

  static List<QuickAction> coding = [
    QuickAction(
      label: 'Debug Code',
      icon: Icons.bug_report,
      prompt: 'Help me debug this code',
    ),
    QuickAction(
      label: 'Optimize',
      icon: Icons.speed,
      prompt: 'How can I optimize this?',
    ),
    QuickAction(
      label: 'Explain',
      icon: Icons.info,
      prompt: 'Explain how this works',
    ),
    QuickAction(
      label: 'Write Tests',
      icon: Icons.check_circle,
      prompt: 'Generate tests for this code',
    ),
  ];
}
