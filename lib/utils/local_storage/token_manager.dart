import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/services/platform_services.dart';

/// Manages user token related operations.
class TokenManager {
  /// User access token.
  String? _accessToken;
  String get accessToken => _accessToken!;

  /// User refresh token.
  ///
  /// Use this for renew the **access token**.
  String? _refreshToken;
  String get refreshToken => _refreshToken!;

  /// Method to get access and refresh tokens from device.
  Future<void> getUserTokens() async {
    await Future.wait([_getAccessToken(), _getRefreshToken()]);
  }

  Future<void> _getAccessToken() async {
    try {
      final accessToken = await GetIt.I<PlatformServices>().secureStorage.read(
        key: 'access_token',
      );
      _accessToken = accessToken.toString();
    } catch (_) {
      _accessToken = '';
    }
  }

  Future<void> _getRefreshToken() async {
    try {
      final refreshToken = await GetIt.I<PlatformServices>().secureStorage.read(
        key: 'refresh_token',
      );
      _refreshToken = refreshToken.toString();
    } catch (_) {
      _refreshToken = '';
    }
  }
}
