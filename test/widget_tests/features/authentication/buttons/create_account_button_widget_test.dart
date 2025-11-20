import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/create_account_button_widget.dart';

void main() {
  testWidgets('Create account button widget test', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: CreateAccountButtonWidget()),
    );

    expect(find.byType(MaterialButton), findsOneWidget);
    expect(find.byType(Row), findsOneWidget);
    expect(find.byType(Icon), findsOneWidget);
    expect(find.byType(Text), findsOneWidget);

    expect(find.byIcon(AppIcons.personAddIcon.icon!), findsOneWidget);

    expect(find.text(AppStrings.createAccount), findsOneWidget);
  });
}
