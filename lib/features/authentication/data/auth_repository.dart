import 'package:get_it/get_it.dart';
import 'package:ostrich_service/core/constants/error_constants.dart';
import 'package:ostrich_service/core/constants/local_storage_key.dart';
import 'package:ostrich_service/core/models/response_model.dart';
import 'package:ostrich_service/features/authentication/data/sources/remote/login_user_service/login_user_interface.dart';
import 'package:ostrich_service/features/authentication/data/sources/remote/logout_user_service.dart';
import 'package:ostrich_service/features/authentication/domain/auth_interface.dart';
import 'package:ostrich_service/utils/local_storage/local_storage_interface.dart';

class AuthRepository implements AuthInterface {
  @override
  Future<String> loginUser(String identifier, String password) async {
    final result = await GetIt.I<LoginUserInterface>(
      instanceName: 'user_name',
    ).login(identifier, password);

    return result.fold(
      (response) {
        try {
          final responseType = ResponseModel.fromJson(response);
          if (responseType.success!) {
            /// User logged in successfully.
            ///
            /// Save login state, and tokens on local storage.
            final localStorage = GetIt.I<LocalStorageInterface>(
              instanceName: 'secure_storage',
            );
            final accessToken = responseType.data['access_token'];
            final refreshToken = responseType.data['refresh_token'];
            Future.wait([
              localStorage.setItem(LocalStorageKey.loginState, '1'),
              localStorage.setItem(LocalStorageKey.accessToken, accessToken),
              localStorage.setItem(LocalStorageKey.refreshToken, refreshToken),
            ]);
          }

          return responseType.message!;
        } catch (_) {
          // Response model error!.
          return ErrorConstants.jsonModelError;
        }
      },
      (error) {
        return error;
      },
    );
  }

  @override
  Future<String> logoutUser() async {
    final result = await GetIt.I<LogoutUserService>().logout();

    return result.fold(
      (response) {
        try {
          final responseType = ResponseModel.fromJson(response);
          if (responseType.success!) {
            /// User logged out successfully.
            ///
            /// Update login state.
            final localStorage = GetIt.I<LocalStorageInterface>(
              instanceName: 'secure_storage',
            );
            localStorage.setItem(LocalStorageKey.loginState, '0');
          }

          return responseType.message!;
        } catch (_) {
          // Response model error!.
          return ErrorConstants.jsonModelError;
        }
      },
      (error) {
        return error;
      },
    );
  }
}
