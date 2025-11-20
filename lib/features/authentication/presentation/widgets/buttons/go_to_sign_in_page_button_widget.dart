import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/routes/nav_routes.dart';

class GoToSignInPageButtonWidget extends StatelessWidget {
  const GoToSignInPageButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialButton(
      elevation: 0.0,
      minWidth: MediaQuery.of(context).size.width,
      padding: const EdgeInsets.all(15.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10.0),
        side: const BorderSide(color: AppColors.primaryColor),
      ),
      textColor: AppColors.primaryColor,
      onPressed: () {
        // Go to sign up page.
        GoRouter.of(context).go(NavRoutes.loginPage);
      },
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        spacing: 5.0,
        children: [AppIcons.logoutIcon, Text('Sign In')],
      ),
    );
  }
}
