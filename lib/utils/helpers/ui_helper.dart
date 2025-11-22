import 'package:flutter/material.dart';
import 'package:ostrich_service/core/globals/app_global_keys.dart';

class UiHelper {
  /// Shows **SnackBar**.
  ///
  /// [message] Message to show on the SnackBar.
  /// [duration] SnackBar duration. By default 1 second.
  /// [onClosed] Callback function to execute after SnackBar closed.
  static void showSnackBar({
    required String message,
    Duration? duration = const Duration(seconds: 1),
    VoidCallback? onClosed,
  }) {
    // Access scaffold state using global registered scaffold messenger key.
    final scaffoldState = scaffoldMessengerKey.currentState;
    final snackBar = SnackBar(content: Text(message));
    final controller = scaffoldState?.showSnackBar(snackBar);
    controller?.closed.then((_) {
      if (onClosed != null) onClosed();
    });
  }
}
