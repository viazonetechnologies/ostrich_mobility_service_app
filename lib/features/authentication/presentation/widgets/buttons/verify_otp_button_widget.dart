import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';

class VerifyOtpButtonWidget extends StatelessWidget {
  const VerifyOtpButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialButton(
      color: AppColors.primaryColor,
      elevation: 0.0,
      minWidth: MediaQuery.of(context).size.width,
      padding: const EdgeInsets.all(15.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
      textColor: Colors.white,
      onPressed: () {},
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        spacing: 5.0,
        children: [AppIcons.sendIcon, Text('Verify OTP')],
      ),
    );
  }
}
