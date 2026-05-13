class ChatMessage {
  final String role;
  final String content;
  final String? uiType;
  final dynamic data;

  ChatMessage({
    required this.role,
    required this.content,
    this.uiType,
    this.data,
  });

  Map<String, dynamic> toJson() => {
    'role': role,
    'content': content,
    if (uiType != null) 'ui_type': uiType,
    if (data != null) 'data': data,
  };

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
    role: json['role'] as String,
    content: json['content'] as String,
    uiType: json['ui_type'] as String?,
    data: json['data'],
  );
}
