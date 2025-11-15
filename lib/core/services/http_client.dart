import 'package:dio/dio.dart';

class HttpClient {
  Dio? _dio;

  /// HTTP client support, an instance of [Dio]
  Dio get httpClient => _dio!;
  set httpClient(Dio dio) => _dio = dio;
}
