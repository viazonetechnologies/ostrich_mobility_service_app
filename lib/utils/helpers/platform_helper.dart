import 'dart:io';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:url_launcher/url_launcher.dart';

class PlatformHelper {
  static void launchCallApp(String phone) {
    final phoneNumberUrl = "tel:$phone";
    final parsedUri = Uri.parse(phoneNumberUrl);
    launchUrl(parsedUri);
  }

  static void launchMaps(String latitude, String longitude) {
    if (Platform.isAndroid) {
      final googleMapsLocationUrl =
          "https://www.google.com/maps/search/?api=1&query=$latitude,$longitude";
      final parsedUri = Uri.parse(googleMapsLocationUrl);
      launchUrl(parsedUri);
    }
    return;
  }

  /// Returns an instance of [FlutterSecureStorage] with platform related
  /// configurations.
  ///
  static FlutterSecureStorage secureStorage() {
    return const FlutterSecureStorage(
      aOptions: AndroidOptions(encryptedSharedPreferences: true),
      iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
    );
  }
}
