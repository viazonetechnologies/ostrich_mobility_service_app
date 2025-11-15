import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/platform_services.dart';
import 'package:ostrich_service/utils/local_storage/local_storage_services.dart';

/// Implementation of [LocalStorageServices] that uses SecureStorage mechanism.
///
/// On [Android] it uses **Keystore**. for more info visit https://developer.android.com/privacy-and-security/keystore
///
/// on [iOS] it uses **KeyChain**. For more info visit https://developer.apple.com/documentation/security/keychain-services#//apple_ref/doc/uid/TP30000897-CH203-TP1
class SecureStorageServices implements LocalStorageServices {
  @override
  Future<String?> getItem(String key) async {
    return await GetIt.I<PlatformServices>().secureStorage.read(key: key);
  }

  @override
  Future<void> setItem(String key, String value) async {
    await GetIt.I<PlatformServices>().secureStorage.write(
      key: key,
      value: value,
    );
  }
}
