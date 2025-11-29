import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/providers/authentication_controllers_provider.dart';
import 'package:provider/provider.dart';

class RegisterEmailTextFieldWidget extends StatelessWidget {
  const RegisterEmailTextFieldWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: Provider.of<AuthenticationControllersProvider>(
        context,
        listen: false,
      ).registerEmailController,
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
