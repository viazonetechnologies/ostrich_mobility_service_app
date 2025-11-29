import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/providers/authentication_controllers_provider.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/obscure_password_button_widget.dart';
import 'package:provider/provider.dart';

class LoginPasswordTextFieldWidget extends StatelessWidget {
  const LoginPasswordTextFieldWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ObscurePasswordCubit, bool>(
      builder: (context, isObscure) {
        return TextFormField(
          controller: Provider.of<AuthenticationControllersProvider>(
            context,
            listen: false,
          ).loginPasswordController,
          decoration: const InputDecoration(
            hintText: AppStrings.enterPassword,
            prefixIcon: AppIcons.lockIcon,
            suffixIcon: ObscurePasswordButtonWidget(),
          ),
          obscureText: isObscure,
          onTapOutside: (_) => FocusManager.instance.primaryFocus?.unfocus(),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              // User not entered anything!.
              return 'Please enter password';
            }
            return null;
          },
        );
      },
    );
  }
}
