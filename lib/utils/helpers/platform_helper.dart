import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class PlatformHelper {
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
