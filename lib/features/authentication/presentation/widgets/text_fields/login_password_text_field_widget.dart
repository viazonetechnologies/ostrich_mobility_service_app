import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/core/cubits/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/obscure_password_button_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

class LoginPasswordTextFieldWidget extends StatelessWidget {
  const LoginPasswordTextFieldWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ObscurePasswordCubit, bool>(
      builder: (context, isObscure) {
        return TextFormField(
          controller: GetIt.I<AuthControllers>().loginPassword,
          decoration: InputDecoration(
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10.0),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10.0),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            hintText: AppStrings.enterYourPassword,
            prefixIcon: AppIcons.lockIcon,
            suffixIcon: const ObscurePasswordButtonWidget(),
          ),
          obscureText: isObscure,
          onTapOutside: (_) => FocusManager.instance.primaryFocus?.unfocus(),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              // User not entered anything!.
              return 'Please enter your password';
            }
            return null;
          },
        );
      },
    );
  }
}
