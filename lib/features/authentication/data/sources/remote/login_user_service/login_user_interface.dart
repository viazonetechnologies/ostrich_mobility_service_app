import 'package:fpdart/fpdart.dart';

abstract interface class LoginUserInterface {
  Future<Either<dynamic, String>> loginUser(String identifier, String password);
}
