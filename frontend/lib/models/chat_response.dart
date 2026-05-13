class ChatResponse {
  final String reply;
  final String? uiType;
  final dynamic data;
  final String intent;
  final String conversationId;

  ChatResponse({
    required this.reply,
    this.uiType,
    this.data,
    required this.intent,
    required this.conversationId,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) => ChatResponse(
    reply: json['reply'] as String,
    uiType: json['ui_type'] as String?,
    data: json['data'],
    intent: json['intent'] as String,
    conversationId: json['conversation_id'] as String,
  );
}
