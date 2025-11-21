import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/terms_and_conditions_check_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/create_account_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/go_to_sign_in_page_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_email_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_full_name_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_password_confirm_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_password_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_phone_number_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';
import 'package:ostrich_service/pages/register_page_widget.dart';

import '../../helpers/test_helpers.dart';

void main() {
  setUp(() {
    // Since many inputs using the [AuthControllers]
    GetIt.I.registerLazySingleton(() => AuthControllers());
  });

  testWidgets('Register page widget test', (tester) async {
    await tester.binding.setSurfaceSize(testMobileScreenSize);
    await tester.pumpWidget(
      MaterialApp(
        home: MultiBlocProvider(
          providers: [
            BlocProvider(create: (context) => ObscurePasswordCubit()),
            BlocProvider(create: (context) => TermsAndConditionsCheckCubit()),
          ],
          child: const RegisterPageWidget(),
        ),
      ),
    );

    // Ensures that no overflow error.
    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);

    // Find widgets
    expect(find.byType(RegisterFullNameTextFieldWidget), findsOneWidget);
    expect(find.byType(RegisterEmailTextFieldWidget), findsOneWidget);
    expect(find.byType(RegisterPhoneNumberTextFieldWidget), findsOneWidget);
    expect(find.byType(RegisterPasswordTextFieldWidget), findsOneWidget);
    expect(find.byType(RegisterPasswordConfirmTextFieldWidget), findsOneWidget);
    expect(find.byType(CreateAccountButtonWidget), findsOneWidget);
    expect(find.byType(GoToSignInPageButtonWidget), findsOneWidget);

    // Invoke keyboard to ensure still no overflow
    await tester.showKeyboard(find.byType(RegisterPasswordTextFieldWidget));
    await tester.pumpAndSettle();

    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);
  });
}
