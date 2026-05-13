import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/chat_response.dart';

class ApiService {
  // For Android emulator use 10.0.2.2, for Windows/desktop use localhost
  static const String _baseUrl = 'http://127.0.0.1:8000/api/v1';

  final http.Client _client = http.Client();

  Future<ChatResponse> sendMessage({
    required String message,
    required String conversationId,
  }) async {
    final url = Uri.parse('$_baseUrl/chat');

    final body = jsonEncode({
      'message': message,
      'conversation_id': conversationId,
      'history': [],
    });

    final response = await _client.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: body,
    );

    if (response.statusCode == 200) {
      return ChatResponse.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    } else {
      throw Exception('Failed: ${response.statusCode} ${response.body}');
    }
  }

  void dispose() {
    _client.close();
  }
}
