import 'dart:io';

import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/utils/local_storage/local_storage_services.dart';
import 'package:ostrich_service/utils/local_storage/secure_storage_services.dart';

void serviceLocator() {
  coreServices();
  utilsServices();
}

// Registers all app core services here.
void coreServices() {
  GetIt.I.registerLazySingleton(() => HttpClient());
  GetIt.I.registerLazySingleton(() => PlatformServices());
}

// Registers all utility services here.
void utilsServices() {
  GetIt.I.registerFactory<LocalStorageServices>(
    () => SecureStorageServices(),
    instanceName: 'secureStorage',
  );
}
