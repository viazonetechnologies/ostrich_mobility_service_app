import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
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
        child: Column(
          children: [
            Text('OTP Verification'),
            Text(
              'Enter your mobile number or email to receive a verification code',
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Clear all otp verification inputs.
    _authControllers.registerOTP.clear();
    super.dispose();
  }
}
