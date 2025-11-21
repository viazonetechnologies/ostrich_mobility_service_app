import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/utils/local_storage/secure_storage_services.dart';
import 'package:test/test.dart';

import '../../../helpers/test_mocks.dart';

void main() {
  late FlutterSecureStorage secureStorage;
  late SecureStorageServices secureStorageServices;
  setUpAll(() {
    secureStorageServices = SecureStorageServices();
    GetIt.I.registerLazySingleton(() => PlatformServices());

    /// Initialize the [FlutterSecureStorage] on the [PlatformServices] with
    /// the mock version.
    GetIt.I<PlatformServices>().secureStorage = MockFlutterSecureStorage();
    secureStorage = GetIt.I<PlatformServices>().secureStorage;

    // Mock the implementation of write method in the [FlutterSecureStorage].
    when(
      () => secureStorage.write(key: 'key', value: 'value'),
    ).thenAnswer((_) async {});
  });

  group('Secure storage services test', () {
    test('Should save the item on secure storage', () async {
      await secureStorageServices.setItem('key', 'value');
    });

    test('Should return value of a key', () async {
      // Mock the implementation of read method in the [FlutterSecureStorage].
      when(() => secureStorage.read(key: 'key')).thenAnswer((_) async => 'abc');

      final result = await secureStorageServices.getItem('key');
      expect(result, 'abc');
    });
  });
}
