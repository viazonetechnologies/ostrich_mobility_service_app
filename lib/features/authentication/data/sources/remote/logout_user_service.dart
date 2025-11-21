import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/http_client.dart';
import 'package:ostrich_service/env/env.dart';
import 'package:ostrich_service/utils/local_storage/token_manager.dart';

class LogoutUserService {
  Future<Either<dynamic, String>> logout() async {
    try {
      final httpClient = GetIt.I<HttpClient>().httpClient;
      final requestUrl = Env.logout;
      final token = GetIt.I<TokenManager>().accessToken;
      final requestHeaders = {'Authorization': 'Bearer $token'};
      final response = await httpClient.post(
        requestUrl,
        options: Options(headers: requestHeaders),
      );
      return Left(response.data);
    } catch (error) {
      return Right(error.toString());
    }
  }
}
