import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

class RegisterEmailTextFieldWidget extends StatelessWidget {
  const RegisterEmailTextFieldWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: GetIt.I<AuthControllers>().registerEmail,
      decoration: const InputDecoration(
        hintText: AppStrings.enterEmail,
        prefixIcon: AppIcons.emailIcon,
      ),
      keyboardType: TextInputType.emailAddress,
      onTapOutside: (_) => FocusManager.instance.primaryFocus?.unfocus(),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          // User not entered anything!.
          return 'Please enter email address';
        }
        return null;
      },
    );
  }
}
