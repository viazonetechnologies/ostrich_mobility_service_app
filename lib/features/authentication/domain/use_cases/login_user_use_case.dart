import 'package:get_it/get_it.dart';
import 'package:ostrich_service/features/authentication/domain/auth_interface.dart';

class LoginUserUseCase {
  Future<String> login(String identifier, String password) async {
    return await GetIt.I<AuthInterface>().loginUser(identifier, password);
  }
}
