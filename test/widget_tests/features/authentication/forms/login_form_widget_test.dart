import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/forgot_password_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/login_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/forms/login_form_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_password_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_user_name_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

import '../../../../helpers/test_helpers.dart';

void main() {
  setUp(() {
    GetIt.I.registerLazySingleton(() => AuthControllers());
  });
  testWidgets('Login form widget test', (tester) async {
    await tester.binding.setSurfaceSize(testMobileScreenSize);
    await tester.pumpWidget(
      MaterialApp(
        home: MultiBlocProvider(
          providers: [
            BlocProvider(create: (context) => ObscurePasswordCubit()),
          ],
          child: const Material(child: LoginFormWidget()),
        ),
      ),
    );

    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);

    final loginUserNameTextField = find.byType(LoginUserNameTextFieldWidget);
    final loginPasswordTextField = find.byType(LoginPasswordTextFieldWidget);
    final forgotPassword = find.byType(ForgotPasswordButtonWidget);
    final loginButton = find.byType(LoginButtonWidget);

    expect(loginUserNameTextField, findsOneWidget);
    expect(loginPasswordTextField, findsOneWidget);
    expect(forgotPassword, findsOneWidget);
    expect(loginButton, findsOneWidget);

    // Trying to tap the login button and ensures form returns error!.
    await tester.tap(loginButton);
    await tester.pumpAndSettle();

    // Ensuring that the error text's are visible.
    expect(find.text('Please enter your username'), findsOneWidget);
    expect(find.text('Please enter your password'), findsOneWidget);

    // Enter auth credentials
    await tester.enterText(loginUserNameTextField, 'username');
    await tester.pumpAndSettle();

    await tester.enterText(loginPasswordTextField, 'password');
    await tester.pumpAndSettle();

    // Trying to tap the login button again, and ensures form returns nothing!.
    await tester.tap(loginButton);
    await tester.pumpAndSettle();

    // Ensuring that the error text's are not visible.
    expect(find.text('Please enter your username'), findsNothing);
    expect(find.text('Please enter your password'), findsNothing);
  });
}
