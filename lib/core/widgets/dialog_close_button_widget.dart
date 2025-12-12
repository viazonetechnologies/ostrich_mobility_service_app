import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';

class DialogCloseButtonWidget extends StatelessWidget {
  const DialogCloseButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialButton(
      elevation: 0.0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10.0),
        side: const BorderSide(color: AppColors.primaryColor),
      ),
      textColor: AppColors.primaryColor,
      onPressed: () {
        Navigator.pop(context);
      },
      child: const Text(AppStrings.close),
    );
  }
}
