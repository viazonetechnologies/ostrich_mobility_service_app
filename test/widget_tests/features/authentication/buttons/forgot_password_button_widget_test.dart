import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/forgot_password_button_widget.dart';

void main() {
  testWidgets('Forgot password button widget test', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: ForgotPasswordButtonWidget()),
    );

    expect(find.byType(TextButton), findsOneWidget);
    expect(find.byType(Text), findsOneWidget);
    expect(find.text(AppStrings.forgotPassword), findsOneWidget);
  });
}
