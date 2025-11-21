import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/verify_otp_button_widget.dart';

void main() {
  testWidgets('Verify OTP button widget test', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: VerifyOtpButtonWidget()));

    expect(find.byType(MaterialButton), findsOneWidget);
    expect(find.byType(Row), findsOneWidget);
    expect(find.byType(Icon), findsOneWidget);
    expect(find.byType(Text), findsOneWidget);

    expect(find.byIcon(AppIcons.sendIcon.icon!), findsOneWidget);

    expect(find.text('Verify OTP'), findsOneWidget);
  });
}
