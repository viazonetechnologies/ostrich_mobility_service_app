import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/core/globals/app_global_keys.dart';

class CreateAccountButtonWidget extends StatelessWidget {
  const CreateAccountButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialButton(
      elevation: 0.0,
      padding: const EdgeInsets.all(10.0),
      textColor: Colors.white,
      onPressed: () {
        // Validate the register form data using global FormState key.
        bool isLoginFormValid = registerFormGlobalKey.currentState!.validate();
        if (!isLoginFormValid) {
          // The form isn't valid can't proceed with further steps!..
          return;
        }

        // Form validated successfully, register the user.
      },
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        spacing: 5.0,
        children: [AppIcons.personAddIcon, Text(AppStrings.createAccount)],
      ),
    );
  }
}
