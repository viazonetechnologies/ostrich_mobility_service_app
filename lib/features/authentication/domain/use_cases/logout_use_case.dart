import 'package:get_it/get_it.dart';
import 'package:ostrich_service/features/authentication/domain/auth_interface.dart';

class LogoutUseCase {
  Future<String> logout() async {
    return await GetIt.I<AuthInterface>().logoutUser();
  }
}
