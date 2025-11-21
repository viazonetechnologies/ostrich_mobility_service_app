import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/obscure_password_button_widget.dart';

void main() {
  testWidgets('Obscure password button widget test', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: BlocProvider(
          create: (context) => ObscurePasswordCubit(),
          child: const ObscurePasswordButtonWidget(),
        ),
      ),
    );

    final obscureIconButton = find.byType(IconButton);
    expect(obscureIconButton, findsOneWidget);
    expect(find.byType(Icon), findsOneWidget);

    // Get the ObscurePasswordCubit instance.
    final obscurePasswordCubit = BlocProvider.of<ObscurePasswordCubit>(
      tester.element(find.byType(IconButton)),
    );

    // By default the state is true!.
    expect(obscurePasswordCubit.state, true);
    expect(find.byIcon(AppIcons.eyeIcon.icon!), findsOneWidget);

    // Change the obscure state
    await tester.tap(obscureIconButton);
    await tester.pumpAndSettle();

    expect(obscurePasswordCubit.state, false);
    expect(find.byIcon(AppIcons.eyeOffIcon.icon!), findsOneWidget);
  });
}
