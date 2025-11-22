import 'package:flutter/material.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';

class AppTheme {
  static const appBarTheme = AppBarTheme(
    backgroundColor: AppColors.primaryColor,
    scrolledUnderElevation: 0.0,
  );

  static const bottomNavigationBarTheme = BottomNavigationBarThemeData(
    backgroundColor: Colors.white,
    elevation: 0.0,
  );

  static const bottomSheetTheme = BottomSheetThemeData(
    backgroundColor: Colors.white,
    showDragHandle: true,
  );

  static final colorScheme = ColorScheme.light(
    primary: AppColors.primaryColor,
    surface: AppColors.surfaceColor!,
  );

  static final dialogTheme = DialogThemeData(
    backgroundColor: Colors.white,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
  );

  static const fontFamily = 'Ubuntu';

  static final inputDecorationTheme = InputDecorationTheme(
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(10.0),
      borderSide: BorderSide(color: Colors.grey[300]!),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(10.0),
      borderSide: BorderSide(color: Colors.grey[300]!),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(10.0),
      borderSide: BorderSide(color: Colors.grey[300]!),
    ),
    fillColor: Colors.white,
    filled: true,
    hintStyle: const TextStyle(color: Colors.grey),
    suffixStyle: const TextStyle(color: Colors.grey),
  );
}
