import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/http_client.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/core/services/service_locator.dart';
import 'package:ostrich_service/routes/app_router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
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
    return AnnotatedRegion(
      value: SystemUiOverlayStyle(
        systemNavigationBarColor: Colors.white.withValues(alpha: 0.002),
        systemNavigationBarIconBrightness: Brightness.dark,
      ),
      child: MaterialApp.router(routerConfig: router),
    );
  }
}
