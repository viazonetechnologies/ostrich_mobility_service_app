import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/go_to_sign_up_page_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/forms/login_form_widget.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

class LoginPageWidget extends StatefulWidget {
  const LoginPageWidget({super.key});

  @override
  State<LoginPageWidget> createState() => _LoginPageWidgetState();
}

class _LoginPageWidgetState extends State<LoginPageWidget> {
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
          AppStrings.ostrichMobility,
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(15.0),
          child: Center(
            child: SingleChildScrollView(
              child: Column(
                spacing: 10.0,
                children: [
                  const Text(
                    AppStrings.login,
                    style: TextStyle(
                      fontSize: 35.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  MultiBlocProvider(
                    providers: [
                      BlocProvider(create: (context) => ObscurePasswordCubit()),
                    ],
                    child: const LoginFormWidget(),
                  ),
                  const Divider(),
                  const Text(
                    AppStrings.dontHaveAnAccount,
                    style: TextStyle(color: Colors.grey),
                  ),
                  const GoToSignUpPageButtonWidget(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Clear all login input data
    _authControllers.loginUsername.clear();
    _authControllers.loginPassword.clear();
    super.dispose();
  }
}
