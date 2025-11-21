import 'package:fpdart/fpdart.dart';

abstract interface class LoginUserInterface {
  Future<Either<dynamic, String>> login(String identifier, String password);
}
