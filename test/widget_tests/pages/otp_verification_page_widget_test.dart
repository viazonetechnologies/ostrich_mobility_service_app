import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/verify_otp_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_otp_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';
import 'package:ostrich_service/pages/register_otp_verification_page_widget.dart';

import '../../helpers/test_helpers.dart';

void main() {
  setUp(() {
    // Since many inputs using the [AuthControllers]
    GetIt.I.registerLazySingleton(() => AuthControllers());
  });

  testWidgets('OTP Verification page widget test', (tester) async {
    await tester.binding.setSurfaceSize(testMobileScreenSize);
    await tester.pumpWidget(
      const MaterialApp(home: RegisterOtpVerificationPageWidget()),
    );

    // Ensures that no overflow error.
    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);

    // Find widgets
    expect(find.byType(RegisterOtpTextFieldWidget), findsOneWidget);
    expect(find.byType(VerifyOtpButtonWidget), findsOneWidget);

    // Invoke keyboard to ensure still no overflow
    await tester.showKeyboard(find.byKey(const Key('OTP Field 0')));
    await tester.pumpAndSettle();

    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);
  });
}
