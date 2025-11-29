import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/providers/authentication_controllers_provider.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/verify_otp_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_otp_text_field_widget.dart';
import 'package:provider/provider.dart';

class RegisterOtpVerificationPageWidget extends StatelessWidget {
  const RegisterOtpVerificationPageWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: AppColors.primaryColor,
        centerTitle: true,
        title: const Text(
          AppStrings.ostrichMobility,
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(15.0),
          child: ChangeNotifierProvider(
            create: (context) => AuthenticationControllersProvider(),
            child: const Column(
              mainAxisAlignment: MainAxisAlignment.center,
              spacing: 10.0,
              children: [
                FittedBox(
                  child: Text(
                    AppStrings.otpVerification,
                    style: TextStyle(
                      fontSize: 25.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Text(
                  AppStrings
                      .enterYourMobileNumberOrEmailToReceiveAVerificationCode,
                  textAlign: TextAlign.center,
                ),
                RegisterOtpTextFieldWidget(),
                VerifyOtpButtonWidget(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
