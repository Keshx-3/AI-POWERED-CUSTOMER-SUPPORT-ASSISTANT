import 'package:flutter/material.dart';
import 'widgets/chat_screen.dart';

void main() {
  runApp(const CustomerSupportApp());
}

class CustomerSupportApp extends StatelessWidget {
  const CustomerSupportApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Customer Support',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.blue, useMaterial3: true),
      home: const ChatScreen(),
    );
  }
}
