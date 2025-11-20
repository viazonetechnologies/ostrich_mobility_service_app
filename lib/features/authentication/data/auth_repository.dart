import 'package:ostrich_service/features/authentication/domain/auth_interface.dart';

class AuthRepository implements AuthInterface {
  @override
  Future<String> loginUser(String identifier, String password) async {
    // TODO: implement loginUser
    throw UnimplementedError();
  }

  @override
  Future<String> logoutUser() async {
    // TODO: implement logoutUser
    throw UnimplementedError();
  }
}
