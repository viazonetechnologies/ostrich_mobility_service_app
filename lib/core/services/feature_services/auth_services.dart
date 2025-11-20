import 'package:get_it/get_it.dart';
import 'package:ostrich_service/features/authentication/state_helpers/auth_controllers.dart';

void authServices() {
  // Controllers
  GetIt.I.registerLazySingleton(() => AuthControllers());
}
