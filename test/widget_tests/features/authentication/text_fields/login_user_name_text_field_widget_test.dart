import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_user_name_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

void main() {
  setUp(() {
    GetIt.I.registerLazySingleton(() => AuthControllers());
  });
  testWidgets('Login user name text field widget test', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Material(child: LoginUserNameTextFieldWidget())),
    );

    final textFormField = find.byType(TextFormField);
    expect(textFormField, findsOneWidget);
    expect(find.text(AppStrings.enterUsername), findsOneWidget);

    // Get reference to the text field controller
    final loginUserName = GetIt.I<AuthControllers>().loginUsername;

    // Ensures that, initially the controller is empty.
    expect(loginUserName.value.text.isEmpty, true);

    // Enter some text on the text field
    await tester.enterText(textFormField, 'username');
    await tester.pumpAndSettle();

    // Ensures that, controller updated with value.
    expect(loginUserName.value.text.isEmpty, false);
    expect(loginUserName.value.text, 'username');
  });
}
