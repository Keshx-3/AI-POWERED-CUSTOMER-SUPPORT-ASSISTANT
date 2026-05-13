import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:customer_support_chat/main.dart';

void main() {
  testWidgets('App renders welcome screen', (WidgetTester tester) async {
    await tester.pumpWidget(const CustomerSupportApp());
    expect(find.text('AI Customer Support'), findsOneWidget);
    expect(find.byIcon(Icons.support_agent), findsWidgets);
  });
}
