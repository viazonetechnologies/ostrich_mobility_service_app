import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';

class ForgotPasswordButtonWidget extends StatelessWidget {
  const ForgotPasswordButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: () {
        // Go to password reset page.
      },
      child: const Text(AppStrings.forgotPassword),
    );
  }
}
