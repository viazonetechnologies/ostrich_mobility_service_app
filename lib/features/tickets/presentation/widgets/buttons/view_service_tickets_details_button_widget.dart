import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';

class ViewServiceTicketsDetailsButtonWidget extends StatelessWidget {
  const ViewServiceTicketsDetailsButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialButton(
      color: AppColors.primaryColor,
      elevation: 0.0,
      padding: const EdgeInsets.all(10.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
      textColor: Colors.white,
      onPressed: () {
        // Go to the Details view page for tickets
      },
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        spacing: 10.0,
        children: [
          AppIcons.eyeIcon,
          Flexible(
            child: Text(
              AppStrings.viewDetails,
              style: TextStyle(fontWeight: FontWeight.normal),
            ),
          ),
        ],
      ),
    );
  }
}
