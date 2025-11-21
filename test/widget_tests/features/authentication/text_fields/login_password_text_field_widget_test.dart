import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/obscure_password_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_password_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

void main() {
  setUp(() {
    GetIt.I.registerLazySingleton(() => AuthControllers());
  });
  testWidgets('Login password text field widget test', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Material(
          child: BlocProvider(
            create: (context) => ObscurePasswordCubit(),
            child: const LoginPasswordTextFieldWidget(),
          ),
        ),
      ),
    );

    final textFormField = find.byType(TextFormField);
    expect(textFormField, findsOneWidget);
    expect(find.byType(ObscurePasswordButtonWidget), findsOneWidget);
    expect(find.text(AppStrings.enterYourPassword), findsOneWidget);

    // Get reference to the text field controller
    final loginPassword = GetIt.I<AuthControllers>().loginPassword;

    // Ensures that, initially the controller is empty.
    expect(loginPassword.value.text.isEmpty, true);

    // Enter some text on the text field
    await tester.enterText(textFormField, 'password');
    await tester.pumpAndSettle();

    // Ensures that, controller updated with value.
    expect(loginPassword.value.text.isEmpty, false);
    expect(loginPassword.value.text, 'password');
  });
}
