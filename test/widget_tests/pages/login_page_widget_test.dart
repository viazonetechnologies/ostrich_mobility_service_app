import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/go_to_sign_up_page_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/login_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_password_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_user_name_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';
import 'package:ostrich_service/pages/login_page_widget.dart';

import '../../helpers/test_helpers.dart';

void main() {
  setUp(() {
    // Since many inputs using the [AuthControllers]
    GetIt.I.registerLazySingleton(() => AuthControllers());
  });

  testWidgets('Login page widget test', (tester) async {
    await tester.binding.setSurfaceSize(testDeviceScreenSize);
    await tester.pumpWidget(
      MaterialApp(
        home: MultiBlocProvider(
          providers: [
            BlocProvider(create: (context) => ObscurePasswordCubit()),
          ],
          child: const LoginPageWidget(),
        ),
      ),
    );

    // Ensures that no overflow error.
    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);

    // Find widgets
    expect(find.byType(LoginUserNameTextFieldWidget), findsOneWidget);
    expect(find.byType(LoginPasswordTextFieldWidget), findsOneWidget);
    expect(find.byType(LoginButtonWidget), findsOneWidget);
    expect(find.byType(GoToSignUpPageButtonWidget), findsOneWidget);

    // Invoke keyboard to ensure still no overflow
    await tester.showKeyboard(find.byType(LoginPasswordTextFieldWidget));
    await tester.pumpAndSettle();

    expect(find.byType(OverflowBar), findsNothing);
    expect(find.byType(OverflowBox), findsNothing);
  });
}
