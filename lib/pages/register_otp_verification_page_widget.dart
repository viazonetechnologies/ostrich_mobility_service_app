import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/verify_otp_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_otp_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

class RegisterOtpVerificationPageWidget extends StatefulWidget {
  const RegisterOtpVerificationPageWidget({super.key});

  @override
  State<RegisterOtpVerificationPageWidget> createState() =>
      _RegisterOtpVerificationPageWidgetState();
}

class _RegisterOtpVerificationPageWidgetState
    extends State<RegisterOtpVerificationPageWidget> {
  late AuthControllers _authControllers;

  @override
  void initState() {
    super.initState();
    _authControllers = GetIt.I<AuthControllers>();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: AppColors.primaryColor,
        centerTitle: true,
        title: const Text(
          AppStrings.appName,
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
      body: const SafeArea(
        child: Padding(
          padding: EdgeInsets.all(15.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            spacing: 10.0,
            children: [
              FittedBox(
                child: Text(
                  'OTP Verification',
                  style: TextStyle(fontSize: 25.0, fontWeight: FontWeight.bold),
                ),
              ),
              Text(
                'Enter your mobile number or email to receive a verification code',
                textAlign: TextAlign.center,
              ),
              RegisterOtpTextFieldWidget(),
              VerifyOtpButtonWidget(),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Clear all otp verification inputs.
    _authControllers.registerOTP.clear();
    _authControllers.registerOTPControllers.map((item) => item.clear());
    super.dispose();
  }
}
