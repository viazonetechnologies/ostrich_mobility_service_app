import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/configs/app_theme.dart';
import 'package:ostrich_service/core/constants/app_colors.dart';
import 'package:ostrich_service/core/services/http_client.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/core/services/service_locator.dart';
import 'package:ostrich_service/routes/app_router.dart';
import 'package:ostrich_service/utils/helpers/network_helper/http_client_helper.dart';
import 'package:ostrich_service/utils/helpers/network_helper/network_helper/network_helper.dart';
import 'package:ostrich_service/utils/helpers/platform_helper.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  /// Register services.
  serviceLocator();

  /// Initializing HTTP client.
  GetIt.I<HttpClient>().httpClient = HttpClientHelper.httpClient();

  /// Initializing all platform services here.
  final platformServices = GetIt.I<PlatformServices>();
  platformServices.secureStorage = PlatformHelper.secureStorage();
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);

  /// Run the app.
  runApp(const OstrichServiceWidget());
}

class OstrichServiceWidget extends StatefulWidget {
  const OstrichServiceWidget({super.key});

  @override
  State<OstrichServiceWidget> createState() => _OstrichServiceWidgetState();
}

class _OstrichServiceWidgetState extends State<OstrichServiceWidget> {
  /// Helps to listens on network status and other network related operations.
  late NetworkHelper _networkHelper;

  @override
  void initState() {
    super.initState();
    _networkHelper = GetIt.I<NetworkHelper>(instanceName: 'native');
    // Start listening on the network connection status.
    _networkHelper.startListenNetworkConnectionStatus();
  }

  @override
  Widget build(BuildContext context) {
    return AnnotatedRegion(
      value: SystemUiOverlayStyle(
        systemNavigationBarColor: Colors.white.withValues(alpha: 0.002),
        systemNavigationBarIconBrightness: Brightness.dark,
      ),
      child: MaterialApp.router(
        routerConfig: router,
        theme: ThemeData(
          appBarTheme: AppTheme.appBarTheme,
          bottomNavigationBarTheme: AppTheme.bottomNavigationBarTheme,
          bottomSheetTheme: AppTheme.bottomSheetTheme,
          colorScheme: AppTheme.colorScheme,
          dialogTheme: AppTheme.dialogTheme,
          fontFamily: AppTheme.fontFamily,
          inputDecorationTheme: AppTheme.inputDecorationTheme,
          textSelectionTheme: const TextSelectionThemeData(
            cursorColor: AppColors.primaryColor,
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Dispose services.
    _networkHelper.stopListenNetworkConnectionStatus();
    super.dispose();
  }
}
