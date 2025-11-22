import 'package:flutter/material.dart';
import 'package:ostrich_service/core/globals/app_global_keys.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/create_account_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/open_privacy_policy_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/buttons/open_terms_of_service_button_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/check_boxes/terms_and_conditions_agree_check_box_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_email_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_full_name_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_password_confirm_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_password_text_field_widget.dart';
import 'package:ostrich_service/features/authentication/presentation/widgets/text_fields/register_phone_number_text_field_widget.dart';

class RegisterFormWidget extends StatelessWidget {
  const RegisterFormWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Form(
      key: registerFormGlobalKey,
      child: const SingleChildScrollView(
        child: Column(
          spacing: 10.0,
          children: [
            RegisterFullNameTextFieldWidget(),
            RegisterEmailTextFieldWidget(),
            RegisterPhoneNumberTextFieldWidget(),
            RegisterPasswordTextFieldWidget(),
            RegisterPasswordConfirmTextFieldWidget(),
            Row(
              spacing: 5.0,
              children: [
                TermsAndConditionsAgreeCheckBoxWidget(),
                Flexible(
                  child: Wrap(
                    crossAxisAlignment: WrapCrossAlignment.center,
                    spacing: 5.0,
                    children: [
                      Text('I agree to the'),
                      OpenTermsOfServiceButtonWidget(),
                      Text('and'),
                      OpenPrivacyPolicyButtonWidget(),
                    ],
                  ),
                ),
              ],
            ),
            CreateAccountButtonWidget(),
          ],
        ),
      ),
    );
  }
}
