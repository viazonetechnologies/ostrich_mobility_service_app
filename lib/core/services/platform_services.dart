import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Holds instances of all platform related services.
class PlatformServices {
  FlutterSecureStorage? _secureStorage;

  /// Instance of [FlutterSecureStorage].
  FlutterSecureStorage get secureStorage => _secureStorage!;
  set secureStorage(FlutterSecureStorage storage) => _secureStorage = storage;
}
