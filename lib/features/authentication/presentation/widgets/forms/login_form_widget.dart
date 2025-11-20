import 'package:flutter/material.dart';
import 'package:ostrich_service/core/globals/app_global_keys.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/forgot_password_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/login_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_password_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/login_user_name_text_field_widget.dart';

class LoginFormWidget extends StatelessWidget {
  const LoginFormWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Form(
      key: loginFormGlobalKey,
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        spacing: 10.0,
        children: [
          LoginUserNameTextFieldWidget(),
          LoginPasswordTextFieldWidget(),
          ForgotPasswordButtonWidget(),
          LoginButtonWidget(),
        ],
      ),
    );
  }
}
