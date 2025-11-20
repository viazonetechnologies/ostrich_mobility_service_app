import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/globals/app_global_keys.dart';

class LoginButtonWidget extends StatelessWidget {
  const LoginButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialButton(
      color: AppColors.primaryColor,
      elevation: 0.0,
      minWidth: MediaQuery.of(context).size.width,
      padding: const EdgeInsets.all(15.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
      textColor: Colors.white,
      onPressed: () {
        // Validate the login form data using global FormState key.
        bool isLoginFormValid = loginFormGlobalKey.currentState!.validate();
        if (!isLoginFormValid) {
          // The form isn't valid can't proceed with further steps!..
          return;
        }

        // Form validated successfully, login the user.
      },
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        spacing: 5.0,
        children: [AppIcons.logoutIcon, Text('Log in')],
      ),
    );
  }
}
