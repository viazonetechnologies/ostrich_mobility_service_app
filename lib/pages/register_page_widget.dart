import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/go_to_sign_in_page_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/forms/register_form_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

class RegisterPageWidget extends StatefulWidget {
  const RegisterPageWidget({super.key});

  @override
  State<RegisterPageWidget> createState() => _RegisterPageWidgetState();
}

class _RegisterPageWidgetState extends State<RegisterPageWidget> {
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
          child: SingleChildScrollView(
            child: Column(
              spacing: 10.0,
              children: [
                FittedBox(
                  child: Text(
                    AppStrings.createAccount,
                    style: TextStyle(
                      fontSize: 25.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Text(
                  'Join Ostrich Mobility to access all our services and support',
                  style: TextStyle(color: Colors.grey),
                ),
                RegisterFormWidget(),
                Divider(),
                Text(AppStrings.alreadyHaveAnAccount),
                GoToSignInPageButtonWidget(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Clear all register input data
    _authControllers.registerEmail.clear();
    _authControllers.registerFullName.clear();
    _authControllers.registerMobile.clear();
    _authControllers.registerPassword.clear();
    _authControllers.registerPasswordConfirm.clear();
    super.dispose();
  }
}
