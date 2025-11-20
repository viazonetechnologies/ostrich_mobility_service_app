import 'package:fpdart/fpdart.dart';
import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/http_client.dart';
import 'package:ostrich_service/features/authentication/data/sources/remote/login_user_service/login_user_interface.dart';

/// Implementation of [LoginUserInterface] using **username**, and **password**.
///
/// User can pass the username and password for login.
class LoginUserWithUserNameService implements LoginUserInterface {
  @override
  Future<Either<dynamic, String>> loginUser(
    String identifier,
    String password,
  ) async {
    try {
      final httpClient = GetIt.I<HttpClient>().httpClient;
      final requestUrl = '';
      final requestBody = {'user_name': identifier, 'password': password};
      final response = await httpClient.post(requestUrl, data: requestBody);
      return Left(response.data);
    } catch (error) {
      return Right(error.toString());
    }
  }
}
