import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/http_client.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/core/services/service_locator.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  serviceLocator();

  /// Initializing HTTP client.
  GetIt.I<HttpClient>().httpClient = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      sendTimeout: const Duration(seconds: 15),
    ),
  );

  /// Initializing all platform services here.
  final platformServices = GetIt.I<PlatformServices>();
  platformServices.secureStorage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  /// Run the app.
  runApp(const OstrichServiceWidget());
}

class OstrichServiceWidget extends StatefulWidget {
  const OstrichServiceWidget({super.key});

  @override
  State<OstrichServiceWidget> createState() => _OstrichServiceWidgetState();
}

class _OstrichServiceWidgetState extends State<OstrichServiceWidget> {
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router();
  }
}
