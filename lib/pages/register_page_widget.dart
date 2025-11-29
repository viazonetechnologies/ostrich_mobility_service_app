import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/obscure_password_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/terms_and_conditions_check_cubit.dart';
import 'package:ostrich_service/features/authentication/presentation/providers/authentication_controllers_provider.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/go_to_sign_in_page_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/forms/register_form_widget.dart';
import 'package:provider/provider.dart';

class RegisterPageWidget extends StatelessWidget {
  const RegisterPageWidget({super.key});

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
          child: SingleChildScrollView(
            child: Column(
              spacing: 10.0,
              children: [
                const FittedBox(
                  child: Text(
                    AppStrings.createAccount,
                    style: TextStyle(
                      fontSize: 25.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const Text(
                  AppStrings
                      .joinOstrichMobilityToAccessAllOurServicesAndSupport,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey),
                ),
                MultiProvider(
                  providers: [
                    BlocProvider(create: (context) => ObscurePasswordCubit()),
                    BlocProvider(
                      create: (context) => TermsAndConditionsCheckCubit(),
                    ),
                    ChangeNotifierProvider(
                      create: (context) => AuthenticationControllersProvider(),
                    ),
                  ],
                  child: const RegisterFormWidget(),
                ),
                const Divider(),
                const Text(AppStrings.alreadyHaveAnAccount),
                const GoToSignInPageButtonWidget(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
