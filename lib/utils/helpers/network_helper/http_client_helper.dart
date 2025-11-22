import 'package:dio/dio.dart';
import 'package:ostrich_service/env/env.dart';

class HttpClientHelper {
  /// Return an instance of **Dio**.
  ///
  /// for more info https://pub.dev/packages/dio
  ///
  /// [duration] is by default **15 seconds**.
  /// The duration must be in milliseconds.
  ///
  static Dio httpClient({int? duration}) {
    final defaultDuration = Duration(milliseconds: duration ?? 15000);
    return Dio(
      BaseOptions(
        baseUrl: Env.baseUrl,
        connectTimeout: defaultDuration,
        receiveTimeout: defaultDuration,
        sendTimeout: defaultDuration,
      ),
    );
  }
}
