import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../models/chat_response.dart';
import '../services/api_service.dart';
import 'hotel_widget.dart';
import 'flight_widget.dart';
import 'info_card.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<ChatMessage> _messages = [];
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ApiService _api = ApiService();
  String _convId = 'conv-${DateTime.now().millisecondsSinceEpoch}';
  bool _loading = false;

  void _newChat() {
    setState(() {
      _messages.clear();
      _convId = 'conv-${DateTime.now().millisecondsSinceEpoch}';
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    _api.dispose();
    super.dispose();
  }

  void _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;

    _controller.clear();
    setState(() {
      _messages.add(ChatMessage(role: 'user', content: text));
      _loading = true;
    });
    _scrollDown();

    try {
      final ChatResponse resp = await _api.sendMessage(
        message: text,
        conversationId: _convId,
      );
      setState(() {
        _messages.add(
          ChatMessage(
            role: 'assistant',
            content: resp.reply,
            uiType: resp.uiType,
            data: resp.data,
          ),
        );
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(
          ChatMessage(
            role: 'assistant',
            content:
                'Error: Could not reach the server. Is the backend running?\n\n($e)',
          ),
        );
        _loading = false;
      });
    }
    _scrollDown();
  }

  void _scrollDown() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.support_agent),
            SizedBox(width: 8),
            Text('AI Support'),
          ],
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'New Chat',
            onPressed: _newChat,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _messages.isEmpty
                ? _buildWelcome()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(12),
                    itemCount: _messages.length,
                    itemBuilder: (ctx, i) => _buildMessage(_messages[i]),
                  ),
          ),
          if (_loading)
            const Padding(
              padding: EdgeInsets.only(bottom: 4),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
          Container(
            color: Theme.of(context).cardColor,
            padding: EdgeInsets.only(
              left: 12,
              right: 12,
              top: 8,
              bottom: MediaQuery.of(context).padding.bottom + 8,
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Type a message...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 10,
                      ),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _send(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _send,
                  icon: const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWelcome() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.support_agent, size: 64, color: Colors.blue.shade300),
            const SizedBox(height: 16),
            const Text(
              'AI Customer Support',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Ask me about hotels, flights, orders, refunds, or complaints.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessage(ChatMessage msg) {
    final isUser = msg.role == 'user';
    return Column(
      crossAxisAlignment: isUser
          ? CrossAxisAlignment.end
          : CrossAxisAlignment.start,
      children: [
        Container(
          margin: const EdgeInsets.only(bottom: 4),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: isUser ? Colors.blue.shade500 : Colors.grey.shade200,
            borderRadius: BorderRadius.only(
              topLeft: const Radius.circular(16),
              topRight: const Radius.circular(16),
              bottomLeft: isUser ? const Radius.circular(16) : Radius.zero,
              bottomRight: isUser ? Radius.zero : const Radius.circular(16),
            ),
          ),
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.75,
          ),
          child: Text(
            msg.content,
            style: TextStyle(color: isUser ? Colors.white : Colors.black87),
          ),
        ),
        if (!isUser && msg.uiType != null) _buildDynamicWidget(msg),
        const SizedBox(height: 8),
      ],
    );
  }

  Widget _buildDynamicWidget(ChatMessage msg) {
    switch (msg.uiType) {
      case 'hotel_list':
        {
          final data = msg.data as Map<String, dynamic>?;
          final hotels = data?['hotels'] as List<dynamic>? ?? [];
          return HotelWidget(hotels: hotels);
        }
      case 'flight_list':
        {
          final data = msg.data as Map<String, dynamic>?;
          final flights = data?['flights'] as List<dynamic>? ?? [];
          return FlightWidget(flights: flights);
        }
      case 'tracking_info':
        {
          final data = msg.data as Map<String, dynamic>? ?? {};
          return InfoCard(
            title: 'Order Tracking',
            fields: {
              'Order ID': data['order_id'],
              'Status': data['status'],
              'Location': data['current_location'],
              'Est. Delivery': data['estimated_delivery'],
              'Carrier': data['carrier'],
            },
          );
        }
      case 'refund_info':
        {
          final data = msg.data as Map<String, dynamic>? ?? {};
          return InfoCard(
            title: 'Refund Status',
            fields: {
              'Order ID': data['order_id'],
              'Amount': data['refund_amount'] != null
                  ? '\u20b9${data['refund_amount']}'
                  : '-',
              'Status': data['status'],
              'Est. Days': data['estimated_days']?.toString(),
              'Payment': data['payment_method'],
            },
          );
        }
      case 'complaint_status':
        {
          final data = msg.data as Map<String, dynamic>? ?? {};
          return InfoCard(
            title: 'Complaint Filed',
            fields: {
              'Ticket ID': data['ticket_id'],
              'Category': data['category'],
              'Status': data['status'],
              'Response Time': data['response_time'],
            },
          );
        }
      case 'escalation_status':
        {
          final data = msg.data as Map<String, dynamic>? ?? {};
          return InfoCard(
            title: 'Escalation',
            fields: {
              'Ticket ID': data['ticket_id'],
              'Escalated To': data['escalated_to'],
              'Priority': data['priority'],
              'Expected': data['expected_response'],
            },
          );
        }
      default:
        return const SizedBox.shrink();
    }
  }
}
