import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:akinator_frontend/app.dart';
import 'package:akinator_frontend/widgets/answer_button.dart';

void main() {
  testWidgets('App renders Home screen with Bangla Akinator title and Start button',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: BanglaAkinatorApp(),
      ),
    );

    expect(find.text('বাংলা জ্বিন'), findsOneWidget);
    expect(find.text('খেলা শুরু করুন'), findsOneWidget);
  });

  testWidgets('AnswerButton responds to tap and displays label',
      (WidgetTester tester) async {
    bool tapped = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AnswerButton(
            label: 'হ্যাঁ (Yes)',
            answerEnum: 'YES',
            baseColor: Colors.green,
            icon: Icons.check,
            isEnabled: true,
            onPressed: () => tapped = true,
          ),
        ),
      ),
    );

    expect(find.text('হ্যাঁ (Yes)'), findsOneWidget);
    await tester.tap(find.byType(AnswerButton));
    await tester.pump();

    expect(tapped, isTrue);
  });
}
