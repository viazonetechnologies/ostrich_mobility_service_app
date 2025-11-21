import 'package:envied/envied.dart';

part 'env.g.dart';

/// class to access Environment variables.
///
/// By default it looks for variables in **.env** file on **root directory**.
///
/// To change this functionality, update the path on @{path} property provided
/// by the @[Envied] decorator.
///
/// For more info visit https://pub.dev/packages/envied.
@Envied()
class Env {
  @EnviedField(obfuscate: true, varName: 'BASE_URL')
  static final String baseUrl = _Env.baseUrl;

  @EnviedField(varName: 'LOGIN')
  static const String login = _Env.login;

  @EnviedField(varName: 'LOGOUT')
  static const String logout = _Env.logout;
}
