import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';

class OpenTermsOfServiceButtonWidget extends StatelessWidget {
  const OpenTermsOfServiceButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        // Open terms of service.
      },
      child: const Text(
        AppStrings.termsOfService,
        style: TextStyle(color: AppColors.primaryColor),
      ),
    );
  }
}
