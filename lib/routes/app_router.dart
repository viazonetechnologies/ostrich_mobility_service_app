import 'package:go_router/go_router.dart';
import 'package:ostrich_service/pages/login_page_widget.dart';
import 'package:ostrich_service/pages/register_otp_verification_page_widget.dart';
import 'package:ostrich_service/pages/register_page_widget.dart';
import 'package:ostrich_service/routes/nav_routes.dart';

final _router = GoRouter(
  initialLocation: NavRoutes.loginPage,
  routes: [
    GoRoute(
      path: NavRoutes.loginPage,
      builder: (context, state) => const LoginPageWidget(),
    ),
    GoRoute(
      path: NavRoutes.registerPage,
      builder: (context, state) => const RegisterPageWidget(),
    ),
    GoRoute(
      path: NavRoutes.registerOtpPage,
      builder: (context, state) => const RegisterOtpVerificationPageWidget(),
    ),
  ],
);

GoRouter get router => _router;
