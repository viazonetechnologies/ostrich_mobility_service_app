import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/feature_services/auth_services.dart';
import 'package:ostrich_service/core/services/http_client.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/utils/local_storage/local_storage_interface.dart';
import 'package:ostrich_service/utils/local_storage/secure_storage_services.dart';

void serviceLocator() {
  coreServices();
  utilsServices();
  featureServices();
}

// Registers all feature related services here.
void featureServices() {
  authServices();
}

// Registers all app core services here.
void coreServices() {
  GetIt.I.registerLazySingleton(() => HttpClient());
  GetIt.I.registerLazySingleton(() => PlatformServices());
}

// Registers all utility services here.
void utilsServices() {
  GetIt.I.registerFactory<LocalStorageInterface>(
    () => SecureStorageServices(),
    instanceName: 'secureStorage',
  );
}
