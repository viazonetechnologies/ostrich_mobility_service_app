import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';

class OpenPrivacyPolicyButtonWidget extends StatelessWidget {
  const OpenPrivacyPolicyButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        // Open the privacy policy
      },
      child: const Text(
        AppStrings.privacyPolicy,
        style: TextStyle(color: AppColors.primaryColor),
      ),
    );
  }
}
