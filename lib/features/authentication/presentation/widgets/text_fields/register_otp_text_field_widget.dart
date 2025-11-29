import 'package:flutter/material.dart';
import 'package:ostrich_service/features/authentication/presentation/providers/authentication_controllers_provider.dart';
import 'package:provider/provider.dart';

class RegisterOtpTextFieldWidget extends StatefulWidget {
  const RegisterOtpTextFieldWidget({super.key});

  @override
  State<RegisterOtpTextFieldWidget> createState() =>
      _RegisterOtpTextFieldWidgetState();
}

class _RegisterOtpTextFieldWidgetState
    extends State<RegisterOtpTextFieldWidget> {
  late List<Flexible> _otpFields;

  @override
  void initState() {
    super.initState();
    final authController = Provider.of<AuthenticationControllersProvider>(
      context,
      listen: false,
    );
    final otpControllers = authController.registerOTPControllers;
    final otpFocusNodes = authController.registerOTPFocusNodes;
    _otpFields = List.generate(
      5,
      (index) => Flexible(
        child: TextField(
          controller: otpControllers[index],
          decoration: const InputDecoration(counterText: ''),
          focusNode: otpFocusNodes[index],
          key: Key('OTP Field $index'),
          keyboardType: TextInputType.number,
          maxLength: 1,
          textAlign: TextAlign.center,
          style: const TextStyle(fontWeight: FontWeight.bold),
          onChanged: (value) {
            // Move focus to the next OTP input
            if (index < otpFocusNodes.length - 1) {
              FocusScope.of(context).requestFocus(otpFocusNodes[index + 1]);
            }
          },
          onTapOutside: (_) => FocusManager.instance.primaryFocus?.unfocus(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Row(spacing: 5.0, children: _otpFields);
  }
}
