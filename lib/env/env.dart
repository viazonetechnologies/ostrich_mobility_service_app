import 'package:envied/envied.dart';

/// class to access Environment variables.
///
/// By default it looks for variables in **.env** file on **root directory**.
///
/// To change this functionality, update the path on @{path} property provided
/// by the @[Envied] decorator.
///
/// For more info visit https://pub.dev/packages/envied.
@Envied()
class Env {}
