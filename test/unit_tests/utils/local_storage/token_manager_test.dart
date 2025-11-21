import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/utils/local_storage/token_manager.dart';
import 'package:test/test.dart';

import '../../../helpers/test_mocks.dart';

void main() {
  late TokenManager tokenManager;
  late FlutterSecureStorage secureStorage;

  setUpAll(() {
    tokenManager = TokenManager();
    GetIt.I.registerLazySingleton(() => PlatformServices());

    /// Initialize the [FlutterSecureStorage] on the [PlatformServices] with
    /// the mock version.
    GetIt.I<PlatformServices>().secureStorage = MockFlutterSecureStorage();
    secureStorage = GetIt.I<PlatformServices>().secureStorage;
  });

  group('Token manager test', () {
    test('Should set access and refresh token', () async {
      // Mock secure storage to return access and refresh token.
      when(
        () => secureStorage.read(key: 'access_token'),
      ).thenAnswer((_) async => 'token_abc');

      when(
        () => secureStorage.read(key: 'refresh_token'),
      ).thenAnswer((_) async => 'token_def');

      await tokenManager.getUserTokens();

      expect(tokenManager.accessToken, 'token_abc');
      expect(tokenManager.refreshToken, 'token_def');
    });

    test('Should throw exception on access_token', () async {
      // Mock secure storage to return access and refresh token.
      when(
        () => secureStorage.read(key: 'access_token'),
      ).thenThrow('Exception');

      when(
        () => secureStorage.read(key: 'refresh_token'),
      ).thenAnswer((_) async => 'token_def');

      await tokenManager.getUserTokens();

      expect(tokenManager.accessToken, '');
      expect(tokenManager.refreshToken, 'token_def');
    });
  });
}
