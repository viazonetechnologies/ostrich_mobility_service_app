import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/constants/app_icons.dart';
import 'package:ostrich_service/core/constants/app_strings.dart';
import 'package:ostrich_service/core/globals/app_global_keys.dart';
import 'package:ostrich_service/features/authentication/presentation/bloc/terms_and_conditions_check_cubit.dart';

class CreateAccountButtonWidget extends StatelessWidget {
  const CreateAccountButtonWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<TermsAndConditionsCheckCubit, bool>(
      builder: (context, isTermsAndConditionsChecked) {
        return MaterialButton(
          color: AppColors.primaryColor,
          disabledColor: Colors.grey,
          elevation: 0.0,
          minWidth: MediaQuery.of(context).size.width,
          padding: const EdgeInsets.all(15.0),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10.0),
          ),
          textColor: Colors.white,
          onPressed: isTermsAndConditionsChecked
              ? () {
                  // Validate the register form data using global FormState key.
                  bool isLoginFormValid = registerFormGlobalKey.currentState!
                      .validate();
                  if (!isLoginFormValid) {
                    // The form isn't valid can't proceed with further steps!..
                    return;
                  }

                  // Form validated successfully, register the user.
                }
              : null,
          child: const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            spacing: 5.0,
            children: [AppIcons.personAddIcon, Text(AppStrings.createAccount)],
          ),
        );
      },
    );
  }
}
