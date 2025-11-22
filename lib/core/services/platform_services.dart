import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Holds instances of all platform related services.
class PlatformServices {
  /// Returns the [EventChannel] for receiving event streams from the native platform.
  static const EventChannel _eventChannel = EventChannel(
    'ostrich_service/network_status',
  );
  EventChannel get eventChannel => _eventChannel;

  FlutterSecureStorage? _secureStorage;

  /// Returns instance of [FlutterSecureStorage].
  FlutterSecureStorage get secureStorage => _secureStorage!;
  set secureStorage(FlutterSecureStorage storage) => _secureStorage = storage;

  /// Returns the [MethodChannel] for communicating with native platform code.
  static const MethodChannel _methodChannel = MethodChannel('ostrich_service');
  MethodChannel get methodChannel => _methodChannel;
}
