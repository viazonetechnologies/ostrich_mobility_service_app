import 'package:flutter/material.dart';

class AuthControllers {
  TextEditingController loginUsername = TextEditingController();
  TextEditingController loginPassword = TextEditingController();
  TextEditingController registerEmail = TextEditingController();
  TextEditingController registerFullName = TextEditingController();
  TextEditingController registerMobile = TextEditingController();
  TextEditingController registerOTP = TextEditingController();
  TextEditingController registerPassword = TextEditingController();
  TextEditingController registerPasswordConfirm = TextEditingController();

  List<TextEditingController> registerOTPControllers = List.generate(
    5,
    (_) => TextEditingController(),
  );
  List<FocusNode> registerOTPFocusNodes = List.generate(5, (_) => FocusNode());
}
