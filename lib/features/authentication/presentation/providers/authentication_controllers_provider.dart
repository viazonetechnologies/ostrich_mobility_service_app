import 'package:flutter/material.dart';

class AuthenticationControllersProvider extends ChangeNotifier {
  TextEditingController loginUsernameController = TextEditingController();
  String get loginUserName => loginUsernameController.value.text;

  TextEditingController loginPasswordController = TextEditingController();
  String get loginPassword => loginPasswordController.value.text;

  TextEditingController registerEmailController = TextEditingController();
  String get registerEmail => registerEmailController.value.text;

  TextEditingController registerFullNameController = TextEditingController();
  String get registerFullname => registerFullNameController.value.text;

  TextEditingController registerMobileController = TextEditingController();
  String get registerMobile => registerMobileController.value.text;

  TextEditingController registerOTPController = TextEditingController();
  String get registerOTP => registerOTPController.value.text;

  TextEditingController registerPasswordController = TextEditingController();
  String get registerPassword => registerPasswordController.value.text;

  TextEditingController registerPasswordConfirmController =
      TextEditingController();
  String get registerPasswordConfirm =>
      registerPasswordConfirmController.value.text;

  List<TextEditingController> registerOTPControllers = List.generate(
    5,
    (_) => TextEditingController(),
  );
  List<FocusNode> registerOTPFocusNodes = List.generate(5, (_) => FocusNode());

  @override
  void dispose() {
    // dispose all controllers.
    loginPasswordController.dispose();
    loginUsernameController.dispose();
    registerEmailController.dispose();
    registerFullNameController.dispose();
    registerMobileController.dispose();
    registerOTPController.dispose();
    for (var item in registerOTPControllers) {
      item.dispose();
    }
    for (var item in registerOTPFocusNodes) {
      item.dispose();
    }
    registerPasswordController.dispose();
    registerPasswordConfirmController.dispose();
    super.dispose();
  }
}
