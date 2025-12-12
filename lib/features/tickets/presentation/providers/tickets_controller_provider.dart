import 'package:flutter/material.dart';

class TicketsControllerProvider with ChangeNotifier {
  TextEditingController updateStatusController = TextEditingController();
  String get updateStatus => updateStatusController.value.text;

  @override
  void dispose() {
    updateStatusController.dispose();
    super.dispose();
  }
}
