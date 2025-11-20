import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/terms_and_conditions_check_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/check_boxes/terms_and_conditions_agree_check_box_widget.dart';

void main() {
  testWidgets('Terms and conditions agree check box widget test', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: BlocProvider(
          create: (context) => TermsAndConditionsCheckCubit(),
          child: const Material(child: TermsAndConditionsAgreeCheckBoxWidget()),
        ),
      ),
    );

    // Find widgets
    final checkBoxFinder = find.byType(Checkbox);
    expect(checkBoxFinder, findsOneWidget);
    // Initially the value property of check box is false.
    expect(tester.widget<Checkbox>(checkBoxFinder).value, false);

    await tester.tap(checkBoxFinder);
    await tester.pumpAndSettle();

    // The check box value property is now true.
    expect(tester.widget<Checkbox>(checkBoxFinder).value, true);
  });
}
